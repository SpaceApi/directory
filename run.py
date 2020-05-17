# Get countries from SpaceAPI directory, and recombine into new JSON
# Python 3.6.1
# Runtime 3 minutes

import json
from urllib.request import urlopen
#from io import open

INPUT_PATH = './directory.json'
OUTPUT_PATH = './directory-country.json'

INPUT_URL_DIRECTORY = 'https://directory.spaceapi.io'

#with open(INPUT_PATH, 'rb') as f:
#  data = json.load(f)

spaceJSONfile = urlopen(INPUT_URL_DIRECTORY)
spaceJSON = json.load(spaceJSONfile)

spaceCountryList = []
count = 0
for (k, v) in spaceJSON.items():
	spaceCountryItem = dict()
	spaceCountryItem["id"] = count
	spaceCountryItem["name"] = k
	spaceCountryItem["url"] = v
	spaceCountryItem["country"] = ""
	# See https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
	spaceCountryItem["iso-3166-1-alpha-2"] = ""
	spaceCountryItem["lat"] = ""
	spaceCountryItem["lon"] = ""
	spaceCountryItem["address"] = ""
	spaceCountryList.append(spaceCountryItem)
	count = count + 1

for space in spaceCountryList:
	try:
		spaceIdentityJSONfile = urlopen( space["url"] )
		spaceIdentityJSON = json.load(spaceIdentityJSONfile)
		spaceCountryList[ space["id"] ]["address"] = spaceIdentityJSON["location"]["address"]
		spaceCountryList[ space["id"] ]["lat"] = spaceIdentityJSON["location"]["lat"]
		spaceCountryList[ space["id"] ]["lon"] = spaceIdentityJSON["location"]["lon"]
	except:
		spaceCountryList[ space["id"] ]["address"] = ""

#Germany is 50% of the list, set Germany
for space in spaceCountryList:
	if ("Germany" in space["address"]):
		space["country"] = "Germany"
		space["iso-3166-1-alpha-2"] = "DE"
	elif (".de" in space["url"]):
		space["country"] = "Germany"
		space["iso-3166-1-alpha-2"] = "DE"
		
with open(OUTPUT_PATH, 'w') as fw:
	json.dump(spaceCountryList, fw, indent="\t")

print("Objects Processed:")
print(count)

#print(spaceCountryList)