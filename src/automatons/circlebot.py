import math
import pygame

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

		self.sensors['nose'] = Nose(self.env, self, 100.0, shouldDraw=True)

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

	def __repr__(self):
		return "bot at: " + str(self.getCenter()) + " id: " + str(id(self))

class HerdBot(CircleBot):
		def __init__(self, env, simulation, pos, color=(100, 100, 100), radius=0.5, density=1.0, restitution=0.6, friction=0.5):
			CircleBot.__init__(self, env, simulation, pos, color=(100, 100, 100), radius=0.5, density=1.0, restitution=0.6, friction=0.5)
			self.nose = self.sensors['nose']
			self.herdDist = None
			self.isLeader = True
			self.friends = None

		def update(self):
			self.friends = self.nose.read()
			self.herdDist = sum(util.distance2(self.getCenter(), friend.getCenter()) for friend in self.friends)

		def communicate(self):
			if self.isLeader:
				friendHerdDists = dict((friend.herdDist, friend) for friend in self.friends)
				minHerdDist = min(friendHerdDists.iterkeys())
				if self.herdDist > minHerdDist:
					self.isLeader = False

		def draw(self, screen):
			self.drawColor = (0,150,0) if self.isLeader else self.color
			CircleBot.draw(self, screen)
			text = pygame.font_instance.render(str(self.herdDist), 1, (0,0,0))
			center = self.getCenter()
			screen.blit(text, self.env.toScreen(center))
			#center = self.getCenter()
			#ex, ey = center
			#ey += self.herdDist * 0.1

			#pygame.draw.line(screen, (0,255,0), self.env.toScreen(center), self.env.toScreen((ex,ey)))
