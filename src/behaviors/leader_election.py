import random
import hurrr
from behavior import Behavior
from environment import Pheromone

class LeaderElection(Behavior):
  MONES = hurrr.lang.Enum.new("LEADER", "FOLLOWER")
  def __init__(self, voteFunc=None):
    self.voteFunc = voteFunc or self.__voteFunc
    self.vote = None
    self.leadersMone = None

  def __voteFunc(self, ton, env, sim):
    if not self.vote:
      self.vote = random.random()
    return self.vote

  def read(self, ton, env, sim):
    self.leadersMone = None
    self.vote = self.voteFunc(ton, env, sim)

    if not ton.sensors['nose']: return
    leadersNearMe = [(mone, ray) for mone, ray in ton.sensors['nose'].read() if mone.kind == LeaderElection.MONES.LEADER]
    if len(leadersNearMe) > 0:
      strongestLeaderMone,_ = max(leadersNearMe, key=lambda (mone, _): mone.value)
      if strongestLeaderMone.value > self.vote:
        self.leadersMone = strongestLeaderMone

  def write(self, ton, env, sim):
    if self.leadersMone:
      color = hurrr.colors.LCARS.TAN
      kind = LeaderElection.MONES.FOLLOWER
    else:
      color = hurrr.colors.LCARS.RED
      kind = LeaderElection.MONES.LEADER
    env.addMone(Pheromone(ton.getCenter(), kind, value=self.vote, color=color), 1)

class GetCloseToLeader(Behavior):
  def __init__(self, closeEnough, leaderElection):
    self.closeEnough = closeEnough
    self.leaderElection = leaderElection

  def act(self, ton, env, sim):
    ton.face(self.leaderElection.leadersMone.pos)
    ton.walkForwards(3.0)
