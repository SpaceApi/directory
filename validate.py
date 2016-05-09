#!/usr/bin/env python2

import requests
import json
import collections

# Get spaces list
directory_file = './directory.json'
directory = open(directory_file, 'r')
spaces = json.loads(directory.read())
spaces_new = {}

# Check spaces
for key in spaces:
    url = spaces[key]
    try:
        print '%s %s' % (key, url)
        req = requests.get(url, verify=False, timeout=10)
        if req.status_code == 200:
            spaces_new[key] = url
        else:
            print '\t\033[0;31m\\_ Status: %s: %s\033[0m' \
                % (req.status_code, req.reason)
    except Exception,e:
        print '\t\033[0;31m\\_Error: %s\033[0m' % (e)

directory.close()

# Save new spaces
directory = open(directory_file, 'w+')
json_str = json.dumps(spaces_new, indent=2, sort_keys=True)
json_str = json_str.replace('/', '\\/')
json_str = json_str.replace(', ', ',')
json_str = json_str.replace(': ', ':')
directory.write(json_str)
directory.close()

