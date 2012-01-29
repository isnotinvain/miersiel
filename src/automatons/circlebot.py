import math
import pygame
import random

import util
from automaton import Automaton
import Box2D as box2d
from sensors import Nose

class CircleBot(Automaton):

	def __init__(self, env, simulation, pos, color=(100, 100, 100), radius=0.5, density=1.0, restitution=0.6, friction=0.5):
		Automaton.__init__(self, env, simulation)
		self.color = color
		self.drawColor = color
		self.radius = radius

		self.body = self.simulation.addBody(pos, self)
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

		self.sensors['nose'] = Nose(self.env, self, 5.0)

	def getCenter(self):
		return self.body.GetWorldCenter().tuple()

	def draw(self, screen):
		wCenter = self.getCenter()
		center = map(lambda x : int(x), self.env.toScreen(wCenter))
		pygame.draw.circle(screen, self.drawColor, center, int(self.env.scToScreen(self.radius)))
		cAngle = self.body.GetAngle()
		vec = -1 * math.sin(cAngle), math.cos(cAngle)
		x, y = util.scaleVec(vec, self.radius)
		x += wCenter[0]
		y += wCenter[1]
		end = self.env.toScreen((x, y))
		pygame.draw.line(screen, (0, 0, 0), center, end, 1)

	def update(self):
		self._applyForces()
		self._applyTorques()

	def kill(self):
		self.simulation.world.DestroyBody(self.body)

	def applyForce(self, f):
		self.force = util.vecAdd(self.force, f)

	def setForce(self, f):
		self.force = f

	def _applyForces(self):
		self.body.ApplyForce(util.ceilVec(self.force, self.maxForce), self.body.GetWorldCenter())
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
		velocityNeeded = amount / self.simulation.timeStep
		currentVelocity = self.body.GetAngularVelocity()
		accelerationNeeded = (velocityNeeded - currentVelocity) / self.simulation.timeStep
		momentInertia = 0.5 * self.body.GetMass() * self.radius ** 2
		torqueNeeded = momentInertia * accelerationNeeded
		self.applyTorque(torqueNeeded)

	def turnTo(self, desired, kp=1.0, kd=0.2):
		desired = util.normalizePositiveAngle(desired)
		current = util.normalizePositiveAngle(self.body.GetAngle())
		angleDelta = util.shortestTurn(current, desired)
		angleDelta = kp * angleDelta - kd * self.body.GetAngularVelocity()
		self.turn(angleDelta)

	def face(self, pt, kp=1.0, kd=0.2):
		desired = -1 * (util.getAngle(self.getCenter(), pt) + (util.halfPi))
		self.turnTo(desired, kp, kd)

	def walkForwards(self, distance):
		cAngle = util.normalizeAngle(self.body.GetAngle())
		self.goTo(util.movePt(self.getCenter(), cAngle, distance))

	def goTo(self,target,kp=1.0,kd=1.0):
		pos = self.getCenter()
		distX,distY = target[0] - pos[0], target[1] - pos[1]
		vX,vY = self.body.GetLinearVelocity().tuple()
		Fx = kp*distX - kd*vX
		Fy = kp*distY - kd*vY
		self.setForce((Fx,Fy))

	def __repr__(self):
		return "bot at: " + str(self.getCenter()) + " id: " + str(id(self))

class WanderBot(CircleBot):
	def __init__(self, env, simulation, pos, color=(100, 100, 100), radius=0.5, density=1.0, restitution=0.6, friction=0.5):
		CircleBot.__init__(self, env, simulation, pos, color=(100, 100, 100), radius=0.5, density=1.0, restitution=0.6, friction=0.5)
		self.desiredAngle = random.random() * util.twoPi

	def update(self):
		self.desiredAngle += (random.random() * (util.twoPi / 25.0)) - util.twoPi/50.0

		self.turnTo(self.desiredAngle)
		self.walkForwards(0.8)

		CircleBot.update(self)


class HerdBot(CircleBot):
		def __init__(self, env, simulation, pos, color=(100, 100, 100), radius=0.5, density=1.0, restitution=0.6, friction=0.5):
			CircleBot.__init__(self, env, simulation, pos, color=(100, 100, 100), radius=0.5, density=1.0, restitution=0.6, friction=0.5)
			self.nose = self.sensors['nose']
			self.herdDist = None
			self.isLeader = True
			self.friends = None
			self.hold = self.getCenter()
			self.myLeader = None
			self.timer = 0
			self.graze = self.getCenter()

		def update(self):
			self.friends = self.nose.read()
			self.herdDist = sum(ray[0] for ray in self.friends)

			CircleBot.update(self)

		def communicate(self):
			if self.isLeader:
				friendHerdDists = dict((friend[2].herdDist, friend[2]) for friend in self.friends if friend[2].isLeader)
				if friendHerdDists:
					minHerdDist = min(friendHerdDists.iterkeys())
					if self.herdDist > minHerdDist:
						self.isLeader = False
					if self.herdDist == minHerdDist and random.random() >= 0.5:
						self.isLeader = False
				self.goTo(self.hold)
			else:
				if not self.myLeader:
					try:
						self.myLeader = (friend[2] for friend in self.friends if friend[2].isLeader).next()
					except StopIteration:
						pass
				if self.myLeader:
					if util.distance2(self.getCenter(), self.myLeader.getCenter()) > 5.0:
						self.goTo(self.myLeader.getCenter())
					else:
						self.timer = (self.timer + 1) % 100
						if self.timer == 0:
							rx,ry = self.getCenter()
							rx += random.random() * 10 - 5
							ry += random.random() * 10 - 5
							self.graze = rx,ry
						else:
							self.goTo(self.graze)

		def draw(self, screen):
			self.drawColor = (0,150,0) if self.isLeader else self.color
			CircleBot.draw(self, screen)
#			text = pygame.font_instance.render(str(self.herdDist), 1, (0,0,0))
#			center = self.getCenter()
#			screen.blit(text, self.env.toScreen(center))
			#center = self.getCenter()
			#ex, ey = center
			#ey += self.herdDist * 0.1

			#pygame.draw.line(screen, (0,255,0), self.env.toScreen(center), self.env.toScreen((ex,ey)))
