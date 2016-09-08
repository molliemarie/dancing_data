import bs4
import requests
import re
from event import Event

URL_SP = 'http://www.swingplanit.com'
URL_DC = 'http://dancecal.com/?sMon=3&sYear=2016&num=10&list=1&theme=&hidetype=&hidedanceIcon='
splitters = ['?', ':']
event_list =[]
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
			event.details = event_soup.findAll('p')[0].text
			event.teachers = event_soup.findAll('p')[2].text.split(', ')
			li_tags = event_soup.findAll('li')
			for li in li_tags:
				li_text = (li.get_text())
				for splitter in splitters:
					if splitter in li_text:
						print(li_text.split(splitter,1)[0] + ': ' + 
							  li_text.split(splitter,1)[1])
						if li_text.split(splitter,1)[0].lower() == 'when':
							event.dates = li_text.split(splitter,1)[1].strip()
						if li_text.split(splitter,1)[0].lower() == 'country':
							event.country = li_text.split(splitter,1)[1].strip()
						if li_text.split(splitter,1)[0].lower() == 'town':
							event.city = li_text.split(splitter,1)[1].strip()
						if li_text.split(splitter,1)[0].lower() == 'website':
							event.url = li_text.split(splitter,1)[1].strip()
						if li_text.split(splitter,1)[0].lower() == 'styles':
							event.dance_styles = li_text.split(splitter,1)[1].lower().strip().split(',')
			event_list.append(event)
	return event_list
	import pdb; pdb.set_trace()

def scrape_dance_cal():
	soup = get_soup(URL_DC)
	for event_div in soup.findAll('div', {'class' : 'DCListEvent'}):
		# if 'DCListEvent' in event_div['class']:
		print(event_div)
		import pdb; pdb.set_trace()




# Scrape from swingplanit.com
scrape_swing_planit()

# scrape from dancecal.com
scrape_dance_cal()


# events = soup.findAll("li", { "class" : "color-shape" })




# For each item in list:
# Follow link to event information
# Retrive name, dates, country, town, website, styles, and notes and put into class
