import pygame
from sensor import Sensor

class Nose(Sensor):

	def __init__(self, env, parent, range, shouldDraw=False):
		Sensor.__init__(self, env, parent, shouldDraw)
		self.range = range

	def read(self):
		tons = self.env.tonsInCircle(self.parent.getCenter(), self.range)
		return set(ton for ton in tons if ton is not self.parent)

	def doDraw(self, screen):
		wCenter = self.parent.getCenter()
		center = map(lambda x : int(x), self.env.toScreen(wCenter))
		pygame.draw.circle(screen, (255,0,0), center, int(self.env.scToScreen(self.range)),1)