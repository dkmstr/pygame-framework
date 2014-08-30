# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging

logger = logging.getLogger(__name__)


class ObjectWithPath(object):
    def __init__(self, origX, origY, width, height, path, tiles, sticky):
        self.rect = pygame.Rect(origX, origY, width, height)
        self.path = path
        self.tiles = tiles
        self.sticky = sticky

    def draw(self, toSurface, x, y):
        '''
        Draws to specied surface, to coords x, y
        '''
        rect = pygame.Rect((x, y), toSurface.get_size())
        if not rect.colliderect(self.rect):
            return
        # Translate start to screen coordinates
        x = self.rect.left - x
        y = self.rect.top - y
        for row in self.tiles:
            xx = x
            for t in row:
                t.draw(toSurface, xx, y)  # tile drawing is in screen coordinates, that is what we have on x & y
                xx += t.getTileSet().tileWidth
            y += t.getTileSet().tileHeight

    def update(self):
        self.rect.left, self.rect.top = self.path.iterate()

    def getRect(self):
        return self.rect

    def collide(self, rect):
        return self.rect.colliderect(rect)
