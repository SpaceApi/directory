#!/usr/bin/env python3
"""Manage directory.json: keep it alphabetically sorted and add new entries.

Usage:
    manage_directory.py [sort]        Sort directory.json in place (default).
    manage_directory.py add           Interactively add an entry (name + URL),
                                       validated against the SpaceAPI validator.
    manage_directory.py add -n NAME -u URL   Non-interactive add.

The on-disk format matches the CI ``sort`` job (``jq -S``): two-space indent,
literal UTF-8, keys sorted by Unicode code point, and a trailing newline.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

PATH = Path(__file__).resolve().parent / "directory.json"
VALIDATOR = "https://validator.spaceapi.io/v2/validateURL"

# Connectivity requirements the directory depends on: a consumer fetches every
# URL cross-origin over HTTPS. Each entry is (validator_key, problem_message).
CONNECTIVITY_CHECKS = (
    ("reachable", "endpoint is not reachable"),
    ("isHttps", "endpoint is not served over HTTPS"),
    ("certValid", "TLS certificate is invalid"),
    ("cors", "CORS headers are missing (cross-origin fetch would fail)"),
    ("contentType", "Content-Type is not application/json"),
)


def load():
    return json.loads(PATH.read_text(encoding="utf-8"))


def save(data):
    """Write ``data`` sorted and formatted exactly like ``jq -S`` (CI canonical).

    The write is atomic: content goes to a temp file in the same directory and is
    renamed into place, so an interruption never truncates directory.json.
    """
    ordered = dict(sorted(data.items()))
    text = json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"
    fd, tmp = tempfile.mkstemp(dir=PATH.parent, prefix=".directory.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        # Preserve the original file's permissions (mkstemp creates 0600).
        if PATH.exists():
            shutil.copymode(PATH, tmp)
        else:
            os.chmod(tmp, 0o644)
        os.replace(tmp, PATH)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return ordered


def normalize_url(url):
    """Canonical form for duplicate detection.

    Lower-cases the scheme and host and drops a trailing slash so that
    ``https://example.org/`` and ``https://example.org`` count as the same
    endpoint. The path case is preserved because paths are case-sensitive.
    """
    parts = urlsplit(url.strip())
    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path.rstrip("/"),
            parts.query,
            parts.fragment,
        )
    )


def validate(url):
    """Validate ``url`` with the SpaceAPI validator (server-side fetch).

    Checks both schema validity and the connectivity requirements the directory
    depends on (reachable, HTTPS, valid cert, CORS, JSON content type). Returns
    (ok: bool, message: str) where message lists every problem found.
    """
    payload = json.dumps({"url": url}).encode("utf-8")
    req = urllib.request.Request(
        VALIDATOR, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace").strip()
        return False, f"validator HTTP {exc.code}: {body[:300] or exc.reason}"
    except Exception as exc:  # network / JSON errors are validation failures too
        return False, f"could not reach validator: {exc}"

    if not isinstance(result, dict):
        return False, "unexpected validator response (not a JSON object)"

    problems = []
    if not result.get("valid"):
        detail = (result.get("message") or "").strip()
        if not detail:
            parts = []
            for err in result.get("schemaErrors") or []:
                if isinstance(err, dict):
                    field = err.get("field", "?")
                    message = err.get("message", "?")
                    parts.append(f"{field}: {message}")
                else:
                    parts.append(str(err))
            detail = "; ".join(parts)
        problems.append("schema: " + (detail or "does not match the SpaceAPI schema"))
    # Fail closed: a connectivity key the validator did not return (or returned
    # false) counts as a failure, consistent with the schema check above.
    for key, description in CONNECTIVITY_CHECKS:
        if not result.get(key):
            problems.append(description)

    return not problems, "\n".join(f"  - {p}" for p in problems)


def cmd_sort():
    ordered = save(load())
    print(f"Sorted: {len(ordered)} entries")


def ask(value, prompt_text, field):
    """Return a non-empty stripped value, prompting only when ``value`` is None.

    An explicitly empty argument (e.g. ``-n ''``) or empty interactive input is
    a clean error, and EOF on a non-interactive stdin exits instead of raising.
    """
    if value is None:
        try:
            value = input(prompt_text)
        except EOFError:
            sys.exit(f"{field} is required.")
    value = value.strip()
    if not value:
        sys.exit(f"{field} is required.")
    return value


def cmd_add(name, url):
    name = ask(name, "Name to add: ", "Name")

    data = load()
    if name in data:
        sys.exit(f"'{name}' already exists in directory.json")

    url = ask(url, "SpaceAPI URL: ", "URL")

    target = normalize_url(url)
    existing = next((n for n, u in data.items() if normalize_url(u) == target), None)
    if existing:
        sys.exit(f"URL already used by '{existing}' in directory.json")

    prompt = "Add anyway, validate again, or abort? [y/v/A]: "
    while True:
        print(f"Validating {url} ...")
        ok, message = validate(url)
        if ok:
            print("Validation OK")
            break
        print(f"Validation FAILED:\n{message or '  - unknown error'}")
        try:
            choice = input(prompt).strip().lower()
        except EOFError:
            sys.exit("Aborted: validation failed and stdin is not interactive.")
        if choice in ("v", "validate"):
            continue
        if choice in ("y", "yes"):
            break
        sys.exit("Aborted, nothing changed.")

    data[name] = url
    ordered = save(data)
    position = list(ordered).index(name) + 1
    print(f"Added '{name}' at position {position} of {len(ordered)}")


def main():
    parser = argparse.ArgumentParser(description="Manage directory.json")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("sort", help="sort directory.json in place (default)")
    p_add = sub.add_parser("add", help="add an entry, validated against SpaceAPI")
    p_add.add_argument("-n", "--name", help="entry name (prompted if omitted)")
    p_add.add_argument("-u", "--url", help="SpaceAPI URL (prompted if omitted)")

    args = parser.parse_args()
    if args.command == "add":
        cmd_add(args.name, args.url)
    else:
        cmd_sort()


if __name__ == "__main__":
    main()
