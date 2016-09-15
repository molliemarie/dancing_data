import bs4
import requests
import re
from event import Event
import datetime
from dateutil.parser import parse
import calendar
import pdb
import csv
import time
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import utils



URL_SP = 'http://www.swingplanit.com'
URL_DC = 'http://dancecal.com/?sMon=9&sYear=2016&num=12&hidetype=&list=1&theme=&hidedanceIcon='
SPLITTERS = ['?', ':']
event_list =[]
event_name_list = []

# Set up gspread
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('/Users/mollie/Dropbox (Datascope Analytics)/dancing_data/drive_key.json', scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1dDE72PW8HV8QaWJg9OYzaaYSvCBrmT50vrDN84cJzA0/edit#gid=0")
worksheet = spreadsheet.worksheet('Sheet1')

def get_soup(url):
    """Download and convert to BeautifulSoup."""
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    return soup

def scrape_swing_planit():
	soup = get_soup(URL_SP)
	for event_list_item in soup.findAll('li', {'class' : 'color-shape'}):
		for a_tag in event_list_item.findAll('a', href=True):
			event_soup = get_soup(a_tag['href'])
			event = Event()
			event.name = event_soup.title.text
			event_name_list.append(event.name)
			event.details = event_soup.findAll('p')[0].text
			event.teachers = event_soup.findAll('p')[2].text
			# event.teachers = event_soup.findAll('p')[2].text.split(', ')
			li_tags = event_soup.findAll('li')
			for li in li_tags:
				li_text = (li.get_text())
				for splitter in SPLITTERS:
					if splitter in li_text:
						print(event.name + li_text.split(splitter,1)[0] + ': ' + 
							  li_text.split(splitter,1)[1])
						if li_text.split(splitter,1)[0].lower() == 'when':
							date_range = li_text.split(splitter,1)[1].strip()
							date_range = date_range.split(' - ')
							event.start_date = parse(date_range[0])
							event.end_date = parse(date_range[1])
						if li_text.split(splitter,1)[0].lower() == 'country':
							event.country = li_text.split(splitter,1)[1].strip()
						if li_text.split(splitter,1)[0].lower() == 'town':
							event.city = li_text.split(splitter,1)[1].strip()
						if li_text.split(splitter,1)[0].lower() == 'website':
							event.url = li_text.split(splitter,1)[1].strip()
						if li_text.split(splitter,1)[0].lower() == 'styles':
							event.dance_styles = li_text.split(splitter,1)[1].lower().strip()
							# event.dance_styles = li_text.split(splitter,1)[1].lower().strip().split(',')
			event_list.append(event)
	return event_list

def scrape_dance_cal():
	soup = get_soup(URL_DC)
	for event_div in soup.findAll('div', {'class' : 'DCListEvent'})[0:1]:
		name = None
		event = Event()
		for span in event_div.findAll('span'):

			if 'DCListName' in span['class']:
				name = span.text.strip()
			if name in event_name_list:
				# checks to see if the event name already exists in the instance list
				# If it does, it skips it
				continue
				# TKTK add state and bands to the instances
				# these items are listed in the dancecal website, and not on swingplanit
			else:
				# This means the event does not already exist in the instance list
				# and will be added
				if 'DCListName' in span['class']:
					event.name = span.text.strip()
					for a_tag in span.findAll('a', href=True):
						event.url = a_tag['href']
				if 'DCEventInfoDate' in span['class']:
					event.start_date = parse(span.text)
					# Now need to guess what the end_date will be since this site does not provide it
					# I'm going to assume that events will tend to end on a Sunday
					# For example, if an event starts on a friday, I will make it's end-date two days later. 
					weekday = event.start_date.weekday()
					gap = datetime.timedelta(days = 6 - weekday)
					event.end_date = event.start_date + gap
				if 'DCEventInfoWhere' in span['class']:
					location_list = span.text.replace(':',',').split(',')
					if len(location_list) == 3:
						event.country = location_list[2].strip()
						event.city = location_list[1].strip()
					if len(location_list) == 4:
						event.country = location_list[3].strip()
						event.state = location_list[2].strip()
						event.city = location_list[1].strip()
				if 'DCEventInfoDances' in span['class']:
					event.dance_styles = span.text.split(': ')[1].lower().strip()
				if 'DCEventInfoTeachers' in span['class']:
					event.teachers = str(span).replace('<br/>', '$').replace(':', '$').replace('</i>', '$').replace('|', 'and').split('$')[1:-1]
				if 'DCEventInfoDesc' in span['class']:
					event.details = span.text.strip()
				if 'DCEventInfoBands' in span['class']:
					event.bands = span.text.split(':')[1].strip()
		if event.name != None:
			event_list.append(event)
	return event_list
				# print('Name: {}, Location: {}, {}, Dances: {}, Dates: {}'.format(event.name, event.city, event.country, event.dance_styles, event.start_date))

def all_event_info_to_csv():
	headers = ['name', 'start date', 'end date', 'city', 'state', 'country', 'dance_styles', 'url', 'details', 'teachers', 'bands', 'status']

	with open('scraped_event_info.csv', 'w') as f:
		writer = csv.writer(f)
		writer.writerow(headers)
		for event in event_list:
			start = event.start_date.strftime('%m/%d/%Y')
			end = event.end_date.strftime('%m/%d/%Y')
			row = [event.name.encode('latin-1'), start, end, event.city, event.state,
				   event.country, event.dance_styles, event.url, event.details, 
				   event.teachers, event.bands, event.status]
			writer.writerow(row)

def event_names_to_csv():
	with open('change_name_before_editing.csv', 'w') as f:
		writer = csv.writer(f)
		writer.writerow(['event'])
		for event in event_list:
			writer.writerow([event.name])

def event_info_to_googledoc():
	for event in event_list:
		print(event.name)
		start = event.start_date.strftime('%m/%d/%Y')
		end = event.end_date.strftime('%m/%d/%Y')
		row = [event.name, start, end, event.city, event.state,
			   event.country, event.dance_styles, event.status, event.url, 
			   event.teachers, event.bands, event.details]
		worksheet.insert_row(row, index=2)

def pull_googledoc_info():
	keys = []
	for row_number, row  in enumerate(utils.iter_worksheet(spreadsheet, 'Sheet1', header_row = 1)):
		pdb.set_trace()
		key = row['name'].lower(), parse(row['start date']).year
		keys.append(key)
	return keys
			



# Scrape from swingplanit.com
# scrape_swing_planit()


# scrape from dancecal.com
# scrape_dance_cal()

# all_event_info_to_csv()
#
# event_names_to_csv()

# event_info_to_googledoc()

pull_googledoc_info()









# TKTK Swingala (with accent over i) does not print correctly in csv. 
# Is it just the csv, or is it also messed up within instance?

# TKTK lowercase all event names when comparing

# Name and year to index of row
# when needing to replace

# for row_number, row  in enumerate(utils.iter_worksheeet(spreadsheet, 'sheet1', header_row = ??)):
	# key = row['name'], row['start']
	# unique[key] = row_number

