import random
import pygame

import hurrr
import hurrr.gui
import hurrr.physics

from environment import Environment
from automatons.herdbot import HerdBot as Bot

class Go(object):
  def __init__(self):
    self.window = hurrr.gui.BorderScrollingWindow(
                                   updateFunc=lambda: self.update(),
                                   drawFunc=lambda screen:self.draw(screen),
                                   screenToWorldRatio=25.0,
                                   bgColor=hurrr.colors.LCARS.BLACK)
    self.window.run(setupWindow=lambda w: self.setupWindow(w))

  def setupWindow(self, window):
    wx, wy = window.size
    worldDims = window.camera.scalarToWorld(wx), window.camera.scalarToWorld(wy)
    self.world = hurrr.physics.Simulator(dimensions=((0,0),worldDims))
    window.camera.worldPos = hurrr.twod.mul(worldDims, 0.5)
    self.env = Environment(self.world, window.camera)

    for i in xrange(100):
      x,y = ((x * random.random() * 0.8) + x * 0.1 for x in self.world.dimensions[1])
      self.env.addTon(Bot(self.env,self.world, (x,y)))

  def update(self):
    self.env.update()

    for ton in self.env.getTons():
      ton.read()

    for ton in self.env.getTons():
      ton.write()

    for ton in self.env.getTons():
      ton.act()

    self.world.step()
    return True

  def draw(self, screen):
    for ton in self.env.getTons():
      ton.draw(screen)
      for sensor in ton.sensors.itervalues():
        sensor.draw(screen)
    self.env.draw(screen)
Go()