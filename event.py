

class Event(object):
	def __init__(self, name=None, start_date=None, end_date=None, country=None, 
				 city=None, state=None, url=None, dance_styles=None,
				 details=None, teachers=None, bands=None, status=None, key=None,
				 obsolete=None, workshop_cost=None, party_pass_cost=None, currency=None, 
				 distance=None, driving_time=None, flight_cost=None, event_type=None):
		self.name = name
		self.start_date = start_date
		self.end_date = end_date
		self.country = country
		self.city = city
		self.url = url
		self.dance_styles = dance_styles
		self.details = details
		self.teachers = teachers
		self.state = state
		self.bands = bands
		self.status = 'upcoming'
		self.key = key
		self.obsolete = 0
		self.workshop_cost = workshop_cost
		self.party_pass_cost = party_pass_cost
		self.currency = currency
		self.distance = distance
		self.driving_time = driving_time
		self.flight_cost = flight_cost
		self.event_type = event_type



		def __str__(self):
			return 'Event: {}, dates: {}, location: {}, {}, dance styles: {}'.format(self.name, self.dates, self.city, self.country, self.dance_styles) 
