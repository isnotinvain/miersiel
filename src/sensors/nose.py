import pygame
import hurrr

from sensor import Sensor

class Nose(Sensor):

  def __init__(self, env, parent, range, shouldDraw=False):
    Sensor.__init__(self, env, parent, shouldDraw)
    self.range = range

  def read(self):
    mones = self.env.monesInSquare(self.parent.getCenter(), self.range)
    return [(mone, hurrr.twod.getRay(self.parent.getCenter(), mone.pos)) for mone in mones]

  def doDraw(self, screen):
    wCenter = self.parent.getCenter()
    sCenter = hurrr.twod.ints(self.env.camera.toScreen(wCenter))
    pygame.draw.circle(screen, (204,102,102), sCenter, int(self.env.camera.scalarToScreen(self.range)), 1)