import requests
import pandas as pd
import numpy as np
import json
import os
from dotenv import load_dotenv
load_dotenv()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


"""
Need to download own API keys from Yelp, Foursquare and Google to be able to complete the script.  These are 
stored as environmental variables to protect values.
"""

# Yelp API information
yelp_client_ID = os.environ['YELP_ID']
yelp_api_key = os.environ['YELP_API_KEY']
    
# Google API information
g_api_key = os.environ['G_API_KEY']

# Foursquare API information
foursquare_id = os.environ['FS_ID']
foursquare_secret = os.environ['FS_SECRET']


"""
Ask for inputs from the user.  The user inputs a text string for a location in the first line, 
then an integer for the search radius in the second line.  The second line will ensure an integer
input before continuing.
"""

place = input(f"{bcolors.HEADER}\nWhere would you like to search? {bcolors.ENDC}")

while True:
    try:
        rad = int(input(f"{bcolors.HEADER}\nWhat search radius would you like to use? (max 5000m) {bcolors.ENDC}"))
    except ValueError:
        print(f"{bcolors.WARNING}Please input an integer{bcolors.ENDC}")
        continue
    else:
        break


# for location written down, give back lat,long coordinates. Store as g_data

g_url = ("https://maps.googleapis.com/maps/api/place/findplacefromtext/"
    "json?"
    "input={1}"
    "&inputtype=textquery"
    "&fields=geometry"
    "&key={0}"
    .format(g_api_key, place))

g_resp = requests.get(g_url)
g_data = g_resp.json()


# pull latitude and longitude data from json file
coord_dict = {'lat':[],'long':[]}

lat = g_data['candidates'][0]['geometry']['location']['lat']
long = g_data['candidates'][0]['geometry']['location']['lng']

"""
Using the inputs given by the user, and the outputs of the latitude/longitude,
request from Yelp API points of interest in the area.  Data will be sorted 
by popularity and json output will be stored in yelp_data.
Used Postman to format the get request.
"""


url = ("https://api.yelp.com/v3/businesses/search?"
    "term=&latitude={0}"
    "&longitude={1}"
    "&radius={2}"
    "&sort_by=rating"
    .format(lat,long,rad))

payload = {}
headers = {
  'Authorization': 'Bearer %s' % yelp_api_key
}

yelp_resp = requests.request("GET", url, headers=headers, data = payload)
yelp_data = yelp_resp.json()

# initialize dictionary
yelp_dict = {'name':[],'rating':[],'review count': [],'latitude':[],'longitude':[]}

#parse through to add key information to dictionary    
for x in range(len(yelp_data['businesses'])):
    
    yelp_dict['name'].append(yelp_data['businesses'][x]['name'])
    yelp_dict['rating'].append(yelp_data['businesses'][x]['rating'])
    yelp_dict['review count'].append(yelp_data['businesses'][x]['review_count'])
    yelp_dict['latitude'].append(yelp_data['businesses'][x]['coordinates']['latitude'])
    yelp_dict['longitude'].append(yelp_data['businesses'][x]['coordinates']['longitude'])

# create main dataframe to store output data
df_yelp = pd.DataFrame(yelp_dict)

# create top 10 dataframe to capture only most popular areas
df_yelp_10 = df_yelp.head(10)


"""
Using the inputs given by the user, and the outputs of the latitude/longitude,
request from Foursquare API points of interest in the area.  Data will be sorted 
by popularity and json output will be stored in fs_data.  Data is also filtered
with the use of section='topPicks' to remove popular, but otherwise unremarkable
places (McDonalds, grocery stores, etc)
"""

# Foursquare API request, this request sorts results by popularity

fs_url = 'https://api.foursquare.com/v2/venues/explore'

params = dict(
client_id=foursquare_id,
client_secret=foursquare_secret,
v='20180323',
ll= str(lat)+','+str(long),
radius=rad,
section='topPicks',
sortByPopularity=1,
limit=200
)
fs_resp = requests.get(url=fs_url, params=params)
fs_data = json.loads(fs_resp.text)

