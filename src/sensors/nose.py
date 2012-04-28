import pygame
import hurrr

from sensor import Sensor

class Nose(Sensor):

  def __init__(self, env, parent, range, shouldDraw=False):
    Sensor.__init__(self, env, parent, shouldDraw)
    self.range = range

  def getRay(self, ton):
    pt = self.parent.getCenter()
    tpt = ton.getCenter()

    dist = hurrr.twod.distance2(pt, tpt)
    angle = hurrr.twod.angleBetweenPts(pt, tpt)
    return (dist, angle, ton)


  def read(self):
    tons = self.env.tonsInCircle(self.parent.getCenter(), self.range)
    if self.parent in tons: tons.remove(self.parent)
    return set(self.getRay(ton) for ton in tons)

  def doDraw(self, screen):
    wCenter = self.parent.getCenter()
    sCenter = hurrr.twod.ints(self.env.camera.toScreen(wCenter))
    pygame.draw.circle(screen, (204,102,102), sCenter, int(self.env.camera.scalarToScreen(self.range)),1)