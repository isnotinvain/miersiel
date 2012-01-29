class Sensor(object):

	def __init__(self, env, parent, shouldDraw=False):
		self.env = env
		self.parent = parent
		self.shouldDraw = shouldDraw

	def read(self):
		pass

	def draw(self, screen):
		if self.shouldDraw:
			self.doDraw(self, screen)

	def doDraw(self, screen):
		pass