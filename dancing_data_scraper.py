import bs4
import requests
import re
from event import Event

URL = 'http://www.swingplanit.com'
splitters = ['?', ':']
event_list =[]
def get_soup(url):
    """Download and convert to BeautifulSoup."""
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    return soup

# def get_event_link(soup)

# def main():
soup = get_soup(URL)
# events = soup.findAll("li", { "class" : "color-shape" })
for a_tag in soup.findAll('a', href=True):
	if a_tag.parent.name == 'li':
		try:
			# Put in this try except to stop it from breaking when
			# encountering parents with no class.
			if 'color-shape' in a_tag.parent['class']:
				# only grap a-tags with color-shape class 
				# print(a_tag['href'])
				event_soup = get_soup(a_tag['href'])
				event = Event()
				event.name = event_soup.title.text
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
				# import pdb; pdb.set_trace()
		except KeyError:
			# Put in this try except to stop it from breaking when
			# encountering parents with no class
			continue

import pdb; pdb.set_trace()


# For each item in list:
# Follow link to event information
# Retrive name, dates, country, town, website, styles, and notes and put into class
