# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging

logger = logging.getLogger(__name__)


class ObjectWithPath(object):
    def __init__(self, parentLayer, origX, origY, width, height, path, tiles, sticky):
        self.parentLayer = parentLayer
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
            yy = 0
            for t in row:
                size = t.getSize()
                t.draw(toSurface, xx, y)  # tile drawing is in screen coordinates, that is what we have on x & y
                xx += size[0]
                if size[1] > yy:
                    yy = size[1]
            y += yy

    def update(self):
        self.rect.left, self.rect.top = self.path.iterate()

    def getRect(self):
        return self.rect

    def collide(self, rect):
        return self.rect.colliderect(rect)
