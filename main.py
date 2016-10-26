from oauth2client.service_account import ServiceAccountCredentials
import gspread
from event import Event
from group import Group
import utils
import pdb
from dateutil.parser import parse
from random import randrange
from money import Money, xrates
from decimal import Decimal
import numpy as np


xrates.install('money.exchange.SimpleBackend')
xrates.base = 'USD'

temp = 5000
cooling_rate = 0.99
max_iter = 1000

# TKTK Later make this so that it will pull exchange rates from API to get most updated rate
# {'', 'EUR', 'HKS', 'CAD', 'MYR', 'CLP', 'US', 'USD', 'CAN', 'CHF', 'GBP', 'SEK', 'AUD'}
xrates.setrate('HKS', Decimal('7.76'))
xrates.setrate('EUR', Decimal('0.92'))
xrates.setrate('MYR', Decimal('4.15'))
xrates.setrate('CAD', Decimal('1.34'))
xrates.setrate('CAN', Decimal('1.34'))
xrates.setrate('CLP', Decimal('653.35'))
xrates.setrate('CHF', Decimal('0.99'))
xrates.setrate('GBP', Decimal('0.82'))
xrates.setrate('SEK', Decimal('8.93'))
xrates.setrate('AUD', Decimal('1.31'))




# Set up gspread
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/mollie/Dropbox (Datascope Analytics)/dancing_data/drive_key.json', scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1dDE72PW8HV8QaWJg9OYzaaYSvCBrmT50vrDN84cJzA0/edit#gid=0")
worksheet = spreadsheet.worksheet('Sheet1')

# def convert_to_usd(row, column_title):
# 	foreign_currency_cost = Money(row[column_title], row['currency'])
# 	converted_cost2 = foreign_currency_cost.to('USD')
# 	return converted_cost2

# def split_hyphenated_costs(row, column_title):
# 	split_cost = [int(i) for i in row[column_title].split('-')]
# 	return split_cost

def get_cost(row, column_title):
	if row[column_title] != '':
		if '-' in row[column_title]:
			split_cost = [int(i) for i in row[column_title].split('-')]
			cost = np.mean(split_cost)
			# pdb.set_trace()
		else:
			cost = row[column_title]
		if row['currency'] == 'USD' or row['currency'] == 'US' or row['currency'] == '':
			# pdb.set_trace()
			converted_cost = cost
			# pdb.set_trace()
		else:
			foreign_currency_cost = Money(cost, row['currency'])
			converted = foreign_currency_cost.to('USD')
			converted_cost = float(converted.amount)
			# pdb.set_trace()
	else:
		converted_cost = ''
	# pdb.set_trace()
	return converted_cost

def create_event_list():
	event_list = []
	for row_number, row  in enumerate(utils.iter_worksheet(spreadsheet, 'Sheet1', header_row = 1)):
		if row['key'] != '' and row['obsolete'] != '1' and row['status'] != 'past':
			event = Event()
			event.key = row['key']
			event.name = row['name']
			event.start_date = parse(row['start date'])
			event.end_date = parse(row['end date'])
			event.city = row['city']
			event.state = row['state']
			event.country = row['country']
			event.dance_styles = row['dance styles']
			event.status = row['status']
			event.url = row['url']
			event.teachers = row['teachers']
			event.bands = row['bands']
			event.details = row['details']
			event.obsolete = row['obsolete']
			# pdb.set_trace()

			event.workshop_cost = get_cost(row, 'workshop cost')
			event.party_pass_cost = get_cost(row, 'party pass cost')
			pdb.set_trace()

			# if row['workshop cost'] != '':
			# 	if currency == 'USD' or currency == 'US':
			# 		if '-' in row['workshop cost']:
			# 			split_cost = split_hyphenated_costs(row, 'workshop cost')
			# 			workshop_cost = np.mean(split_cost)
			# 		else:
			# 			workshop_cost = int(row['workshop cost'])
			# 		event.workshop_cost = workshop_cost
			# 	else:
			# 		converted_cost = convert_to_usd(row, 'workshop cost')
			# 		event.workshop_cost = float(converted_cost.amount)
			# if row['party pass cost'] != '':
			# 	if currency == 'USD' or currency == 'US':
			# 		event.party_pass_cost = int(row['party pass cost'])
			# 	else:
			# 		converted_cost = convert_to_usd(row, 'party pass cost')
			# 		event.party_pass_cost = float(converted_cost.amount)
			# pdb.set_trace()
			# event.workshop_cost = Money(amount = float(row['workshop cost']), currency=row['currency'])
			# event.party_pass_cost = Money(amount = float(row['party pass cost']), currency=row['currency'])
			event.currency = row['currency']
			event.distance = int(row['distance'])
			event.flight_cost = int(row['flight cost'])
			event.event_type = row['type']
			if row['driving time'] == '':
				event.driving_time = 99999
			else: 
				event.driving_time = int(row['driving time'])
			event_list.append(event)
	return event_list

def create_initial_random_set(event_list):
	bool_state = [False] * len(event_list)
	count = 0
	while count < 7:
		rand_index = randrange(0, len(event_list))
		bool_state[rand_index] = True
		count += 1
	return bool_state


# def random_step(in_state):
#    new_state = []
#    #Copy in_state to new_state
#    for i in len(in_state):
#       new_state [i] = in_state[i]
#    rand_index = randrange(0, len(in_state))
#    #Flip one boolean
#    new_state[rand_index] = not new_state[rand_index] 

# def simulated_annealing():
# 	for i in range(max_iter):
#     new_state = random_step(bool_state)
#     energy_change = energy(new_state) - energy(bool_state)
#     if energy_change < -random.random(temp):
#         bool_state = new_state
#     temp = temp * cooling_rate


event_list = create_event_list()

# Create initial random bool set
bool_state = create_initial_random_set(event_list)








# pdb.set_trace()





# start random sample of events
# COST FUNCTION
#distance = 