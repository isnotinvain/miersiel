import pygame
import hurrr
import hurrr.physics.util

class Environment(object):

  def __init__(self, sim, camera):
    self.sim = sim
    self.tons = set()
    self.mones = hurrr.collections.TwoDIndex(3)
    self.moneLifetimes = {}
    self.camera = camera
    self.shouldDraw = True

  def update(self):
    newMoneLifetimes = dict((mone, life-1) for mone, life in self.moneLifetimes.iteritems() if life > 0)
    for mone in [mone for mone in self.moneLifetimes.iterkeys() if mone not in newMoneLifetimes]:
      self.removeMone(mone)
    self.moneLifetimes = newMoneLifetimes

  def draw(self, screen):
    if self.shouldDraw:
      for mone in self.moneLifetimes.iterkeys():
        rect = (hurrr.twod.add(self.camera.toScreen(mone.pos), (-5, -5)), (10,10))
        pygame.draw.rect(screen, mone.color, rect)

  def addTon(self, ton):
    self.tons.add(ton)

  def getTons(self):
    return self.tons

  def addMone(self, mone, life):
    self.mones[mone.pos] = mone
    self.moneLifetimes[mone] = life

  def removeMone(self, mone):
    del self.mones[mone]
    del self.moneLifetimes[mone]

  def monesInBox(self, pt1, pt2):
    return self.mones[pt1:pt2:True]

  def monesInSquare(self, center, distance):
    return self.mones[center:distance:True]

  def tonsInBox(self, pt1, pt2):
    pt1, pt2 = hurrr.twod.normalizeRect(pt1, pt2)
    bodies = hurrr.physics.util.bodiesInRegion(self.sim.world, (leftBottom, rightTop))
    tons = set()
    for body in bodies:
      parent = body.userData['parent']
      if parent and parent in self.tons:
        tons.add(parent)
    return tons

  def tonsInCircle(self, center, radius):
    cx, cy = center
    left = cx - radius
    right = cx + radius
    top = cy + radius
    bottom = cy - radius
    inBox = self.tonsInBox((left, bottom), (right, top))
    # todo: use two circumscribed circle?
    return set(x for x in inBox if hurrr.twod.distance2(x.getCenter(), center) <= radius**2)

class Pheromone(object):
  def __init__(self, pos, kind, value=None, color=hurrr.colors.LCARS.WHITE):
    self.pos = pos
    self.kind = kind
    self.value = value
    self.color = color