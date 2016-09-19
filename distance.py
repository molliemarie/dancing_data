import googlemaps

start = 'Chicago, IL'
destinations = ['New York, NY', 'St. Louis, Missouri', 'Stockholm, Sweden', 
	   'Ann Arbor, MI', 'Minneapolis, MN']
# destinations = ['Stockholm, Sweden']

gmaps = googlemaps.Client(key='AIzaSyAKHDuZsqZRAwxP9BqVCw-VmMTbeaoSoso')

geocode_result = gmaps.geocode('Chicago, IL')

for destination in destinations:
	distance = gmaps.distance_matrix(start, destination)
	if distance['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
		print(destination + ': not driveable')
	else:
		print(destination + ': '+ distance['rows'][0]['elements'][0]['duration']['text'])

import pdb; pdb.set_trace()