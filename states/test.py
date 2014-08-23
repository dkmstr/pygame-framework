#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
from pygame.locals import *
import resources


class GameTest(resources.GameState):
    framerate = 1

    def __init__(self, name):
        super(GameTest, self).__init__(name)

    def on_init(self):
        print 'Initializing'

    def on_enter(self):
        print 'Entering state'

    def on_exit(self):
        print 'Exiting'

    def on_keydown(self, key):
        if key == K_q:
            if self.name == 'state1':
                return resources.GameControl.EXIT_GAMESTATE
            else:
                return 'state1'

        print "Keydown: {}".format(key)

    def on_keyup(self, key):
        print "KeyUP: {}".format(key)

    def on_frame(self):
        print "Calculating frame logic for {}".format(self.name)

    def on_render(self):
        print "Rendering: {}".format(self.fps())


gc = resources.GameControl()
gc.add(GameTest('state0'))
gc.add(GameTest('state1'))
gc.run()
