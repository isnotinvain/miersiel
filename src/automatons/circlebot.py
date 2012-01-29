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
		pygame.draw.circle(screen, self.color, center, int(self.env.scToScreen(self.radius)))
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

		def update(self):
			friends = self.nose.read()

			for friend in friends:
				friend.color = (0,0,0)
