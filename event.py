

class Event(object):
	def __init__(self, name=None, dates=None, country=None, 
				 city=None, state=None, url=None, dance_styles=None,
				 details=None, teachers=None, bands=None, status=None):
		self.name = name
		self.dates = dates
		self.country = country
		self.city = city
		self.url = url
		self.dance_styles = dance_styles
		self.details = details
		self.teachers = teachers
		self.state = state
		self.bands = bands
		self.status = 'upcoming'


		def __str__(self):
			return 'Event: {}, dates: {}, location: {}, {}, dance styles: {}'.format(self.name, self.dates, self.city, self.country, self.dance_styles) 
