import math
import pygame
import hurrr

from pointbot import PointBot
from behavior import *
from behaviors.leader_election import *
from behaviors.simple import *
from sensors import Nose

class HerdBot(PointBot):
  def __init__(self, env, sim, pos):
    sensors = {'nose' : Nose(env, self, 10.0, shouldDraw=False)}
    super(HerdBot, self).__init__(env, sim, pos, color=hurrr.colors.LCARS.ORANGE, radius=0.5, density=1.0, restitution=0.6, friction=0.5, maxForce=10, maxTorque=10, sensors=sensors)

  def draw(self, screen):
    super(HerdBot, self).draw(screen)
    sCenter = hurrr.twod.ints(self.env.camera.toScreen(self.getCenter()))
    target = hurrr.twod.ints(self.env.camera.toScreen(self.herd.getTarget()))
    pygame.draw.line(screen, hurrr.colors.LCARS.WHITE, sCenter, target, 1)

  def genBehavior(self):
    self.herd = Herd(2.0, 4.0, 8.0)
    return self.herd