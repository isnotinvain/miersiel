from sensor import Sensor

class Nose(Sensor):

	def __init__(self, environment, range):
		Sensor.__init__(self, environment)
		self.range = range
