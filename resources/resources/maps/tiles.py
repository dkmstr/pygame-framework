# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import logging

logger = logging.getLogger(__name__)


######################
# Tile               #
######################
class Tile(object):
    def __init__(self, tileSet, tileId, surface, properties={}):
        self._tileSet = tileSet
        self._id = tileId
        self._orig_surface = self._surface = surface
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
            self.animation_orig_delay = self.animation_delay = int(self.properties.get('delay', '1'))
            self.animation_state = 0
            logger.debug('Added animation for tile {}: {}'.format(self._id, self.animation))
        else:
            self.animated = False
            self.animation = None
            self.animation_state = None

    def update(self):
        if self.animated is False:
            return
        self.animation_delay -= 1
        if self.animation_delay > 0:
            return
        self.animation_delay = self.animation_orig_delay
        if self.animation_state >= len(self.animation):
            self.animation_state = 0
            self.resetImage()
        else:
            self._surface = self._tileSet.getTile(self.animation[self.animation_state]).getImage()
            self.animation_state += 1

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName)

    # This x,y coordinates are screen coordinates
    # TileArray, Platform, etc.. converts coordinates of objects acordly beforw invoking it
    def draw(self, toSurface, x, y):
        if self._surface is not None:
            toSurface.blit(self._surface, (x, y))

    def getImage(self):
        return self._surface

    def setImage(self, surface):
        self._surface = surface

    def resetImage(self):
        self._surface = self._orig_surface

    def id(self):
        return self._id

    def getTileSet(self):
        return self._tileSet

    def __unicode__(self):
        return 'Tile {} ({}x{}) ({})'.format(self._id, self._surface.get_width(), self._surface.get_height(), self.properties)
