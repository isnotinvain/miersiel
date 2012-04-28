class Automaton(object):

  def __init__(self, env, sim, behavior=None, sensors=None):
    self.sim = sim
    self.env = env
    self.sensors = sensors
    if not self.sensors:
      self.sensors = {}
    self.behavior = behavior

  def getCenter(self):
    pass

  def checkConditions(self):
    self.behavior.checkConditions(self, self.env, self.sim)

  def read(self):
    self.behavior.read(self, self.env, self.sim)

  def communicate(self):
    self.behavior.communicate(self, self.env, self.sim)

  def act(self):
    self.behavior.act(self, self.env, self.sim)

  def draw(self, screen):
    pass

  def kill(self):
    pass

class Behavior(object):
  def __init__(self, conditions=None):
    self.conditions = conditions
    if not self.conditions:
      self.conditions = []

  def checkConditions(self, ton, env, sim):
    for condition, behavior in self.conditions:
      if condition(ton, env, sim):
        ton.behavior = behavior

  def read(self, ton, env, sim):
    pass

  def communicate(self, ton, env, sim):
    pass

  def act(self, ton, env, sim):
    pass