# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging
from game.util import checkTrue

logger = logging.getLogger(__name__)


class ObjectWithPath(object):
    def __init__(self, parentLayer, origX, origY, width, height, tiles, properties):
        self.parentLayer = parentLayer
        self.rect = pygame.Rect(origX, origY, width, height)
        self.path = None
        self.tiles = tiles
        self.sticky = False
        self.properties = {}
        self.setProperties(properties)

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
        x, y = self.rect.left, self.rect.top
        self.path.save()  # Keeps a copy before iterating, so if we collide we can return back
        self.rect.left, self.rect.top = self.path.iterate()
        xOffset, yOffset = self.rect.left - x, self.rect.top - y

        # First we check what any actor collided moves acordly
        for c in self.parentLayer.parentMap.getActorsCollisions(self.rect):
            actorRect, actor, actorLayer = c  # actorRect is a "reference" to actor position, so modifying it will modify actor's position
            if yOffset > 0 or xOffset != 0:  # Do not move if we moved down, left or right
                self.path.restore()
                self.rect.left, self.rect.top = x, y
            else:
                # If actor collides in new position, do not move
                bottom = actor.rect.bottom
                actor.rect.bottom = self.rect.top - 1
                for c in actor.getCollisions():
                    actor.rect.bottom = bottom
                    self.path.restore()
                    self.rect.left, self.rect.top = x, y

            #if xOffset > 0:
                #actorRect.left = self.rect.right
            #elif xOffset < 0:
                #actorRect.right = self.rect.left
            #if yOffset > 0:
                #actorRect.top = self.rect.bottom
            #elif yOffset < 0:
                #actorRect.bottom = self.rect.top
        # Now, it we are "sticky", we move any actor that is "over" this item
        # Sticky is only sticky for actors that are ON this object
        if self.sticky and xOffset != 0:
            # Inflate rect at top to detect collision
            rect = pygame.Rect(self.rect.left, self.rect.top-2, self.rect.width, self.rect.height)
            for c in self.parentLayer.parentMap.getActorsCollisions(rect):
                actorRect, actor, actorLayer = c  # Rect is a "reference" to actor position, so modifying it will modify actor's position
                actor.move(xOffset, 0)

    def setProperties(self, properties):
        self.properties = properties

        self.path = self.properties.get('path', None)
        self.sticky = checkTrue(properties.get('sticky', 'True'))

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName)
    
    def hasProperty(self, prop):
        return prop in self.properties

    def getRect(self):
        return self.rect

    def collide(self, rect):
        return self.rect.colliderect(rect)
