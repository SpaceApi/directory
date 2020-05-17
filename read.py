# Get statistics from new SpaceAPI directory, output them to file
# Python 3.6.1


import json
from urllib.request import urlopen
#from io import open

INPUT_PATH = './directory-country-manual.json'
OUTPUT_PATH = './worldwide-overview.txt'

INPUT_URL_DIRECTORY = 'https://directory.spaceapi.io'

with open(INPUT_PATH, 'rb') as f:
  spaceCountryList = json.load(f)

#spaceJSONfile = urlopen(INPUT_URL_DIRECTORY)
#spaceCountryList = json.load(spaceJSONfile)


result = dict()
result["iso-3166-1-alpha-2"] = dict()
result["undefined"] = dict()
result["undefined"]["nothing"] = []
result["undefined"]["country"] = []
result["undefined"]["iso"] = []
result["undefined"]["geo"] = []
result["undefined"]["address"] = []

for spaceCountryItem in spaceCountryList:
	v_id 		= spaceCountryItem["id"]
	v_name 		= spaceCountryItem["name"]
	v_url 		= spaceCountryItem["url"]
	v_country 	= spaceCountryItem["country"]
	v_iso 		= spaceCountryItem["iso-3166-1-alpha-2"]
	v_lat 		= spaceCountryItem["lat"]
	v_lon 		= spaceCountryItem["lon"]
	v_address 	= spaceCountryItem["address"]
	
	if (v_iso != ""):
		if ( not v_iso in result["iso-3166-1-alpha-2"] ):
			result["iso-3166-1-alpha-2"][v_iso] = []
		
		result["iso-3166-1-alpha-2"][v_iso].append(v_id)
	else:	
		if (v_country == "" and v_iso == "" and v_lat == "" and v_lon == "" and v_address == ""):
			result["undefined"]["nothing"].append(v_id)
		else:
			if (v_country == ""):
				result["undefined"]["country"].append(v_id)
			if (v_iso == ""):
				result["undefined"]["iso"].append(v_id)	
			if (v_lat == "" and v_lon == ""):
				result["undefined"]["geo"].append(v_id)	
			if (v_address == ""):
				result["undefined"]["address"].append(v_id)
	#Set for country iso deduced from URL
	if (v_address == ""):
		result["undefined"]["address"].append(v_id)


#Process statistics
result["count"] = dict()
result["count"]["iso"] = dict()
result["count"]["undefined"] = dict()

#Count HACKERSPACES per Country
for v_iso in result["iso-3166-1-alpha-2"].keys():
	result["count"]["iso"][v_iso] = len( result["iso-3166-1-alpha-2"][v_iso] )

result_text = ""		
result_text = result_text + "HACKERSPACES per Country:\r\n"
for v_iso in sorted( result["count"]["iso"].keys() ):
	v_count = result["count"]["iso"][v_iso]
	result_text = result_text + "\t" + v_iso + ": " +  str(v_count) + "\r\n"
result_text = result_text + "\r\n"


#Count Undefined variables
result["count"]["undefined"]["nothing"] = len( result["undefined"]["nothing"] )
result["count"]["undefined"]["country"] = len( result["undefined"]["country"] )
result["count"]["undefined"]["iso"] 	= len( result["undefined"]["iso"] )
result["count"]["undefined"]["geo"] 	= len( result["undefined"]["geo"] )
result["count"]["undefined"]["address"] = len( result["undefined"]["address"] )

v_nothing = result["count"]["undefined"]["nothing"]
v_country = result["count"]["undefined"]["country"]
v_iso = result["count"]["undefined"]["iso"] 
v_geo = result["count"]["undefined"]["geo"] 
v_address = result["count"]["undefined"]["address"]

result_text = result_text + "DATA INTEGRITY - Count\r\n"
result_text = result_text + "\t" + "HACKERSPACES with NOTHING:\t\t" +  			str(v_nothing) + "\r\n"
result_text = result_text + "\t" + "HACKERSPACES with no Country:\t\t" + 		str(v_country) + "\r\n"
result_text = result_text + "\t" + "HACKERSPACES with no Country Code:\t" + 	str(v_iso) + "\r\n"
result_text = result_text + "\t" + "HACKERSPACES with no GeoData:\t\t" + 		str(v_geo) + "\r\n"
result_text = result_text + "\t" + "HACKERSPACES with no Address:\t\t" + 		str(v_address) + "\r\n"
result_text = result_text + "\r\n"

v_nothing = result["undefined"]["nothing"]
v_country = result["undefined"]["country"]
v_iso = result["undefined"]["iso"] 
v_geo = result["undefined"]["geo"] 
v_address = result["undefined"]["address"]

result_text = result_text + "DATA INTEGRITY - IDs\r\n"
result_text = result_text + "\t" + "HACKERSPACES with NOTHING:\r\n" + "\t\t" +  		str(v_nothing) + "\r\n"
result_text = result_text + "\t" + "HACKERSPACES with no Country:\r\n" + "\t\t" + 		str(v_country) + "\r\n"
result_text = result_text + "\t" + "HACKERSPACES with no Country Code:\r\n" + "\t\t" + 	str(v_iso) + "\r\n"
result_text = result_text + "\t" + "HACKERSPACES with no GeoData:\r\n" + "\t\t" + 		str(v_geo) + "\r\n"
result_text = result_text + "\t" + "HACKERSPACES with no Address:\r\n" + "\t\t" + 		str(v_address) + "\r\n"
result_text = result_text + "\r\n"

result_text = result_text + "Objects Processed:\r\n"
result_text = result_text + str( len(spaceCountryList) )
result_text = result_text + "\r\n"

print(result_text)

#Write the results
with open(OUTPUT_PATH, 'w', newline="") as fw:
	fw.write(result_text)
	fw.close()