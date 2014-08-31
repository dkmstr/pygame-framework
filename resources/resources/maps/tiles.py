# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging

logger = logging.getLogger(__name__)


######################
# Tile               #
######################
class Tile(object):
    def __init__(self, tileSet, tileId, surface, properties={}):
        self.tileSet = tileSet
        self.tileId = tileId
        if tileSet is not None:
            self.rect = pygame.Rect(0, 0, tileSet.tileWidth, tileSet.tileHeight)
        else:
            self.rect = pygame.Rect(0, 0, 0, 0)
        self.originalSurface = self.surface = surface
        self.setProperties(properties)

    def setProperties(self, properties):
        self.properties = properties
        self.updateAttributes()

    def updateAttributes(self):
        '''
        Updates attributes of the object because properties was set
        '''
        self.sticky = self.properties.get('sticky', 'False') == 'True'
        self.delay = int(self.properties.get('delay', '0'))
        # Animation ids of tiles are relative to tileset
        if self.properties.get('animation') is not None:
            self.animated = True
            self.animation = [int(i) for i in self.properties.get('animation', '-1').split(',')]
            self.animationOriginalDelay = self.animationDelay = int(self.properties.get('delay', '1'))
            self.animationState = 0
            logger.debug('Added animation for tile {}: {}'.format(self.tileId, self.animation))
        else:
            self.animated = False
            self.animation = None
            self.animationState = None
            
        if self.properties.get('height') is not None:
            self.rect.height = int(self.properties.get('height'))

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

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName)

    # This x,y coordinates are screen coordinates
    # TileArray, Platform, etc.. converts coordinates of objects acordly beforw invoking it
    def draw(self, toSurface, x, y):
        size = toSurface.get_size()
        rect = self.rect.move(x, y)
        if self.surface is not None and rect.right > 0 and rect.left < size[0] and rect.bottom > 0 and rect.top < size[1]:
            toSurface.blit(self.surface, (x, y), self.rect)

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
