

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

	def energy(self):
		"""
		Calculate energy of each individual event
		Takes into consideration cost of event, cost of flight...
		"""
		if self.workshop_cost == '' and self.party_pass_cost == '':
			cost = self.flight_cost + 100
		elif self.workshop_cost != '':
			cost = int(self.workshop_cost) + int(self.flight_cost)
		else:
			cost = int(self.party_pass_cost) + int(self.flight_cost) 
		energy = cost

		return energy




	def __str__(self):
		return 'Event: {}, Energy: {}'.format(self.name, self.energy()) 
