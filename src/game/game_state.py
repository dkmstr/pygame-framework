# -*- coding: utf-8 -*-

import typing

import pygame
from pygame import locals

from game.renderer import Renderer

import logging

logger = logging.getLogger(__name__)

SCREEN_BUFFER_SIZE = (1280, 1024)


class GameState:
    name: str  # Name of this game state
    controller: typing.Optional['GameControl']  # controller for the gamestate
    total_events: int  # number of events
    total_frames: int  # Total Number of frames
    rendered_frames: int  # Number of frames rendered
    frame_skip: int
    frame_skip_count: int

    def __init__(self, name: str) -> None:
        self.name = name
        self.controller = None
        self.total_events = 0
        self.total_frames = 0
        self.rendered_frames = 0
        self.frame_skip = 0
        self.frame_skip_count = 0

    def init(self) -> None:
        self.on_init()

    def enter(self) -> None:  # Activates the state
        self.on_enter()

    def exit(self) -> None:  # Exit form the state
        return self.on_exit()

    def tick(self, events: typing.List[pygame.event.Event]) -> typing.Optional[str]:
        '''
        Processes one game 'tick'
        '''
        newState: typing.Optional[str] = None

        for event in events:
            newState = self.event(event)
            if newState:
                break

        # Executes game logic if no new game state is requested
        if not newState:
            newState = self.frame()

        return newState

    def event(self, ev: pygame.event.Event) -> typing.Optional[str]:
        '''
        Invoked to process events (key down, mouse move, etc...)
        '''
        self.total_events += 1

        if ev.type == locals.QUIT:
            return GameControl.EXIT_GAMESTATE
        elif ev.type == locals.VIDEORESIZE:
            pygame.display.set_mode(
                ev.dict['size'], locals.HWSURFACE | locals.RESIZABLE
            )

        elif ev.type == locals.KEYDOWN:
            return self.on_keydown(typing.cast(int, ev.key))
        elif ev.type == locals.KEYUP:
            return self.on_keyup(typing.cast(int, ev.key))

        return None

    def frame(self) -> typing.Optional[str]:
        '''game logic'''
        self.total_frames += 1
        self.on_frame()
        return None

    def render(self) -> typing.Optional[str]:
        self.rendered_frames += 1
        return self.on_render()

    def on_init(self) -> None:
        print("Base on_init called!!!")

    def on_enter(self) -> None:
        print("Base on_enter called!!!")

    def on_exit(self) -> None:
        print("Base on_exit called!!!")

    def on_keydown(self, key: int) -> typing.Optional[str]:
        print("Base on_keydown called!!!")
        return None

    def on_keyup(self, key: int) -> typing.Optional[str]:
        print("Base on_keyup called!!!")
        return None

    def on_frame(self) -> None:
        print("Base on_frame called!!!")

    def on_render(self) -> typing.Optional[str]:
        print("Base on_render called!!!")
        return None


class GameControl:
    EXIT_GAMESTATE = 'EXIT_GAME'
    states: typing.MutableMapping[str, GameState]
    current: typing.Optional[GameState]
    framerate: int
    frameskipEnabled: bool
    frameskip: int
    frameSkipCount: int
    clock: pygame.time.Clock
    width: int
    height: int
    renderer: Renderer

    def __init__(
        self,
        width: int,
        height: int,
        framerate: int,
        enableFrameSkip: bool = False,
        fullScreen: bool = False,
        renderer: typing.Type[Renderer] = Renderer,
    ):
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

    def add(self, state: GameState) -> None:
        state.controller = self
        state.init()

        self.states[state.name] = state
        if self.current is None:  # Switch to first state
            self.switch(state.name)

    def switch(self, game_state: str) -> bool:
        if game_state not in self.states or game_state == GameControl.EXIT_GAMESTATE:
            logger.debug('Received game_state {}. EXITING'.format(game_state))
            return False

        if self.current is not None:
            self.current.exit()

        self.current = self.states[game_state]
        self.current.enter()
        return True

    def run(self) -> None:
        if not self.current:
            return
        logger.debug('Running main loop')

        frames_counter: int = 0
        while True:

            frames_counter += 1

            # Recalc frameskip every second
            if frames_counter > self.framerate:
                fps = self.clock.get_fps()
                # logger.debug("FPS: {}, FrameSkip: {}".format(self.current.fps(), self.current.frameSkip))
                pygame.display.set_caption(
                    "FPS: {}, FrameSkip: {}".format(fps, self.frameSkip)
                )
                if self.frameskipEnabled:
                    if 120 * fps / 100 < self.framerate:
                        self.frameSkip += 1
                        self.frameSkipCount = 0
                    # If we have a frameskip and we are "almost" at full speed
                    if self.frameSkip > 0 and 103 * fps / 100 > self.framerate:
                        self.frameSkip -= 1
                        self.frameSkipCount = 0
                frames_counter = 0

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

    def getRenderer(self) -> Renderer:
        return self.renderer

    def render(self, force:bool=False) -> typing.Optional[str]:
        if not self.current:
            return None
        self.renderer.beginDraw()
        res = self.current.render()
        self.renderer.endDraw()
        return res

    def quit(self):
        pygame.font.quit()
        pygame.mixer.quit()
        self.renderer.quit()
