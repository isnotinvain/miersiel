import pygame
import util
from sensor import Sensor

class Nose(Sensor):

	def __init__(self, env, parent, range, shouldDraw=False):
		Sensor.__init__(self, env, parent, shouldDraw)
		self.range = range

	def getRay(self, ton):
		pt = self.parent.getCenter()
		tpt = ton.getCenter()

		dist = util.distance2(pt, tpt)
		angle = util.getAngle(pt, tpt)
		return (dist, angle, ton)


	def read(self):
		tons = self.env.tonsInCircle(self.parent.getCenter(), self.range)
		if self.parent in tons: tons.remove(self.parent)
		return set(self.getRay(ton) for ton in tons)

	def doDraw(self, screen):
		wCenter = self.parent.getCenter()
		center = map(lambda x : int(x), self.env.toScreen(wCenter))
		pygame.draw.circle(screen, (255,0,0), center, int(self.env.scToScreen(self.range)),1)