import math
import random
import pygame

import hurrr

from automaton import *
from behavior import *
import Box2D as box2d
from sensors import Nose
from environment import Pheromone

class NewBot(Automaton):
  def __init__(self, env, sim, pos, color=hurrr.colors.LCARS.ORANGE, radius=0.5, density=1.0, restitution=0.6, friction=0.5):
    Automaton.__init__(self, env, sim)
    self.color = color
    self.drawColor = color
    self.radius = radius

    self.body = self.sim.addBody(pos, self)
    bodyCircleDef = box2d.b2CircleDef()
    bodyCircleDef.radius = self.radius
    bodyCircleDef.localPosition.Set(0.0, 0.0)
    bodyCircleDef.density = density
    bodyCircleDef.restitution = restitution
    bodyCircleDef.friction = friction
    self.body.CreateShape(bodyCircleDef)
    self.body.SetMassFromShapes()

    self.force = (0,0)
    self.maxForce = 10
    self.torque = 0
    self.maxTorque = 10

    self.hold = self.getCenter()

    self.sensors['nose'] = Nose(self.env, self, 8.0, shouldDraw=False)
    self.behavior = self.__genBehavior()

  def draw(self, screen):
    wCenter = self.getCenter()
    sCenter = hurrr.twod.ints(self.env.camera.toScreen(wCenter))
    self.drawColor = hurrr.colors.LCARS.PURPLE if self.leaderElection.leadersMone else self.color
    pygame.draw.circle(screen, self.drawColor, sCenter, int(self.env.camera.scalarToScreen(self.radius)))
    if self.leaderElection.leadersMone:
      leader = hurrr.twod.ints(self.env.camera.toScreen(self.leaderElection.leadersMone.pos))
      pygame.draw.line(screen, hurrr.colors.LCARS.GREEN, sCenter, leader, 1)
    else:
      hold = hurrr.twod.ints(self.env.camera.toScreen(self.hold))
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

  def getCenter(self):
    return self.body.GetWorldCenter().tuple()

  def kill(self):
    self.sim.world.DestroyBody(self.body)

  def applyForce(self, f):
    self.force = hurrr.twod.vecAdd(self.force, f)

  def setForce(self, f):
    self.force = f

  def _applyForces(self):
    self.body.ApplyForce(hurrr.twod.ceil(self.force, self.maxForce), self.body.GetWorldCenter())
    self.force = (0, 0)

  def applyTorque(self, t):
    self.torque += t

  def setTorque(self, t):
    self.torque = t

  def _applyTorques(self):
    if abs(self.torque) > self.maxTorque:
      self.torque = (abs(self.torque) / self.torque) * self.maxTorque
    self.body.ApplyTorque(self.torque)
    self.torque = 0

  def turn(self, amount):
    velocityNeeded = amount / self.sim.timeStep
    currentVelocity = self.body.GetAngularVelocity()
    accelerationNeeded = (velocityNeeded - currentVelocity) / self.sim.timeStep
    momentInertia = 0.5 * self.body.GetMass() * self.radius ** 2
    torqueNeeded = momentInertia * accelerationNeeded
    self.applyTorque(torqueNeeded)

  def turnTo(self, desired, kp=1.0, kd=0.2):
    desired = hurrr.angle.normalizePositiveAngle(desired)
    current = hurrr.angle.normalizePositiveAngle(self.body.GetAngle())
    angleDelta = hurrr.angle.shortestTurn(current, desired)
    angleDelta = kp * angleDelta - kd * self.body.GetAngularVelocity()
    self.turn(angleDelta)

  def face(self, pt, kp=1.0, kd=0.2):
    desired = -1 * (hurrr.twod.angleBetweenPts(self.getCenter(), pt) + (hurrr.angle.HALF_PI))
    self.turnTo(desired, kp, kd)
    return desired

  def walkForwards(self, distance):
    cAngle = hurrr.angle.normalizeAngle(self.body.GetAngle())
    self.goTo(hurrr.twod.movePt(self.getCenter(), cAngle, distance))

  def goTo(self,target,kp=1.0,kd=1.0):
    pos = self.getCenter()
    distX,distY = target[0] - pos[0], target[1] - pos[1]
    vX,vY = self.body.GetLinearVelocity().tuple()
    Fx = kp*distX - kd*vX
    Fy = kp*distY - kd*vY
    self.setForce((Fx,Fy))

  def act(self):
    Automaton.act(self)
    self._applyForces()
    self._applyTorques()

  def __repr__(self):
    return "bot at: " + str(self.getCenter()) + " id: " + str(id(self))

  def __genBehavior(self):
    hangAroundHold = ConditionalBehavior(
     (
       (lambda ton, env, sim: hurrr.twod.distance2(ton.getCenter(), ton.hold) > 5**2, GetCloseToPt(self.hold, 2.0)),
     ),
     default=Wander()
    )

    handAroundLeader = ConditionalBehavior(
      (
        (lambda ton, env, sim: self.leaderElection.leadersMone and hurrr.twod.distance2(ton.getCenter(), self.leaderElection.leadersMone) > 5**2, GetCloseToLeader(2.0)),
      ),
      default=Wander()
    )
    self.leaderElection = HerdMember()
    return CompositeBehavior(
             self.leaderElection,
             ConditionalBehavior(
               (
                 (lambda ton, env, sim: self.leaderElection.leadersMone, hangAroundHold),
               ),
               default=handAroundLeader
             )
           )

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

class HerdMember(LeaderElection):
  def write(self, ton, env, sim):
    LeaderElection.write(self, ton, env, sim)
    if ton.leaderElection.leadersMone:
      ton.hold = ton.getCenter()

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

class GetCloseToLeader(Behavior):
  def __init__(self, closeEnough):
    self.closeEnough = closeEnough

  def act(self, ton, env, sim):
    ton.face(ton.leaderElection.leadersMone.pos)
    ton.walkForwards(3.0)
