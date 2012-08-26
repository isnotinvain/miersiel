class Behavior(object):
  def read(self, ton, env, sim):
    pass

  def write(self, ton, env, sim):
    pass

  def act(self, ton, env, sim):
    pass

class CompositeBehavior(Behavior):
  def __init__(self, *behaviors):
    self.behaviors = list(behaviors) if behaviors else []

  def read(self, ton, env, sim):
    for behavior in self.behaviors:
      behavior.read(ton, env, sim)

  def write(self, ton, env, sim):
    for behavior in self.behaviors:
      behavior.write(ton, env, sim)

  def act(self, ton, env, sim):
    for behavior in self.behaviors:
      behavior.act(ton, env, sim)

class ConditionalBehavior(Behavior):
  def __init__(self, conditionals, default=Behavior()):
    self.conditionals = conditionals or ()
    self.current = None
    self.default = default

  def read(self, ton, env, sim):
    self.current = None
    for cond, behavior in self.conditionals:
      if cond(ton, env, sim):
        self.current = behavior
        break
    self.current = self.current or self.default
    self.current.read(ton, env, sim)

  def write(self, ton, env, sim):
    self.current.write(ton, env, sim)

  def act(self, ton, env, sim):
    self.current.act(ton, env, sim)
