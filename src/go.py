# miersiel (c) Alex Levenson 2011, All Rights Reserved

import sys
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE

import physics

class Game:
	def __init__(self, screen):
		# get everything set up
		self.screen = screen
		self.clock = pygame.time.Clock()
		self.bgColor = (255, 255, 255)
		self.running = False
		self.simulator = physics.PhysicsSimulator(self)

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

			# clear the display
			self.screen.fill(self.bgColor)

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

	# create an instance of the game
	game = Game(screen)

	# start the main loop
	game.run()

# make sure that main get's called
if __name__ == '__main__':
	main(sys.argv)