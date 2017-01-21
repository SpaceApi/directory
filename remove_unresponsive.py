#!/usr/bin/env python
"""
A simple script to remove unresponsive SpaceAPI endpoints from the directory.

An entry is removed in the following cases:

- Endpoint does not return HTTP 200

"""
from __future__ import print_function, division, absolute_import, unicode_literals

import requests
import json

# Get spaces list
directory_file = './directory.json'
directory = open(directory_file, 'r')
spaces = json.loads(directory.read())
spaces_new = {}
has_error = False


def check_space(url):
    """
    Check a space URL. Return `true` if it's OK, or `false` if it should be
    removed.
    """
    try:
        response = requests.get(url, verify=False, timeout=10)
    except Exception as e:
        print('  \033[0;31m-> Error: {}\033[0m'.format(e).encode('utf8'))
        global has_error
        has_error = True
        return False
    if response.status_code == 200:
        return True
    else:
        print('  \033[0;31m-> Status: %s: %s\033[0m'
                .format(response.status_code, response.reason)
                .encode('utf8'))
        return False


# Check spaces
for name, url in spaces.items():
    if 'spaceapi.net' in url:
        continue
    print('+ {} {}'.format(name, url).encode('utf8'))
    space_valid = check_space(url)
    if space_valid is True:
        spaces_new[name] = url


directory.close()

# Save new spaces
directory = open(directory_file, 'w+')
json_str = json.dumps(spaces_new, indent=2, sort_keys=True, separators=(',', ':'))
directory.write(json_str)
directory.close()
exit(int(has_error))
