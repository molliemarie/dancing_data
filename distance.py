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
import config

# TKTK if it's a past event, assume it will happen 
# around the same weekend the following year and make a new event

START_AIRPORT = 'ORD'
# Could edit to take into consideration both airports:
# START_AIRPORTs = ['ORD', 'MDW'] 
START_CITY = "Chicago, IL"
DAY_HOURS = 24 #hours in a day

GAS_PRICE = 2.24 #average gas price in Illinois 
MPG = 23.6 #average miles per gallon for cars and light trucks
KM_IN_MILE = 1.609344

DIST_COLUMN = '15'
DRIVING_TIME_COLUMN = '16'

# set up geobase to grab near airports
geo_a = GeoBase(data='airports', verbose=False)

# Set up gspread
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/mollie/Dropbox (Datascope Analytics)/dancing_data/drive_key.json', scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1dDE72PW8HV8QaWJg9OYzaaYSvCBrmT50vrDN84cJzA0/edit#gid=0")
worksheet = spreadsheet.worksheet('Sheet1')

# Google flights stuff
api_key = config.key
url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + api_key
headers = {'content-type': 'application/json'}

# googlemaps wrapper
gmaps = googlemaps.Client(key=config.key)

flight_cushion = gap = datetime.timedelta(days = 1)

# Loop through each row in the google spreadsheet
# for row_number, row  in enumerate(utils.iter_worksheet(spreadsheet, 'Sheet5', header_row = 1)):
# 	worksheet.update_cell(str(row_number+2), COLUMN, 'test1')
	# pdb.set_trace()

def find_distance_and_driving_duration(row_number, row):
	# retrieve lat/long of destination
	geocode = gmaps.geocode(destination)
	lat = geocode[0]['geometry']['bounds']['southwest']['lat']
	lng = geocode[0]['geometry']['bounds']['southwest']['lng']
	# get list of airports within 40 km of destination
	destination_airports = [k for _, k in sorted(geo_a.findNearPoint((lat, lng), 100))]

	# Find distance and duration of trip to destination city
	distance = gmaps.distance_matrix(START_CITY, destination)
	if distance['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
		worksheet.update_cell(str(row_number+2), DIST_COLUMN, 'Nan')
		# this means the destination is not driveable
		dt_hours = DAY_HOURS
	else:
		# pdb.set_trace()
		dur = distance['rows'][0]['elements'][0]['duration']['text']
		dist = distance['rows'][0]['elements'][0]['distance']['text'][0:-3]

		dist_int = int(dist.replace(',', '')) #remove comma from number and make int
		worksheet.update_cell(str(row_number+2), DIST_COLUMN, str(dist_int))
		dt_hours = 0

		# calculate driving cost
		price_drive = round(((dist_int * GAS_PRICE) / (MPG * KM_IN_MILE)), 2)
		if 'day' in dur:
			# driving duration over a day, so not driveable
			dt_hours = DAY_HOURS
		else:
			# time listed in format like "3 hours 25 minutes". Following code breaks that up
			time = dur.replace(' hours ', ':').replace('hour', ':').replace(' mins', '').replace(' min', '').split(':')
			if len(time) == 1:
				dt_hours = datetime.timedelta(minutes=int(time[0])).hours
			elif len(time) == 2:
				dt_hours = datetime.timedelta(hours=int(time[0]), minutes=int(time[1])).hours
		worksheet.update_cell(str(row_number+2), DRIVING_TIME_COLUMN, str(dt_hours))
		pdb.set_trace()
	return dur, dist_int, price_drive, dt_hours



for row_number, row  in enumerate(utils.iter_worksheet(spreadsheet, 'Sheet1', header_row = 1)):
	status = row['status'] 
	if status != 'past':
		start_date = (parse(row['start date'])).strftime('%Y-%m-%d')
		end_date = (parse(row['end date'])).strftime('%Y-%m-%d')
		start_date_with_cushion = ((parse(row['start date']))-flight_cushion).strftime('%Y-%m-%d')
		end_date_with_cushion = ((parse(row['end date']))+flight_cushion).strftime('%Y-%m-%d')
		departure_dates = [start_date, start_date_with_cushion]
		return_dates = [end_date, end_date_with_cushion]
		destination = row['city'] + ', ' + row['country']

		dur, dist_int, price_drive, dt_hours = find_distance_and_driving_duration(row_number, row)
		pdb.set_trace()

		print('TOO FAR')
		if dt_hours < DRIVING_LIMIT: 
			# if the driving time is within driving limit...
			price = price_drive
			print(destination + ', $' + str(price) + ', driving')
			driveable = 1
		else:
			# not within driving limit...
			driveable = 0
			price = 9999
			for airport2 in destination_airports: 
				for departure_date in departure_dates:
					for return_date in return_dates:
					#loops through each airport near the destination
					# finds roundtrip price for each set of start_airport and destination_airport
					# set price as smallest price
						params = {
						  "request": {
						    "slice": [
						      {
						        "origin": START_AIRPORT,
						        "destination": airport2,
						        "date": departure_date
						      },
						      {
						      	"origin": airport2,
						      	"destination": START_AIRPORT, 
						      	"date": return_date
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
							# KeyError happens if there are no flights from that airport
							continue

			print(destination + ', $' + str(price))

			# pdb.set_trace()
