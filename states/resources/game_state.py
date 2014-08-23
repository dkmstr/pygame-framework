# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pygame


class GameState(object):
    framerate = 60
    name = None

    def __init__(self):
        self.controller = None
        self.max_frame_time = 1000.0 / float(self.framerate)

    def on_init(self):
        pass

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def on_event(self, event):
        '''
        Receives a pygame event
        '''
        return GameControl.EXIT_GAMESTATE

    def on_render(self):
        pass


class GameControl(object):
    EXIT_GAMESTATE = 'EXIT_GAME'

    def __init__(self):
        self._states = {}
        self._current = None
        self._requested_fps = 60
        self._clock = pygame.time.Clock()
        pygame.init()

    def add(self, state):
        state.controller = self
        state.on_init()

        self._states[state.name] = state
        if self._current is None:
            self.switch(state.name)

    def switch(self, game_state):
        if game_state not in self._states or game_state == GameControl.EXIT_GAMESTATE:
            return False
        self._current = self._states[game_state]
        self._current.on_enter()
        return True

    def run(self):
        if self._current is None:
            self._current = self._states

        frames = 0
        while True:
            for event in pygame.event.get():
                new_state = self._current.on_event(event)
                if new_state != '':
                    if self.switch(new_state) is False:  # End of GameControl loop
                        return

            self.on_render()
            frames += 1

            self.tick(self._current.framerate)
