import pygame
from sensor import Sensor

class Nose(Sensor):

	def __init__(self, env, parent, range, shouldDraw=False):
		Sensor.__init__(self, env, parent, shouldDraw)
		self.range = range

	def read(self):
		return env.tonsInCircle(self, center, radius)

	def doDraw(self, screen):
		wCenter = self.parent.getCenter()
		center = map(lambda x : int(x), self.env.toScreen(wCenter))
		pygame.draw.circle(screen, (255,0,0), center, int(self.env.scToScreen(self.range)),1)