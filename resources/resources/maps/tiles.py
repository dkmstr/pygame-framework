# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import logging

logger = logging.getLogger(__name__)


######################
# Tile               #
######################
class Tile(object):
    def __init__(self, tileSet, tileId, surface, properties={}):
        self.tileSet = tileSet
        self.tileId = tileId
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

    def update(self):
        if self.animated is False:
            return
        self.animationDelay -= 1
        if self.animationDelay > 0:
            return
        self.animationDelay = self.animationOriginalDelay
        if self.animationState >= len(self.animation):
            self.animationState = 0
            self.resetImage()
        else:
            self.surface = self.tileSet.getTile(self.animation[self.animationState]).getImage()
            self.animationState += 1

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName)

    # This x,y coordinates are screen coordinates
    # TileArray, Platform, etc.. converts coordinates of objects acordly beforw invoking it
    def draw(self, toSurface, x, y):
        if self.surface is not None:
            toSurface.blit(self.surface, (x, y))

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

    def __unicode__(self):
        return 'Tile {} ({}x{}) ({})'.format(self.tileId, self.surface.get_width(), self.surface.get_height(), self.properties)
