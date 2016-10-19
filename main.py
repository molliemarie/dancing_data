from oauth2client.service_account import ServiceAccountCredentials
import gspread
from event import Event
import utils
import pdb

# Set up gspread
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/mollie/Dropbox (Datascope Analytics)/dancing_data/drive_key.json', scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1dDE72PW8HV8QaWJg9OYzaaYSvCBrmT50vrDN84cJzA0/edit#gid=0")
worksheet = spreadsheet.worksheet('Sheet1')


event_list = []
for row_number, row  in enumerate(utils.iter_worksheet(spreadsheet, 'Sheet1', header_row = 1)):
	event = Event()
	event.key = row['key']
	event.name = row['name']
	event.start_date = row['start date']
	event.end_date = row['end date']
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
	event.workshop_cost = row['workshop cost']
	event.party_pass_cost = row['party pass cost']
	event.currency = row['currency']
	event.travel_cost = row['travel cost']
	event.event_type = row['type']

	# key = row['name'].lower(), parse(row['start date']).year
	event_list.append(event)
pdb.set_trace()