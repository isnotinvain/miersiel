import math
import pygame
import random

import util
from automaton import Automaton, Behavior
import Box2D as box2d
from sensors import Nose

class NewBot(Automaton):
	def __init__(self, env, sim, pos, color=(100, 100, 100), radius=0.5, density=1.0, restitution=0.6, friction=0.5):
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

		self.sensors['nose'] = Nose(self.env, self, 4.0, shouldDraw=False)
		self.behavior = self.__genBehavior()

	def draw(self, screen):
		wCenter = self.getCenter()
		center = map(lambda x : int(x), self.env.toScreen(wCenter))
		self.drawColor = (0,255,0) if self.isLeader else self.color
		pygame.draw.circle(screen, self.drawColor, center, int(self.env.scToScreen(self.radius)))
		if self.leader:
			leader = map(lambda x : int(x), self.env.toScreen(self.leader.getCenter()))
			pygame.draw.line(screen, (0,255,0), center, leader, 1)
		else:
			hold = map(lambda x: int(x), self.env.toScreen(self.hold))
			pygame.draw.circle(screen, (0,0,255), hold, 3)
			linecolor = (0,0,0)
			pygame.draw.line(screen, linecolor, center, hold, 1)

		cAngle = self.body.GetAngle()
		vec = -1 * math.sin(cAngle), math.cos(cAngle)
		x, y = util.scaleVec(vec, self.radius)
		x += wCenter[0]
		y += wCenter[1]
		end = self.env.toScreen((x, y))
		pygame.draw.line(screen, (0, 0, 0), center, end, 1)

	def getCenter(self):
		return self.body.GetWorldCenter().tuple()

	def kill(self):
		self.sim.world.DestroyBody(self.body)

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
		velocityNeeded = amount / self.sim.timeStep
		currentVelocity = self.body.GetAngularVelocity()
		accelerationNeeded = (velocityNeeded - currentVelocity) / self.sim.timeStep
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
		return desired

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

	def act(self):
		Automaton.act(self)
		self._applyForces()
		self._applyTorques()

	def __repr__(self):
		return "bot at: " + str(self.getCenter()) + " id: " + str(id(self))

	def __genBehavior(self):
		ifTooFarFromHold = lambda ton, env, sim: util.distance2(ton.getCenter(), ton.hold) > 5**2

		hangAroundHold = Wander()
		goBackToHold = GetCloseToPt(self.hold, hangAroundHold, 2.0)
		hangAroundHold.conditions = [(ifTooFarFromHold, goBackToHold)]
		leaderBehavior = hangAroundHold

		ifTooFarFromLeader = lambda ton, env, sim: ton.leader!=None and util.distance2(ton.getCenter(), ton.leader.getCenter()) > 5**2
		hangAroundLeader = Wander()
		goBackToLeader = GetCloseToLeader(hangAroundLeader, 3.0)
		hangAroundLeader.conditions = [(ifTooFarFromLeader, goBackToLeader)]

		followerBehavior = hangAroundLeader

		return HerdElectLeader(self, leaderBehavior, followerBehavior)
#		leaderBehavior = Wander()
		#return HerdElectLeader(self, )

class Wander(Behavior):
	def __init__(self, conditions=None):
		self.color = (100,100,100)
		Behavior.__init__(self, conditions)
		self.desiredAngle = random.random() * util.twoPi

	def act(self, ton, env, sim):
		self.desiredAngle += (random.random() * (util.twoPi/ 10.0)) - util.twoPi/ 20.0
		ton.turnTo(self.desiredAngle)
		ton.walkForwards(1.0)

class HerdElectLeader(Behavior):
	def __init__(self, ton, leaderBehavior, followerBehavior):
		conditions = [(lambda ton, env, sim: self.isLeader, leaderBehavior), \
									(lambda ton, env, sim: self.isLeader == False and self.leader, followerBehavior)]

		Behavior.__init__(self, conditions)
		self.isLeader = None
		self.leader = None
		self.isLeaderCandidate = None
		self.tieBreaker = None
		ton.leader = None
		ton.isLeader = None

	def read(self, ton, env, sim):
		if not ton.sensors['nose']: return
		self.bors = ton.sensors['nose'].read()
		self.herdDist = sum(ray[0] for ray in self.bors)
		env.writeComm(HerdElectLeader, ton, self.herdDist)

	def communicate(self, ton, env, sim):
		if self.isLeaderCandidate:
 			otherCandidates = dict( \
				(env.readComm("Leadership", bor[2])['tie-breaker'], bor[2]) \
				for bor in self.bors if env.readComm("Leadership", bor[2])['isLeader'])
			if otherCandidates:
				maxRand = max(otherCandidates.iterkeys())
				if self.tieBreaker > maxRand:
					self.isLeader = True
					ton.isLeader = True
					ton.leader = None
				elif self.tieBreaker == maxRand:
					self.tieBreaker = random.random()
					env.writeComm("Leadership", ton, {'isLeader': True, 'tie-breaker': self.tieBreaker})
				else:
					self.isLeaderCandidate = False
					self.isLeader = False
					ton.isLeader = False
				env.writeComm("Leadership", ton, {'isLeader': False})
			else:
				self.isLeader = True
				ton.isLeader = True
				ton.leader = None

		if self.isLeader == False:
 			potentialLeaders = tuple(bor[2] for bor in self.bors if env.readComm("Leadership", bor[2])['isLeader'])
			if len(potentialLeaders) == 1:
				self.leader = potentialLeaders[0]
				ton.leader = self.leader
		else:
			herdDists = dict((env.readComm(HerdElectLeader, bor[2]), bor[2]) for bor in self.bors)
			if herdDists:
				minHerdDist = min(herdDists.iterkeys())
				if self.herdDist > minHerdDist:
					self.isLeader = False
					ton.isLeader = False
					env.writeComm("Leadership", ton, {'isLeader': False})
				else:
					self.tieBreaker = random.random()
					env.writeComm("Leadership", ton, {'isLeader': True, 'tie-breaker': self.tieBreaker})
					self.isLeaderCandidate = True

class GetCloseToPt(Behavior):
	def __init__(self, to, getThereBehavior, closeEnough):
		self.color = (255,0,0)
		self.to = to
		self.closeEnough = closeEnough
		conditions = [(self.isCloseEnough, getThereBehavior)]
		Behavior.__init__(self, conditions)

	def isCloseEnough(self, ton, env, sim):
		return util.distance2(self.to, ton.getCenter()) <= self.closeEnough**2

	def act(self, ton, env, sim):
		ton.face(self.to)
		ton.walkForwards(1.0)

class GetCloseToLeader(Behavior):
	def __init__(self, getThereBehavior, closeEnough):
		self.color = (255,0,0)
		self.closeEnough = closeEnough
		conditions = [(self.isCloseEnough, getThereBehavior)]
		Behavior.__init__(self, conditions)

	def isCloseEnough(self, ton, env, sim):
		return util.distance2(ton.getCenter(), ton.leader.getCenter()) <= self.closeEnough**2

	def act(self, ton, env, sim):
		ton.face(ton.leader.getCenter())
		ton.walkForwards(1.0)