#initialize dictionary
fs_dict = {'id':[],'name':[],'latitude':[],'longitude':[]}

# parse through JSON for applicable data
for i in range(len(fs_data['response']['groups'])):
    for j in range(len(fs_data['response']['groups'][i]['items'])):
        fs_dict['id'].append(fs_data['response']['groups'][i]['items'][j]['venue']['id'])
        fs_dict['name'].append(fs_data['response']['groups'][i]['items'][j]['venue']['name'])
        fs_dict['latitude'].append(fs_data['response']['groups'][i]['items'][j]['venue']['location']['lat'])
        fs_dict['longitude'].append(fs_data['response']['groups'][i]['items'][j]['venue']['location']['lng']) 

# establish main dataframe
df_fs = pd.DataFrame(fs_dict)

#establish top 10 dataframe
df_fs_10 = df_fs.head(10)


# print output statements
print("\n---------------------------------------------------------------------")
print("---------------------------------------------------------------------\n")
print("There are {0} Yelp locations and {1} Foursquare locations in the specified area."
.format(df_yelp.shape[0],df_fs.shape[0]))
"""
print("\nAccording to Yelp, here are the top 10 places within {} m:\n".format(rad))
for row in range(df_yelp_10.shape[0]):
    print('\t',row + 1,'-',df_yelp_10['name'][row])

print("\nAccording to Foursquare, here are the top 10 places within {} m:\n".format(rad))
for row in range(df_fs_10.shape[0]):
    print('\t',row + 1,'-',df_fs_10['name'][row])
"""

# show the top places that each list have in common

yelp_names = df_yelp['name']
fs_names = df_fs['name']
common = fs_names[fs_names.isin(yelp_names)].reset_index(drop=True)

if len(common) > 0:
    print('\nThe places in common between Yelp and Foursquare are:\n')
    for row in range(len(common)):
        print('\t',row+1,'-',common[row])
else:
    print('\nThere are no places in common between the sites.')

# combine lists to make full top 10
full_list = pd.concat([df_fs_10,df_yelp_10])
short_list = full_list.sort_index().head(10).reset_index(drop=True)

print('\nCombining the lists, the top 10 places are:\n')
for row in range(short_list.shape[0]):
    print('\t',row + 1,'-',short_list['name'][row])

"""
Google Directions to calculate the total time to visit each place using each location
as a waypoint.  This takes the latitude and longitude of each location as a waypoint
for the Google Direction API
"""

# using the combined top 10 list to input as waypoint string for Google Direction API
# the waypoint string has a specific format, this is used to match it
fs_list = []

for row in range(short_list.shape[0]):
    fs_list.append(str(short_list['latitude'][row])+'%2C'+str(short_list['longitude'][row]))

waypoint_string = '|'.join(fs_list)


# request information from Google API, store output json in g_dir_data

g_dir_url = ("https://maps.googleapis.com/maps/api/directions/"
             "json?"
             "origin={1}"
             "&destination={1}"
             "&waypoints=optimize:true|"
             "{2}"
             "&key={0}"
             .format(g_api_key,fs_list[0],waypoint_string))

g_dir_resp = requests.get(g_dir_url)

g_dir_data = g_dir_resp.json()


# calculation and output of the total time to go from location to location

time = 0

for x in range(len(g_dir_data['routes'][0]['legs'])):
    time += g_dir_data['routes'][0]['legs'][x]['duration']['value']
                
minutes = round(time/60)


# show the optimal order of locations

order = g_dir_data['routes'][0]['waypoint_order']


# print output statements

print("\nIt will take about {} minutes to drive between each of the top 10 locations.\n".format(minutes))


# based on the waypoint optimization, this will print out the best order for getting from location to location

print("The optimal order to visit the locations is:\n")
for i in range(len(order)):
    print('   ','  '*i,'->',(short_list['name'][order[i]]))
print("")
print("")