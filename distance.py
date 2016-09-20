import googlemaps
import datetime
import pdb
import json
import requests
import re
import utils
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from dateutil.parser import parse
from GeoBases import GeoBase

geo_a = GeoBase(data='airports', verbose=False)


# Set up gspread
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/mollie/Dropbox (Datascope Analytics)/dancing_data/drive_key.json', scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1dDE72PW8HV8QaWJg9OYzaaYSvCBrmT50vrDN84cJzA0/edit#gid=0")
worksheet = spreadsheet.worksheet('Sheet1')

# TKTK:
# 1) Need a way to get the airport code for the closest airport if given
# a city and country. Build that in.
# 2) feed in real data from google spreadsheets

start_airport = 'ORD'# start = 'ORD'
start_city = "Chicago, IL"
DRIVING_LIMIT = 18000
# destinations = ['New York, NY', 'St. Louis, Missouri', 'Stockholm, Sweden', 
# 	   'Ann Arbor, MI', 'Minneapolis, MN']
# destinations = ['Chicago, IL']
# destinations = ['NYC', 'STL', 'ARN', 'DTW','MSP']
gas_price = 2.24 #average gas price in Illinois 
mpg = 23.6 #average miles per gallon for cars and light trucks
km_in_mile = 1.609344

api_key = "AIzaSyAKHDuZsqZRAwxP9BqVCw-VmMTbeaoSoso"
url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + api_key
headers = {'content-type': 'application/json'}


gmaps = googlemaps.Client(key='AIzaSyAKHDuZsqZRAwxP9BqVCw-VmMTbeaoSoso')

# geocode_result = gmaps.geocode('Chicago, IL')

for row_number, row  in enumerate(utils.iter_worksheet(spreadsheet, 'Sheet1', header_row = 1)):
	status = row['status']
	if status == 'past':
		continue
	else:
		start_date = (parse(row['start date'])).strftime('%Y-%m-%d')
		end_date = (parse(row['end date'])).strftime('%Y-%m-%d')
		destination = row['city'] + ', ' + row['country']
		geocode = gmaps.geocode(destination)
		lat = geocode[0]['geometry']['bounds']['southwest']['lat']
		lng = geocode[0]['geometry']['bounds']['southwest']['lng']
		destination_airports = [k for _, k in sorted(geo_a.findNearPoint((lat, lng), 40))]

		# loop through all airports retrieved in order to get the cheapest cost

		# pdb.set_trace()

		# if destination == start:
		# 	# if destination city is same as start city
		# 	price = 0
		# else:
		distance = gmaps.distance_matrix(start_city, destination)
		if distance['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
			# this means the destination is not driveable
			print(destination + ': not driveable')
			dt_seconds = DRIVING_LIMIT + 1
		else:
			dur = distance['rows'][0]['elements'][0]['duration']['text']
			dist = distance['rows'][0]['elements'][0]['distance']['text'][0:-3]
			if dist == '':
				continue
			dist_int = int(dist.replace(',', ''))
			price_drive = round(((dist_int * gas_price) / (mpg * km_in_mile)), 2)
			if 'day' in dur:
				dt_seconds = DRIVING_LIMIT + 1
			else:
				time = dur.replace(' hours ', ':').replace('hour', ':').replace(' mins', '').replace(' min', '').split(':')
				# pdb.set_trace()
				if len(time) == 1:
					dt_seconds = datetime.timedelta(minutes=int(time[0])).seconds
				elif len(time) == 2:
					dt_seconds = datetime.timedelta(hours=int(time[0]), minutes=int(time[1])).seconds
				print(destination + ': '+ dur + ', $' + str(price_drive))
		if dt_seconds < DRIVING_LIMIT: 
			#less than 18000 seconds, or five hours
			price = price_drive
		else:
			price = 9999
			for airport2 in destination_airports:
			# get airline price
				params = {
				  "request": {
				    "slice": [
				      {
				        "origin": start_airport,
				        "destination": airport2,
				        "date": start_date
				      },
				      {
				      	"origin": airport2,
				      	"destination": start_airport, 
				      	"date": end_date
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
				try:
					price_string = data['trips']['tripOption'][0]['saleTotal']
					price_split = re.split('(\d+)', price_string)
					price_test = int(price_split[1])
					currency = price_split[0]
					if price_test < price:
						price = price_test
				except KeyError:
					continue

			print(destination + ', $' + str(price))


		# pdb.set_trace()