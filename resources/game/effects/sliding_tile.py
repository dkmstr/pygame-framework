# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
from game.util import resource_path
from game.effects import Effect
from game import dialog

import logging

logger = logging.getLogger(__name__)

NUMBER_SIZE = 32

class SlidingTileEffect(Effect):

    numbersImage = None
    numbers = None

    # TODO: Add support for multiple tiles sliding
    def __init__(self, layer, rect, ticks=50, horizontalSliding=True):
        Effect.__init__(self, rect)
        self.layer = layer
        tile = layer.getObjectAt(rect.x, rect.y)
        self.image = tile.getImage()
        self.pos = 0
        self.width = tile.getImage().get_width()
        self.height = tile.getImage().get_height()
        self.maxPos = self.width if horizontalSliding else self.height
        self.step = (self.maxPos << 12) / ticks
        self.horizontalSliding = horizontalSliding

    def update(self):
        if self.pos == 0:
            self.layer.removeObjectAt(self.rect.x, self.rect.y)
        self.pos += self.step
        if self.pos>>12 >= self.maxPos:
            # Remove tile
            return True
        return False

    def draw(self, renderer, rect):
        # Apply transparency to image
        pos, width, height = self.pos>>12, self.width, self.height
        area = (pos, 0, width - pos, height) if self.horizontalSliding else (0, pos, width, height - pos)
        renderer.blit(self.image, (self.rect.x-rect.x, self.rect.y-rect.y), area)
