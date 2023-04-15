# -*- coding: utf-8 -*-
import os
import typing

import pygame

from . import util
from . import renderer


TRANSPARENT = 0
BLUE_STEEL = 1

_TILE_SIZE = 33


class DialogStyle:
    path: str
    image: renderer.Image
    tiles: typing.List

    def __init__(self, tileSheet: str = 'transparent-dialog.png') -> None:
        self.path = util.resource_path(os.path.join('data/images', tileSheet))
        self.image = renderer.Renderer.renderer.imageFromFile(self.path)
        self.tiles = []
        for y in range(3):
            tiles = []
            for x in range(3):
                tiles.append(
                    self.image.subimage(
                        pygame.Rect(
                            x * _TILE_SIZE, y * _TILE_SIZE, _TILE_SIZE, _TILE_SIZE
                        )
                    )
                )
            self.tiles.append(tiles)


class Dialog(object):
    __builder = None

    def __init__(self, tileSheets):
        self.tileSheets = tileSheets
        self.styles = [DialogStyle(tileSheet) for tileSheet in self.tileSheets]

    @util.classProperty
    def builder(cls):
        if cls.__builder is None:
            cls.__builder = Dialog(('transparent-dialog.png', 'blue-steel-dialog.png'))
        return cls.__builder

    def genDialog(self, width, height, style=0):

        sTiles = self.styles[style].tiles

        width = 3 if width < 99 else (width + _TILE_SIZE - 1) / _TILE_SIZE
        height = 3 if height < 99 else (height + _TILE_SIZE - 1) / _TILE_SIZE

        surface = renderer.Renderer.renderer.image(width * _TILE_SIZE, height * _TILE_SIZE)

        for y in range(0, int(height)):
            for x in range(0, int(width)):
                if y == 0:  # Left side
                    tiles = sTiles[0]
                elif y == height - 1:
                    tiles = sTiles[2]
                else:
                    tiles = sTiles[1]
                if x == 0:
                    tile = tiles[0]
                elif x == width - 1:
                    tile = tiles[2]
                else:
                    tile = tiles[1]
                surface.blit(tile, (x * _TILE_SIZE, y * _TILE_SIZE))

        return surface

    def textDialog(self, text, style):
        pass
