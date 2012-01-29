class Environment(object):
	
	def __init__(self, simulation):
		self.simulation = simulation
		self.automatons = []
	
	def addAutomaton(self, ton):
		self.automatons.append(ton)
	
	def getAutomatons(self):
		return self.automatons
	
	#def automatonsInBox: