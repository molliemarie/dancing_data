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
import math

xrates.install('money.exchange.SimpleBackend')
xrates.base = 'USD'

COOLING_FACTOR = 0.99
MAX_ITER = 1000
MAX_EVENTS = 10
MOVES_PER_TEMPERATURE = 5 #TKTK - find out how to decide on best number for this...
MAX_CHANGE_NUMBER = 8

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

def create_new_group(in_state):
	new_state = random_step(in_state)
	new_group = create_group(new_state)
	
	return new_state, new_group

def simulated_annealing(in_state):

	# estimate a good starting temperature by attempting a few non-stupid
    # transitions and measuring the average change in temperature.

	current_group = create_group(in_state)
	delta_energies = []
	while len(delta_energies) < 20:
		new_state, new_group = create_new_group(in_state)
		delta_energies.append(abs(new_group.energy() - current_group.energy()))
	temperature = sum(delta_energies) / len(delta_energies)

    # EXPERIMENT with increasing the cooling factor (and decreasing the cooling
    # rate) to see how this affects the results.

    # EXPERIMENT with increasing the number of moves per temperature to more
    # thoroughly explore the state-space

    # continue until there are no changes in the energy.
	count = 0
	not_changed_counter = 0
	best_group = current_group #TKTK - why do this here?
	while not_changed_counter < MAX_CHANGE_NUMBER:
		temperature *= COOLING_FACTOR

		# at each temperature, try a bunch of different configurations to
		# let the system "equilibrate" at this temperature
		changed = False
		transition_unconditionally_accepted = 0
		transition_conditionally_accepted = 0
		transition_rejected = 0
		for n_moves in range(MOVES_PER_TEMPERATURE):
			# copy_and_transition returns a new state object
			new_state, new_group = create_new_group(in_state)
			delta_energy = new_group.energy() - current_group.energy()
			# always accept "downhill" moves that decrease the energy
			# TKTK Might not want to ALWAYS accept downhill movements. 
			# Play with this.
			if delta_energy < 0:
				current_group = new_group
				changed = True
				transition_unconditionally_accepted += 1
				if new_group.energy() < best_group.energy():
					best_group = new_group

	    	# conditionally accept "uphill" moves that increase the energy
			else:
				r = random.random()
				if math.exp(-delta_energy / temperature) > r:
					current_group = new_group
					transition_conditionally_accepted += 1
				else:
					transition_rejected += 1


		if not changed:
			not_changed_counter += 1
		else:
			not_changed_counter = 0
		# EXPERIMENT with resetting the state back to the best_state and
		# resetting the temperature/=cooling_factor**not_changed_counter and
		# not_changed_counter=0 and then continuing the simulation. This will
		# make it so that we make sure that the final state that leaves the
		# simulated annealing procedure is the best_state and that we have
		# tried to explore other nearby optimal configurations for this state.

		# print count to make sure working
		count += 1
		print(count)

	# print out results of this run and return the best state
	return best_group


# pull in data from google spreadsheet and create event list
# comprised of a list of instances
event_list = create_event_list()

# Create initial random bool set
bool_state = create_initial_random_set(event_list)

# use find best group
best_group = simulated_annealing(bool_state)

pdb.set_trace()
