import random

import hurrr
from behavior import *
from environment import Pheromone

class Wander(Behavior):
  def __init__(self, delta=20.0, burst=1.0, speed=1.0):
    self.desiredAngle = random.random() * hurrr.angle.TWO_PI
    self.delta = delta
    self.burst = burst
    self.speed = speed

  def act(self, ton, env, sim):
    if random.random() < self.burst:
      self.desiredAngle += (random.random() * (hurrr.angle.TWO_PI / (self.delta / 2))) - hurrr.angle.TWO_PI / self.delta
      ton.turnTo(self.desiredAngle)
      ton.walkForwards(self.speed)

class GoToPt(Behavior):
  def __init__(self, toFunc, speed):
    self.toFunc = toFunc
    self.speed = speed

  def act(self, ton, env, sim):
    ton.face(self.toFunc(ton, env, sim))
    ton.walkForwards(self.speed)

class HangAround(DelegatingBehavior):
  def __init__(self, toFunc, speedW, speedR, closeEnough):
    self.goToPt = GoToPt(toFunc, speedR)
    b = ConditionalBehavior(
          (
            (lambda ton, env, sim: not self.goToPt.toFunc(ton, env, sim), Behavior()),
            (lambda ton, env, sim: hurrr.twod.distance2(self.goToPt.toFunc(ton, env, sim), ton.getCenter()) > closeEnough**2, self.goToPt),
          ),
          default=Wander(speed=speedW)
        )
    super(HangAround, self).__init__(b)

class HerdBase(Behavior):
  def __init__(self):
    self.target = None

  def read(self, ton, env, sim):
    if not ton.sensors['nose']: return
    othersNearMe = [(mone, ray) for mone, ray in ton.sensors['nose'].read() if mone.kind == HerdBase]
    c = ton.getCenter()
    for mone, _ in othersNearMe:
      c = hurrr.twod.add(c, mone.pos)
    self.target = hurrr.twod.mul(c, 1.0/(len(othersNearMe) + 1.0))

  def write(self, ton, env, sim):
    env.addMone(Pheromone(ton.getCenter(), HerdBase), 1)

class Herd(DelegatingBehavior):
  def __init__(self, speedW, speedR, closeEnough):
    self.herdBase = HerdBase()
    b = CompositeBehavior(self.herdBase, HangAround(self.__toFunc, speedW, speedR, closeEnough))
    super(Herd, self).__init__(b)

  def __toFunc(self, ton, env, sim):
    return self.herdBase.target

  def getTarget(self):
    return self.herdBase.target