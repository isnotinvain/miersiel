class Sensor(object):

	def __init__(self, env, parent, shouldDraw):
		self.env = env
		self.parent = parent
		self.shouldDraw = shouldDraw

	def read(self):
		pass

	def draw(self, screen):
		if self.shouldDraw:
			self.doDraw(screen)

	def doDraw(self, screen):
		pass