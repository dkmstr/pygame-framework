#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import pygame
from pygame.locals import *
import resources
import parallax

WIDTH = 1280
HEIGHT = 1024

BASE_SPEED = 8

class GameTest(resources.game_state.GameState):
    framerate = 50

    def __init__(self, name):
        super(GameTest, self).__init__(name)

        self.x_speed = self.y_speed = self.bg_speed = 0
        self.x = self.y = 0

        self.images = resources.images.Images((1280, 2880))
        self.maps = resources.maps.Maps()

        self.map = None
        self.bg = parallax.ParallaxSurface((WIDTH, HEIGHT), pygame.RLEACCEL)

    def on_init(self):
        self.images.addImage('bck1', 'data/images/far-background.png')
        self.images.addImage('bck2', 'data/images/near-background.png')
        self.images.load(self.controller.screen)

        self.maps.add('level0', 'data/maps/level.tmx')
        #self.maps.add('level0', 'data/maps/other.tmx')
        self.maps.load()

        self.map = self.maps.get('level0')

        self.bg.add_surface(self.images.get('bck1'), 5)
        self.bg.add_surface(self.images.get('bck2'), 3)

    def on_enter(self):
        pygame.mixer.music.load(resources.util.resource_path('data/sound/forest_0.ogg'))
        pygame.mixer.music.play(-1)

    def on_exit(self):
        print 'Exiting'

    def on_keydown(self, key):
        if key == K_q:
            return resources.game_state.GameControl.EXIT_GAMESTATE
        elif key == K_RIGHT:
            self.x_speed = BASE_SPEED
            self.bg_speed = BASE_SPEED
        elif key == K_LEFT:
            self.x_speed = -BASE_SPEED
            self.bg_speed = -BASE_SPEED
        elif key == K_UP:
            self.y_speed = -BASE_SPEED
        elif key == K_DOWN:
            self.y_speed = BASE_SPEED

    def on_keyup(self, key):
        if key in (K_RIGHT, K_LEFT):
            self.x_speed = 0
            self.bg_speed = 0
        elif key in (K_UP, K_DOWN):
            self.y_speed = 0

    def on_frame(self):
        self.bg.scroll(self.bg_speed)
        self.x += self.x_speed
        self.y += self.y_speed

    def on_render(self):
        self.bg.draw(self.controller.screen)
        self.map.draw(self.controller.screen, self.x, self.y)

logging.basicConfig(
    filename='log.log',
    filemode='w',
    format='%(levelname)s %(asctime)s %(module)s %(funcName)s %(lineno)d %(message)s',
    level=logging.DEBUG
)


gc = resources.game_state.GameControl(WIDTH, HEIGHT)
gc.add(GameTest('state0'))
gc.add(GameTest('state1'))

#import cProfile

#cProfile.run('gc.run()')
gc.run()