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
has_error = False


def check_space(url):
    """
    Check a space URL. Return `true` if it's OK, or `false` if it should be
    removed from the directory.
    """
    # Fetch response
    try:
        response = requests.get(url, verify=False, timeout=TIMEOUT_SECONDS)
    except requests.exceptions.ConnectTimeout:
        print('  \033[0;31m-> Connection timeout (%ds)\033[0m' % TIMEOUT_SECONDS)
        return False
    except requests.exceptions.ReadTimeout:
        print('  \033[0;31m-> Read timeout (%ds)\033[0m' % TIMEOUT_SECONDS)
        return False
    except requests.exceptions.ConnectionError:
        print('  \033[0;31m-> Connection error\033[0m')
        return False
    except Exception as e:
        print('  \033[0;31m-> Error: %s\033[0m' % e)
        global has_error
        has_error = True
        return False

    # Verify status code
    if response.status_code != 200:
        print('  \033[0;31m-> Status: %s: %s\033[0m' % (response.status_code, response.reason))
        return False

    # Verify JSON format
    try:
        response.json()
    except json.decoder.JSONDecodeError:
        print('  \033[0;31m-> Invalid JSON\033[0m')
        return False

    return True


# Check spaces
with open(DIRECTORY_FILE, 'r') as directory:
    spaces = json.loads(directory.read())
    for name, url in spaces.items():
        print('+ %s %s' % (name, url))
        space_valid = check_space(url)
        if space_valid is True:
            spaces_new[name] = url


# Save new spaces
with open(DIRECTORY_FILE, 'w+') as directory:
    json_str = json.dumps(spaces_new, indent=2, sort_keys=True, separators=(',', ':'))
    directory.write(json_str)


exit(1 if has_error else 0)
