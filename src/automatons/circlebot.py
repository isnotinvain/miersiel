import math
import pygame

import util
from automaton import Automaton
import Box2D as box2d

class CircleBot(Automaton):

	def __init__(self, environment, simulation, pos, color=(100, 100, 100), radius=0.5, density=1.0, restitution=0.6, friction=0.5):
		Automaton.__init__(self, environment, simulation)
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
		
	
	def draw(self, screen):
		wCenter = self.body.GetWorldCenter().tuple()
		center = map(lambda x : int(x), self.simulation.toScreen(wCenter))
		pygame.draw.circle(screen, self.color, center, int(self.simulation.scToScreen(self.radius)))
		cAngle = self.body.GetAngle()
		vec = -1 * math.sin(cAngle), math.cos(cAngle)
		x, y = util.scaleVec(vec, self.radius)
		x += wCenter[0]
		y += wCenter[1]
		end = self.simulation.toScreen((x, y))
		pygame.draw.line(screen, (0, 0, 0), center, end, 1)
	