# miersiel (c) Alex Levenson 2011, All Rights Reserved

import sys
import random
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE

import physics
import environment

from automatons.circlebot import HerdBot as Bot

class Game:
	def __init__(self, screen):
		# get everything set up
		self.screen = screen
		self.clock = pygame.time.Clock()
		self.bgColor = (255, 255, 255)
		self.running = False

		PPM = 25
		SCREENHEIGHT = self.screen.get_height()

		size = (environment.Environment._scToWorld(x, PPM,) for x in self.screen.get_size())
		aabb = ((-10,-10), tuple(x+10 for x in size))

		self.simulator = physics.PhysicsSimulator(aabb)
		self.env = environment.Environment(self.simulator, self.screen.get_height(), PPM=25.0)

		self.worldSize = tuple(self.env.scToWorld(x) for x in self.screen.get_size())

		self.creation()

	def creation(self):
		for i in xrange(100):
			x,y = ((x * random.random() * 0.8) + x * 0.1 for x in self.worldSize)
			self.env.addTon(Bot(self.env,self.simulator, (x,y)))

	def run(self):
		# the game's main loop
		self.running = True
		while self.running:
			# handle events
			for event in pygame.event.get():
				if event.type == QUIT:
					# bye bye! Hope you had fun!
					self.running = False
					break

			# update the physics engine
			self.simulator.update()

			for ton in self.env.getTons():
				ton.update()

			for ton in self.env.getTons():
				ton.communicate()

			# clear the display
			self.screen.fill(self.bgColor)

			for ton in self.env.getTons():
				ton.draw(self.screen)
				for sensor in ton.sensors.itervalues():
					sensor.draw(self.screen)

			# blit to the screen
			pygame.display.flip()

			# try to stay at 60 FPS
			self.clock.tick(60)

def main(args):
	# initialize pygame / screen size
	pygame.init()
	pygame.display.init()
	size = pygame.display.list_modes()[0]
	size = map(lambda x : int(x * 0.75), size)
	screen = pygame.display.set_mode(size)
	pygame.font_instance = pygame.font.Font(None, 20)
	# create an instance of the game
	game = Game(screen)

	# start the main loop
	game.run()

# make sure that main get's called
if __name__ == '__main__':
	main(sys.argv)