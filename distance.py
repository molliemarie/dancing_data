import googlemaps
import datetime
import pdb
import json
import requests
import re

# start = 'Chicago, IL'
start = 'ORD'
# destinations = ['New York, NY', 'St. Louis, Missouri', 'Stockholm, Sweden', 
# 	   'Ann Arbor, MI', 'Minneapolis, MN']
# destinations = ['Chicago, IL']
destinations = ['NYC', 'STL', 'ARN', 'ARB','MSP']
gas_price = 2.24 #average gas price in Illinois 
mpg = 23.6 #average miles per gallon for cars and light trucks
km_in_mile = 1.609344

api_key = "AIzaSyAKHDuZsqZRAwxP9BqVCw-VmMTbeaoSoso"
url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + api_key
headers = {'content-type': 'application/json'}


gmaps = googlemaps.Client(key='AIzaSyAKHDuZsqZRAwxP9BqVCw-VmMTbeaoSoso')

# geocode_result = gmaps.geocode('Chicago, IL')

for destination in destinations:
	# if destination == start:
	# 	# if destination city is same as start city
	# 	price = 0
	# else:
	distance = gmaps.distance_matrix(start, destination)
	if distance['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
		# this means the destination is not driveable
		print(destination + ': not driveable')
	else:
		dur = distance['rows'][0]['elements'][0]['duration']['text']
		dist = distance['rows'][0]['elements'][0]['distance']['text'][0:-3]
		if dist == '':
			continue
		dist_int = int(dist.replace(',', ''))
		price_drive = round(((dist_int * gas_price) / (mpg * km_in_mile)), 2)
		time = dur.replace(' hours ', ':').replace('hour', ':').replace(' mins', '').replace(' min', '').split(':')
		if len(time) == 1:
			dt_seconds = datetime.timedelta(minutes=int(time[0])).seconds
		elif len(time) == 2:
			dt_seconds = datetime.timedelta(hours=int(time[0]), minutes=int(time[1])).seconds
		print(destination + ': '+ dur + ', $' + str(price_drive))
	# pdb.set_trace()
	if dt_seconds < 18000: 
		#less than 18000 seconds, or five hours
		price = price_drive
	else:
		price = 0
		# get airline price
		params = {
		  "request": {
		    "slice": [
		      {
		        "origin": start,
		        "destination": destination,
		        "date": "2016-11-19"
		      }
		    ],
		    "passengers": {
		      "adultCount": 1
		    },
		    "solutions": 1,
		    "refundable": False
		  }
		}

		response = requests.post(url, data=json.dumps(params), headers=headers)
		data = response.json()

		price_string = data['trips']['tripOption'][0]['saleTotal']
		price_split = re.split('(\d+)', price_string)
		price = price_split[1]
		currency = price_split[0]
		print(destination + ', $' + str(price))


pdb.set_trace()