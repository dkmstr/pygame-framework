#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import tempfile
import os

# Early logger configuration, before imports so we can use logger everywhere
logging.basicConfig(
    filename=os.path.join(tempfile.gettempdir(), 'log.log'),
    filemode='w',
    format='%(levelname)s %(asctime)s %(module)s %(funcName)s %(lineno)d %(message)s',
    level=logging.DEBUG
)

# Main imports
import pygame
from pygame.locals import *
from player import Player
from items import *
import game
from game.actors import actorsFactory
from game.sound import soundsStore

WIDTH = 1024
HEIGHT = 768

BASE_SPEED = 8


class GameTest(game.game_state.GameState):
    framerate = 50

    def __init__(self, name):
        super(GameTest, self).__init__(name)

        self.bg_speed = 0

        # self.images = game.images.Images((1280, 2880))
        self.maps = game.maps.Maps()
        self.maps.add('level0', 'data/maps/level-test-0.tmx')
        #self.maps.add('level0', 'data/maps/level.tmx')

        self.map = None
        #self.bg = parallax.ParallaxSurface((WIDTH, HEIGHT), pygame.RLEACCEL)

    def on_init(self):
        # Register actors types
        actorsFactory.registerType('Player', Player)
        soundsStore.storeMusicFile('level0', 'journey_3.ogg')
        
        #self.images.addImage('bck1', 'data/images/far-background.png')
        #self.images.addImage('bck2', 'data/images/near-background.png')
        #self.images.load(self.controller.screen)

        #self.maps.add('level0', 'data/maps/other.tmx')
        self.maps.load()

        self.map = self.maps.get('level0')
        self.player = list(self.map.getActors('Player'))[0]

        #self.bg.add_surface(self.images.get('bck1'), 5)
        #self.bg.add_surface(self.images.get('bck2'), 3)

    def on_enter(self):
        soundsStore.get('level0').play()
        pass

    def on_exit(self):
        pygame.mixer.music.stop()
        print 'Exiting'

    def on_keydown(self, key):
        if key == K_q:
            return game.game_state.GameControl.EXIT_GAMESTATE
        elif key == K_RIGHT:
            self.player.goRight()
        elif key == K_LEFT:
            self.player.goLeft()
        elif key == K_SPACE:
            self.player.jump()
        elif key == K_DOWN:
            pass

    def on_keyup(self, key):
        if key in (K_RIGHT, K_LEFT):
            self.player.stop()
        elif key in (K_UP, K_DOWN):
            pass

    def on_frame(self):
        #self.bg.scroll(self.bg_speed)
        self.map.update()
        #self.player.move(self.x_speed, self.y_speed)

        self.player.updateMapDisplayPosition(self.controller.screen)
        return None

    def on_render(self):
        #self.bg.draw(self.controller.screen)
        self.map.draw(self.controller.screen)
        #self.player.draw(self.controller.screen)
        return None

gc = game.game_state.GameControl(WIDTH, HEIGHT)
gc.add(GameTest('state0'))
#gc.add(GameTest('state1'))

import cProfile

cProfile.run('gc.run()', os.path.join(tempfile.gettempdir(), 'test.stats'))
#gc.run()

gc.quit()