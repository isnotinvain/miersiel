import random

import hurrr
from behavior import Behavior

class Wander(Behavior):
  def __init__(self):
    self.desiredAngle = random.random() * hurrr.angle.TWO_PI

  def act(self, ton, env, sim):
    self.desiredAngle += (random.random() * (hurrr.angle.TWO_PI/ 10.0)) - hurrr.angle.TWO_PI/ 20.0
    ton.turnTo(self.desiredAngle)
    ton.walkForwards(1.0)

class GetCloseToPt(Behavior):
  def __init__(self, to, closeEnough):
    self.to = to
    self.closeEnough = closeEnough

  def act(self, ton, env, sim):
    ton.face(self.to)
    ton.walkForwards(3.0)