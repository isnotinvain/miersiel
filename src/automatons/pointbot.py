import math
import pygame
import Box2D as box2d
import hurrr

from automaton import BasicMobilityBot

class PointBot(BasicMobilityBot):
  def __init__(self, env, sim, pos, color=hurrr.colors.LCARS.ORANGE, radius=0.5, density=1.0, restitution=0.6, friction=0.5, maxForce=10, maxTorque=10, sensors=None):
    super(PointBot, self).__init__(env, sim, maxForce, maxTorque, sensors)
    self.color = color
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

    self.sensors = sensors or {}
    self.behavior = self.genBehavior()

  def getCenter(self):
    return self.body.GetWorldCenter().tuple()

  def act(self):
    super(PointBot, self).act()
    self._applyForces()
    self._applyTorques()

  def draw(self, screen):
    wCenter = self.getCenter()
    sCenter = hurrr.twod.ints(self.env.camera.toScreen(wCenter))
    pygame.draw.circle(screen, self.color, sCenter, int(self.env.camera.scalarToScreen(self.radius)))
    cAngle = self.body.GetAngle()
    vec = -1 * math.sin(cAngle), math.cos(cAngle)
    x, y = hurrr.twod.scale(vec, self.radius)
    x, y = hurrr.twod.add((x,y), wCenter)
    end = self.env.camera.toScreen((x,y))
    pygame.draw.line(screen, hurrr.colors.LCARS.WHITE, sCenter, end, 1)

  def kill(self):
    self.sim.world.DestroyBody(self.body)

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

  def _applyForces(self):
    self.body.ApplyForce(self.getLimitedForce(), self.body.GetWorldCenter())

  def _applyTorques(self):
    self.body.ApplyTorque(self.getLimitedTorque())

  def __repr__(self):
    return "PointBot at: " + str(self.getCenter()) + " id: " + str(id(self))