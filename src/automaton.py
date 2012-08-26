import hurrr
from behavior import Behavior

class Automaton(object):

  def __init__(self, env, sim, sensors=None):
    self.sim = sim
    self.env = env
    self.sensors = sensors or {}
    self.behavior = self.genBehavior()

  def getCenter(self):
    pass

  def read(self):
    self.behavior.read(self, self.env, self.sim)

  def write(self):
    self.behavior.write(self, self.env, self.sim)

  def act(self):
    self.behavior.act(self, self.env, self.sim)

  def draw(self, screen):
    pass

  def kill(self):
    pass

  def genBehavior(self):
    pass

class LimitedForceAutomaton(Automaton):
  def __init__(self, env, sim, maxForce, maxTorque, sensors=None):
    super(LimitedForceAutomaton, self).__init__(env, sim, sensors)
    self.maxForce = maxForce
    self.maxTorque = maxTorque
    self.force = (0,0)
    self.torque = 0

  def applyForce(self, f):
    self.force = hurrr.twod.vecAdd(self.force, f)

  def setForce(self, f):
    self.force = f

  def applyTorque(self, t):
    self.torque += t

  def setTorque(self, t):
    self.torque = t

  def getLimitedForce(self):
    f = hurrr.twod.ceil(self.force, self.maxForce)
    self.force = (0, 0)
    return f

  def getLimitedTorque(self):
    if abs(self.torque) > self.maxTorque:
      self.torque = (abs(self.torque) / self.torque) * self.maxTorque
    t = self.torque
    self.torque = 0
    return t

class BasicMobilityBot(LimitedForceAutomaton):
  def turn(self, amount):
    pass

  def turnTo(self, desired, kp=1.0, kd=0.2):
    pass

  def face(self, pt, kp=1.0, kd=0.2):
    pass

  def walkForwards(self, distance):
    pass

  def goTo(self,target,kp=1.0,kd=1.0):
    pass
