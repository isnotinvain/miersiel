import math

class Automaton(object):
	
	def __init__(self, environment, simulation, sensors={}):
		self.simulation = simulation
		self.environment = environment
		self.sensors = sensors

	def update(self):
		pass
		
	def draw(self, screen):
		pass
		
	def kill(self):
		pass
