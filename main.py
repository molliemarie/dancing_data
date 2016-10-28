from oauth2client.service_account import ServiceAccountCredentials
import gspread
from event import Event
from group import Group
import utils
import pdb
from dateutil.parser import parse
import random
from random import randrange
from money import Money, xrates
from decimal import Decimal
import numpy as np


xrates.install('money.exchange.SimpleBackend')
xrates.base = 'USD'

COOLING_RATE = 0.99
MAX_ITER = 1000
MAX_EVENTS = 10
MOVES_PER_TEMPERATURE = 5 #TKTK - find out how to decide on best number for this...
MAX_CHANGE_NUMBER = 3

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

def get_cost(row, column_title):
	"""
	Grabs the cost from the specified column. If there is a hyphenated
	range, it splits the range and finds the average. Then, checks for currency. 
	If the currency is not blank or USD, it converts the cost to  USD using Money.
	"""
	if row[column_title] != '' and row[column_title] != 'TBA':
		if '-' in row[column_title]:
			split_cost = [int(i) for i in row[column_title].split('-')]
			cost = np.mean(split_cost)
		else:
			cost = row[column_title]
		if row['currency'] == 'USD' or row['currency'] == 'US' or row['currency'] == '':
			converted_cost = cost
		else:
			foreign_currency_cost = Money(cost, row['currency'])
			converted = foreign_currency_cost.to('USD')
			converted_cost = float(converted.amount)
	else:
		converted_cost = ''
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
			event.workshop_cost = get_cost(row, 'workshop cost')
			event.party_pass_cost = get_cost(row, 'party pass cost')
			event.distance = int(row['distance'])
			event.flight_cost = int(row['flight cost'])
			event.event_type = row['type']
			if row['currency'] == '':
				event.currency = 'USD'
			else:
				event.currency = row['currency']
			if row['driving time'] == '':
				event.driving_time = 99999
			else: 
				event.driving_time = int(row['driving time'])
			event_list.append(event)
	return event_list

def create_initial_random_set(event_list):
	bool_state = [False] * len(event_list)
	count = 0
	while count < MAX_EVENTS:
		rand_index = randrange(0, len(event_list))
		bool_state[rand_index] = True
		count += 1
	return bool_state


def random_step(bool_state):

	# TKTK - later make it so that it goes through various 
	# sizes of groups

	#Copy in_state to new_state
	new_state = bool_state.copy()

	# Find true / false indices
	true_indices = []
	false_indices = []
	# print('OLD STATE')
	for i, event in enumerate(bool_state):
		if event == True:
			true_indices.append(i)
			# print(i)
		else:
			false_indices.append(i)

	random_indices = []
	random_indices.append(random.choice(true_indices))
	random_indices.append(random.choice(false_indices))

	for index in random_indices:
		new_state[index] = not new_state[index]
	# print('NEW STATE')
	# for i, event in enumerate(new_state):
	# 	if event == True:
	# 		print(i)
	return new_state

   # rand_index = randrange(0, len(in_state))
   # #Flip one boolean
   # new_state[rand_index] = not new_state[rand_index] 

def create_group(bool_state):
	group = Group()
	for i, item in enumerate(bool_state):
		if item == True:
			group.events.append(event_list[i])
			group.event_names.append(event_list[i].name)
	return group

def new_group_and_delta_energies(in_state):
	new_state = random_step(in_state)
	new_group = create_group(new_state)
	delta_energies.append(abs(new_group.energy() - in_group.energy()))
	return new_group, delta_energies

def simulated_annealing(in_state):

	# estimate a good starting temperature by attempting a few non-stupid
    # transitions and measuring the average change in temperature.

	in_group = create_group(in_state)
	delta_energies = []
	while len(delta_energies) < 20:
		new_group, delta_energies = new_group_and_delta_energies(in_state)
	temperature = sum(delta_energies) / len(delta_energies)
	pdb.set_trace()

    # EXPERIMENT with increasing the cooling factor (and decreasing the cooling
    # rate) to see how this affects the results.

    # EXPERIMENT with increasing the number of moves per temperature to more
    # thoroughly explore the state-space

    # continue until there are no changes in the energy.
	not_changed_counter = 0
	best_group = current_group #TKTK - why do this here?
	while not_changed_count < MAX_CHANGE_NUMBER:
		temperature *= cooling_factor

		# at each temperature, try a bunch of different configurations to
        # let the system "equilibrate" at this temperature
        changed = False
        transition_unconditionally_accepted = 0
        transition_conditionally_accepted = 0
        transition_rejected = 0
        for n_moves in range(MOVES_PER_TEMPERATURE):
    	# copy_and_transition returns a new state object
    	new_state = random_step(in_state)
		new_group = create_group(new_state)
		delta_energies.append(abs(new_group.energy() - in_group.energy()))

    if not changed:
	    not_changed_counter += 1
	else:
	    not_changed_counter = 0
	# for i in range(MAX_ITER):
	# 	new_state = random_step(in_state)
	# 	new_group = create_group(new_state)
	# 	delta_energy = new_group.energy() = in_group.energy()
	# 	if delta_energy < -

		# in_state = new_state



	# for i in range(MAX_ITER):
 #    new_state = random_step(bool_state)
 #    energy_change = energy(new_state) - energy(bool_state)
 #    if energy_change < -random.random(TEMPERATURE):
 #        bool_state = new_state
 #    TEMPERATURE = TEMPERATURE * COOLING_RATE


event_list = create_event_list()

# Create initial random bool set
bool_state = create_initial_random_set(event_list)

simulated_annealing(bool_state)

# pdb.set_trace()








# pdb.set_trace()





# start random sample of events
# COST FUNCTION
#distance = 