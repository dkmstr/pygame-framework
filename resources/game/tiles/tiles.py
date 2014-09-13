# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging
from game.util import checkTrue
from game.objects import GraphicObject

logger = logging.getLogger(__name__)


######################
# Tile               #
######################
class Tile(GraphicObject):
    def __init__(self, tileSet, tileId, surface, properties={}):
        GraphicObject.__init__(self, pygame.Rect(0, 0, tileSet.tileWidth, tileSet.tileHeight) if tileSet else None, properties)
        
        self.tileSet = tileSet
        self.tileId = tileId
        self.originalSurface = self.surface = surface

    def updateAttributes(self):
        GraphicObject.updateAttributes(self)
        '''
        Updates attributes of the object because properties was set
        '''
        self.delay = int(self.properties.get('delay', '0'))
        # Animation ids of tiles are relative to tileset
        if self.properties.get('animation') is not None:
            self.animated = True
            self.animation = [int(i) for i in self.properties.get('animation', '-1').split(',')]
            self.animationOriginalDelay = self.animationDelay = int(self.properties.get('delay', '1'))
            self.animationState = 0
        else:
            self.animated = False
            self.animation = None
            self.animationState = None

        # Optimized rect for collisions
        if self.properties.get('height') is not None:
            self.rect.height = int(self.properties.get('height'))
        if self.properties.get('width') is not None:
            self.rect.width = int(self.properties.get('width'))
        if self.properties.get('left') is not None:
            self.rect.left = int(self.properties.get('left'))
        if self.properties.get('top') is not None:
            self.rect.top = int(self.properties.get('top'))
            
    def update(self):
        if self.animated is False:
            return
        self.animationDelay -= 1
        if self.animationDelay > 0:
            return
        self.animationDelay = self.animationOriginalDelay
        if self.animationState > len(self.animation):
            self.animationState = 0
            self.resetImage()
        else:
            self.surface = self.tileSet.getTile(self.animation[self.animationState-1]).getOriginalImage()
            self.animationState += 1

    # This x,y coordinates are screen coordinates
    # TileArray, Platform, etc.. converts coordinates of objects acordly beforw invoking it
    def draw(self, toSurface, rect):
        size = toSurface.get_size()
        toSurface.blit(self.surface, rect.topleft)

    def getOriginalImage(self):
        return self.originalSurface

    def getImage(self):
        return self.surface

    def setImage(self, surface):
        self.surface = surface

    def resetImage(self):
        self.surface = self.originalSurface

    def id(self):
        return self.tileId

    def getTileSet(self):
        return self.tileSet

    def getRect(self):
        return self.rect

    def getSize(self):
        return (self.rect.width, self.rect.height)

    def __unicode__(self):
        return 'Tile {} ({}x{}) ({})'.format(self.tileId, self.surface.get_width(), self.surface.get_height(), self.properties)
