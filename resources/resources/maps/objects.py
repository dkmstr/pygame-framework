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
        xOffset, yOffset = self.rect.left, self.rect.top
        self.rect.left, self.rect.top = self.path.iterate()
        xOffset, yOffset = self.rect.left - xOffset, self.rect.top - yOffset
        # First we check what any actor collided moves acordly
        for c in self.parentLayer.parentMap.getActorsCollisions(self.rect):
            actorRect, actor = c  # Rect is a "reference" to actor position, so modifying it will modify actor's position
            if xOffset > 0:
                actorRect.left = self.rect.right
            elif xOffset < 0:
                actorRect.right = self.rect.left
            if yOffset > 0:
                actorRect.top = self.rect.bottom
            elif yOffset < 0:
                actorRect.bottom = self.rect.top
        # Now, it we are "sticky", we move any actor that is "over" this item
        # Sticky is only sticky for actors that are ON this object
        if self.sticky and xOffset != 0:
            # Inflate rect at top to detect collision
            rect = pygame.Rect(self.rect.left, self.rect.top-2, self.rect.width, self.rect.height)
            for c in self.parentLayer.parentMap.getActorsCollisions(rect):
                actorRect, actor = c  # Rect is a "reference" to actor position, so modifying it will modify actor's position
                actor.move(xOffset, 0)

    def getRect(self):
        return self.rect

    def collide(self, rect):
        return self.rect.colliderect(rect)
