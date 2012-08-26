import math
import pygame
import hurrr

from pointbot import PointBot
from behavior import *
from behaviors.leader_election import *
from behaviors.simple import *
from sensors import Nose

class LeaderBot(PointBot):
  def __init__(self, env, sim, pos):
    sensors = {'nose' : Nose(env, self, 8.0, shouldDraw=False)}
    super(LeaderBot, self).__init__(env, sim, pos, color=hurrr.colors.LCARS.ORANGE, radius=0.5, density=1.0, restitution=0.6, friction=0.5, maxForce=10, maxTorque=10, sensors=sensors)

  def draw(self, screen):
    wCenter = self.getCenter()
    sCenter = hurrr.twod.ints(self.env.camera.toScreen(wCenter))
    self.drawColor = hurrr.colors.LCARS.PURPLE if self.herdMember.leadersMone else self.color
    pygame.draw.circle(screen, self.drawColor, sCenter, int(self.env.camera.scalarToScreen(self.radius)))
    if self.herdMember.leadersMone:
      leader = hurrr.twod.ints(self.env.camera.toScreen(self.herdMember.leadersMone.pos))
      pygame.draw.line(screen, hurrr.colors.LCARS.GREEN, sCenter, leader, 1)
    else:
      hold = hurrr.twod.ints(self.env.camera.toScreen(self.herdMember.hold))
      pygame.draw.circle(screen, hurrr.colors.LCARS.BLUE, hold, 3)
      linecolor = hurrr.colors.LCARS.WHITE
      pygame.draw.line(screen, linecolor, sCenter, hold, 1)

    cAngle = self.body.GetAngle()
    vec = -1 * math.sin(cAngle), math.cos(cAngle)
    x, y = hurrr.twod.scale(vec, self.radius)
    x += wCenter[0]
    y += wCenter[1]
    end = self.env.camera.toScreen((x,y))
    pygame.draw.line(screen, hurrr.colors.LCARS.WHITE, sCenter, end, 1)

  def genBehavior(self):
    self.herdMember = HerdMember()

    hangAroundHold = ConditionalBehavior(
     (
       (lambda ton, env, sim: hurrr.twod.distance2(ton.getCenter(), self.herdMember.hold) > 5**2, GetCloseToPt(self.herdMember.hold, 2.0)),
     ),
     default=Wander()
    )

    handAroundLeader = ConditionalBehavior(
      (
        (lambda ton, env, sim: self.herdMember.leadersMone and hurrr.twod.distance2(ton.getCenter(), self.herdMember.leadersMone) > 5**2, GetCloseToLeader(2.0, self.herdMember)),
      ),
      default=Wander()
    )

    return CompositeBehavior(
             self.herdMember,
             ConditionalBehavior(
               (
                 (lambda ton, env, sim: self.herdMember.leadersMone, hangAroundHold),
               ),
               default=handAroundLeader
             )
           )

class HerdMember(LeaderElection):
 def __init__(self):
   super(HerdMember, self).__init__()
   self.hold = None

 def write(self, ton, env, sim):
   LeaderElection.write(self, ton, env, sim)
   if not self.hold or self.leadersMone:
     self.hold = ton.getCenter()