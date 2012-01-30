from langutil import Enum

class Automaton(object):
	ONE_STATE = Enum.new("default")
	DEFAULT_STATE = ONE_STATE.default

	def __init__(self, env, simulation, sensors=None, states=ONE_STATE, defaultState=DEFAULT_STATE, onStateTransition=None):
		self.simulation = simulation
		self.env = env
		self.sensors = sensors
		if not self.sensors:
			self.sensors = {}
		if not issubclass(states, Enum):
			states = Enum.new(*states)
		self.states = states
		self.defaultState = defaultState
		self.currentState = defaultState
		self.onStateTransition = onStateTransition

	def getCenter():
		pass

	def update(self):
		pass

	def communicate(self):
		pass

	def draw(self, screen):
		pass

	def kill(self):
		pass

	def changeState(self, state):
		if not hasattr(self.states, str(state)):
			raise ValueError("Invalid state change, I have no knowlege of state: " + str(state))
		if self.onStateTransition:
			self.onStateTransition(self.currentState, state)
		self.currentState = state