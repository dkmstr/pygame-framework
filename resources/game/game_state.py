# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pygame
from pygame.locals import *

from game.renderer import RendererGL as Renderer

import logging

logger = logging.getLogger(__name__)

SCREEN_BUFFER_SIZE = (1280,1024)

class GameState(object):
    def __init__(self, name):
        self.name = name
        self.controller = None
        self.events = 0
        self.frames = 0
        self.rendered_frames = 0
        self.frameSkip = 0
        self.frameSkipCount = 0

    def init(self):
        self.on_init()

    def enter(self):   # Activates the state
        self.on_enter()

    def exit(self):    # Exit form the state
        return self.on_exit()

    def tick(self, events):
        '''
        Processes one game 'tick'
        '''
        newState = None

        for event in events:
            newState = self.event(event)
            if newState is not None:
                break

        # Executes game logic
        if newState is None:
            newState = self.frame()

        return newState

    def event(self, ev):
        '''
        Invoked to process events (key down, mouse move, etc...)
        '''
        self.events += 1

        if ev.type == QUIT:
            return GameControl.EXIT_GAMESTATE
        elif ev.type == VIDEORESIZE:
            pygame.display.set_mode(ev.dict['size'],HWSURFACE|RESIZABLE)

        elif ev.type == KEYDOWN:
            return self.on_keydown(ev.key)
        elif ev.type == KEYUP:
            return self.on_keyup(ev.key)

    def frame(self):
        ''' game logic '''
        self.frames += 1
        return self.on_frame()


    def render(self):
        self.rendered_frames += 1

        return self.on_render()

    def on_init(self):
        print("Base on_init called!!!")

    def on_enter(self):
        print("Base on_enter called!!!")

    def on_exit(self):
        print("Base on_exit called!!!")

    def on_keydown(self, key):
        print("Base on_keydown called!!!")

    def on_keyup(self, key):
        print("Base on_keyup called!!!")

    def on_frame(self, event):
        print("Base on_frame called!!!")

    def on_render(self):
        print("Base on_render called!!!")


class GameControl(object):
    EXIT_GAMESTATE = 'EXIT_GAME'

    def __init__(self, width, height, framerate, enableFrameSkip=False, fullScreen=False, renderer=Renderer):
        self.states = {}
        self.current = None

        self.framerate = framerate
        self.frameskipEnabled = enableFrameSkip
        self.frameSkip = 0
        self.frameSkipCount = 0

        self.clock = pygame.time.Clock()

        # Initializes all used libraries
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()
        self.width = width
        self.height = height

        self.renderer = renderer(width, height, fullScreen=fullScreen)
        self.renderer.init()

    def add(self, state):
        state.controller = self
        state.init()

        self.states[state.name] = state
        if self.current is None:
            self.switch(state.name)

    def switch(self, game_state):
        if game_state not in self.states or game_state == GameControl.EXIT_GAMESTATE:
            logger.debug('Received game_state {}. EXITING'.format(game_state))
            return False

        if self.current is not None:
            self.current.exit()

        self.current = self.states[game_state]
        self.current.enter()
        return True

    def run(self):
        logger.debug('Running main loop')
        counter = 0
        while True:

            counter += 1

            # Recalc frameskip every second
            if counter > self.framerate:
                fps = self.clock.get_fps()
                #logger.debug("FPS: {}, FrameSkip: {}".format(self.current.fps(), self.current.frameSkip))
                pygame.display.set_caption("FPS: {}, FrameSkip: {}".format(fps, self.frameSkip))
                if self.frameskipEnabled:
                    if 120 * fps / 100 < self.framerate:
                        self.frameSkip += 1
                        self.frameSkipCount = 0
                    # If we have a frameskip and we are "almost" at full speed
                    if self.frameSkip > 0 and 103 * fps / 100 > self.framerate:
                        self.frameSkip -= 1
                        self.frameSkipCount = 0
                counter = 0

            new_state = self.current.tick(pygame.event.get())
            # If not frame skipping and no new state transition
            if new_state is None:
                draw = False
                if self.frameSkip > 0:
                    self.frameSkipCount += 1
                    if self.frameSkipCount > self.frameSkip:
                        self.frameSkipCount = 0
                        draw = True
                else:
                    draw = True

                if draw:
                    new_state = self.render()

            if new_state is not None:
                logger.debug('Got new state: {}'.format(new_state))
                if self.switch(new_state) is False:
                    return

            self.clock.tick(self.framerate)

            # Nothing more to do, this is the basic loop

    def getRenderer(self):
        return self.renderer

    def render(self, force=False):
        self.renderer.beginDraw()
        res = self.current.render()
        self.renderer.endDraw()
        return res

    def quit(self):
        pygame.font.quit()
        pygame.mixer.quit()
        self.renderer.quit()
