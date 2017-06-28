#!/usr/bin/env python
"""
A simple script to remove unresponsive SpaceAPI endpoints from the directory and update urls.

An entry is removed in the following cases:

- There are more than 3 redirects
- Endpoint does not return HTTP 200

An url will be updated

- if there is a permanent redirect to a working SpaceAPI

"""
from __future__ import print_function, division, absolute_import, unicode_literals

import requests
import json

# Config
DIRECTORY_FILE = './directory.json'
TIMEOUT_SECONDS = 10
MAX_REDIRECTS = 3

# Variables
spaces_new = {}
removed = []
updated = []
has_error = False


def check_space(url, allowed_redirects=MAX_REDIRECTS):
    """
    Check a space URL. Return `true` if it's OK, or `false` if it should be
    removed from the directory. Additionally, the reason will be returned.
    """
    # Fetch response
    try:
        response = requests.get(url, verify=False, timeout=TIMEOUT_SECONDS, allow_redirects=False)
        if response.is_redirect:
            if 'location' not in response.headers:
                return False, 'Missing new location for redirect'
            else:
                print('  redirecting to', response.headers['location'])
                if allowed_redirects == 0:
                    return False, 'Too many redirects'
                redirected_space_valid, redirect_reason = check_space(
                    response.headers['location'],
                    allowed_redirects=allowed_redirects - 1
                )
                if redirected_space_valid:
                    if response.is_permanent_redirect:
                        if not redirect_reason:
                            # after redirecting the request succeeded:
                            # we use the new url
                            return True, response.headers['location']
                        else:
                            # after redirecting permanent there was still a
                            # valid reason to update the url:
                            # we use the updated url from there
                            return True, redirect_reason
                    else:
                        # no permanent redirect: no url update
                        return True, None
                else:
                    # there was no valid SpaceAPI after following the redirect
                    return redirected_space_valid, redirect_reason
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
    except ValueError:
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
            if not reason:
                spaces_new[name] = url
            else:
                print('  \033[0;33m-> new location: %s\033[0m' % reason)
                spaces_new[name] = reason  # new location
                updated.append((name, url, reason))
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

print('\nUpdated %d spaces.\n' % len(updated))
for name, old, new in updated:
    print('- %s: from %s to %s' % (name, old, new))

exit(1 if has_error else 0)
