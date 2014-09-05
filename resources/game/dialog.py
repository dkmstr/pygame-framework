# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import os
from game.util import resource_path

TRANSPARENT = 0
BLUE_STEEL = 1

_TILE_SIZE = 33

class DialogStyle(object):
    def __init__(self, tileSheet='transparent-dialog.png'):
        self.path = resource_path(os.path.join('data/images', tileSheet))
        self.image = pygame.image.load(self.path).convert_alpha()
        self.tiles = []
        for y in xrange(3):
            tiles = []
            for x in xrange(3):
                tiles.append(self.image.subsurface(pygame.Rect(x*_TILE_SIZE, y*_TILE_SIZE, _TILE_SIZE, _TILE_SIZE)))
            self.tiles.append(tiles)

class DialogBuilder(object):
    def __init__(self, tileSheets=['transparent-dialog.png', 'blue-steel-dialog.png']):
        self.tileSheets = tileSheets
        self.styles = None
            
    def genDialog(self, width, height, style=0):
        if self.styles is None:
            self.styles = [DialogStyle(tileSheet) for tileSheet in self.tileSheets]
            
        style = self.styles[style]
            
        width = 3 if width < 99 else (width + _TILE_SIZE - 1) / _TILE_SIZE
        height = 3 if height < 99 else (height + _TILE_SIZE - 1) / _TILE_SIZE
        
        surface = pygame.Surface((width*_TILE_SIZE, height*_TILE_SIZE), pygame.SRCALPHA)
        
        for y in xrange(height):
            for x in xrange(width):
                if y == 0: # Left side
                    tiles = style.tiles[0]
                elif y == height - 1:
                    tiles = style.tiles[2]
                else:
                    tiles = style.tiles[1]
                if x == 0:
                    tile = tiles[0]
                elif x == width - 1:
                    tile = tiles[2]
                else:
                    tile = tiles[1]
                surface.blit(tile, (x*_TILE_SIZE, y*_TILE_SIZE))
        
        return surface
    
    def textDialog(self, text, style):
        pass
    
dialogBuilder = DialogBuilder()