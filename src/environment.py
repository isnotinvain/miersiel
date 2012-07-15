import hurrr
import hurrr.physics.util

class Environment(object):

  def __init__(self, sim, camera):
    self.sim = sim
    self.tons = set()
    self.comms = {}
    self.camera = camera

  def writeComm(self, channelKey, ton, value):
    if channelKey not in self.comms:
      self.comms[channelKey] = {}
    self.comms[channelKey][ton] = value

  def readComm(self, channelKey, ton):
    if channelKey not in self.comms:
      return None
    if ton not in self.comms[channelKey]:
      return None
    return self.comms[channelKey][ton]

  def addTon(self, ton):
    self.tons.add(ton)

  def getTons(self):
    return self.tons

  def tonsInBox(self, leftTop, rightBottom):
    bodies = hurrr.physics.util.bodiesInRegion(self.sim.world, (leftTop, rightBottom))
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
    inBox = self.tonsInBox((left, top), (right, bottom))
    return set(x for x in inBox if hurrr.twod.distance2(x.getCenter(), center) <= radius**2)