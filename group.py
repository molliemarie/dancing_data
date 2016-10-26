from event import Event

class Group(object):
	def __init__(self, events=None, event_names=None):
		self.events = []
		self.event_names = []

	def energy(self):
		return sum(event.energy() for event in self.events)
