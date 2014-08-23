# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pygame
from pygame.locals import *


class GameState(object):
    framerate = 60
    name = None

    def __init__(self, name):
        self.name = name
        self.controller = None
        self.clock = pygame.time.Clock()
        self.events = 0
        self.frames = 0
        self.rendered_frames = 0
        self.max_frame_time = int(1000.0 / self.framerate)

    def fps(self):
        return self.clock.get_fps()

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
        new_state = None

        for event in events:
            new_state = self.event(event)
            if new_state is not None:
                break

        # Executes game logic
        if new_state is None:
            new_state = self.frame()

        # Executes rendering
        if new_state is None:
            new_state = self.render()

        self.clock.tick(self.framerate)

        return new_state

    def event(self, ev):
        '''
        Invoked to process events (key down, mouse move, etc...)
        '''
        self.events += 1

        if ev.type == QUIT:
            return GameControl.EXIT_GAMESTATE

        if ev.type == KEYDOWN:
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
        print "Base on_init called!!!"

    def on_enter(self):
        print "Base on_enter called!!!"

    def on_exit(self):
        print "Base on_exit called!!!"

    def on_keydown(self, key):
        print "Base on_keydown called!!!"

    def on_keyup(self, key):
        print "Base on_keyup called!!!"

    def on_frame(self, event):
        print "Base on_frame called!!!"

    def on_render(self):
        print "Base on_render called!!!"


class GameControl(object):
    EXIT_GAMESTATE = 'EXIT_GAME'

    def __init__(self):
        self._states = {}
        self._current = None
        pygame.init()

    def add(self, state):
        state.controller = self
        state.init()

        self._states[state.name] = state
        if self._current is None:
            self.switch(state.name)

    def switch(self, game_state):
        if game_state not in self._states or game_state == GameControl.EXIT_GAMESTATE:
            return False

        if self._current is not None:
            self._current.exit()

        self._current = self._states[game_state]
        self._current.enter()
        return True

    def run(self):
        screen = pygame.display.set_mode((640, 480), pygame.DOUBLEBUF | pygame.HWSURFACE)

        while True:
            print ">> Executing game loop"
            new_state = self._current.tick(pygame.event.get())
            if new_state is not None:
                print 'Got new state: {}'.format(new_state)
                if self.switch(new_state) is False:
                    return
            # Nothing more to do, this is the basic loop
