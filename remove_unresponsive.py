#!/usr/bin/env python
"""
A simple script to remove unresponsive SpaceAPI endpoints from the directory.

An entry is removed in the following cases:

- Endpoint does not return HTTP 200

"""
from __future__ import print_function, division, absolute_import, unicode_literals

import requests
import json

# Config
DIRECTORY_FILE = './directory.json'
TIMEOUT_SECONDS = 10

# Variables
spaces_new = {}
removed = []
has_error = False


def check_space(url):
    """
    Check a space URL. Return `true` if it's OK, or `false` if it should be
    removed from the directory. Additionally, the reason will be returned.
    """
    # Fetch response
    try:
        response = requests.get(url, verify=False, timeout=TIMEOUT_SECONDS)
    except requests.exceptions.ConnectTimeout:
        return False, 'Connection timeout (%ds)' % TIMEOUT_SECONDS
    except requests.exceptions.ReadTimeout:
        return False, 'Read timeout (%ds)' % TIMEOUT_SECONDS
    except requests.exceptions.ConnectionError:
        return False, 'Connection error'
    except Exception as e:
        global has_error
        has_error = True
        return False, 'Error: %s' % e

    # Verify status code
    if response.status_code != 200:
        return False, 'Status: HTTP %s (%s)' % (response.status_code, response.reason)

    # Verify JSON format
    try:
        data = response.json()
    except json.decoder.JSONDecodeError:
        return False, 'Invalid JSON'

    # Verify that data at least looks like a valid SpaceAPI response
    if 'api' not in data:
        return False, 'Invalid SpaceAPI response: "api" key missing'
    if 'space' not in data:
        return False, 'Invalid SpaceAPI response: "space" key missing'

    return True, None


# Check spaces
with open(DIRECTORY_FILE, 'r') as directory:
    spaces = json.loads(directory.read())
    for name, url in spaces.items():
        print('+ %s %s' % (name, url))
        space_valid, reason = check_space(url)
        if space_valid is True:
            spaces_new[name] = url
        else:
            print('  \033[0;31m-> %s\033[0m' % reason)
            removed.append((name, reason))


# Save new spaces
with open(DIRECTORY_FILE, 'w+') as directory:
    json_str = json.dumps(spaces_new, indent=2, sort_keys=True, separators=(',', ':'))
    directory.write(json_str)


# Print summary
print('\nRemoved %d spaces from the directory.\n' % len(removed))
for name, reason in removed:
    print('- %s (%s)' % (name, reason))

exit(1 if has_error else 0)
