from behavior import Behavior
class Automaton(object):

  def __init__(self, env, sim, behavior=Behavior(), sensors=None):
    self.sim = sim
    self.env = env
    self.sensors = sensors or {}
    self.behavior = behavior

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

