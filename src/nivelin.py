#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import tempfile
import os
import typing

# Early logger configuration, before imports so we can use logger everywhere
logging.basicConfig(
    filename=os.path.join(tempfile.gettempdir(), 'log.log'),
    filemode='w',
    format='%(levelname)s %(asctime)s %(module)s %(funcName)s %(lineno)d %(message)s',
    level=logging.DEBUG,
)

# Main imports
import pygame
from pygame import constants as const
from player import Player
from items import *
import game
from game.actors import actorsFactory
from game.sound.sound import SoundsStore
from game.hud import ScoreFilesHud
from game.renderer import Renderer2D
from game.renderer import RendererGL

WIDTH = 1280
HEIGHT = 960
FULLSCREEN = False
RENDERER = Renderer2D

BASE_SPEED = 8


class GameTest(game.game_state.GameState):
    store: SoundsStore
    maps: typing.Optional[game.maps.Maps]
    bg_speed: int
    pressKey: typing.Dict[typing.Any, typing.Callable[[Player], None]]
    releaseKey: typing.Dict[typing.Any, typing.Callable[[Player], None]]
    map: typing.Optional[game.maps.Maps]

    def __init__(self, name):
        super(GameTest, self).__init__(name)

        self.bg_speed = 0

        self.store = SoundsStore.store  # type: ignore

        self.map = None
        self.pressKey = {
            const.K_RIGHT: Player.goRight,
            const.K_LEFT: Player.goLeft,
            const.K_DOWN: Player.goDown,
            const.K_UP: Player.goUp,
            const.K_SPACE: Player.jump,
        }
        self.releaseKey = {
            const.K_RIGHT: Player.stopRight,
            const.K_LEFT: Player.stopLeft,
            const.K_DOWN: Player.stopDown,
            const.K_UP: Player.stopUp,
            const.K_SPACE: Player.stopJump,
        }

    def on_init(self):
        self.maps = game.maps.Maps(self.controller)
        # self.maps.add('level0', 'data/maps/kenney/level-test-1.tmx')
        self.maps.add('level0', 'data/maps/kenney/level-test-1.tmx')
        # Register actors types
        actorsFactory.registerType('Player', Player)
        # SoundsStore.store.storeMusicFile('level0', 'journey_3.ogg', volume=0.5)
        self.store.storeMusicFile('level0', 'Rose Flats.ogg', volume=0.1)  

        # self.images.addImage('bck1', 'data/images/far-background.png')
        # self.images.addImage('bck2', 'data/images/near-background.png')
        # self.images.load(self.controller.screen)

        # self.maps.add('level0', 'data/maps/other.tmx')
        self.maps.load()

        self.map = self.maps.get('level0')
        self.player = list(self.map.getActors('Player'))[0]
        self.map.addHudElement(  
            ScoreFilesHud(self.player, 'data/images/numbers/hud_*.png', 8, 5, 5)
        )

        # self.bg.add_surface(self.images.get('bck1'), 5)
        # self.bg.add_surface(self.images.get('bck2'), 3)

    def on_enter(self):
        level0 = self.store.get('level0')
        if level0:
            level0.play()

    def on_exit(self):
        pygame.mixer.music.stop()

    def on_keydown(self, key):
        fnc = self.pressKey.get(key)
        if fnc is not None:
            fnc(self.player)

        return None

    def on_keyup(self, key):
        if key == const.K_q:
            return game.game_state.GameControl.EXIT_GAMESTATE

        # if key == K_n:
        #    return 'state1'

        fnc = self.releaseKey.get(key)
        if fnc is not None:
            fnc(self.player)

        return None

    def on_frame(self):
        # self.bg.scroll(self.bg_speed)
        self.map.update()  # type: ignore
        # self.player.move(self.x_speed, self.y_speed)

        self.player.updateMapDisplayPosition(self.controller.renderer)  # type: ignore
        return None

    def on_render(self):
        # self.bg.draw(self.controller.screen)
        self.map.draw(self.controller.renderer)  # type: ignore
        # self.player.draw(self.controller.screen)
        return None


os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

# Set defaults sound settings before initializing pygame
pygame.mixer.pre_init(44100, -16, 2, 1024)

gc = game.game_state.GameControl(
    WIDTH,
    HEIGHT,
    framerate=50,
    enableFrameSkip=True,
    fullScreen=FULLSCREEN,
    renderer=RENDERER,
)

gc.add(GameTest('state0'))

import cProfile

cProfile.run('gc.run()', os.path.join(tempfile.gettempdir(), 'test.stats'))
# gc.run()

gc.quit()
