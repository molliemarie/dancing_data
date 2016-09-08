

class Event(object):
	def __init__(self, name=None, dates=None, country=None, 
				 city=None, url=None, dance_styles=None):
		self.name = name
		self.dates = dates
		self.country = country
		self.city = city
		self.url = url
		self.dance_styles = dance_styles

		def __str__(self):
			return 'Event: {}, dates: {}, location: {}, {}, dance styles: {}'.format(self.name, self.dates, self.city, self.country, self.dance_styles) 
