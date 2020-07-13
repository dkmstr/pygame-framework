# -*- coding: utf-8 -*-

import pygame
import logging
from game.util import checkTrue
from game.objects import GraphicObject

logger = logging.getLogger(__name__)


######################
# Tile               #
######################
class Tile(GraphicObject):
    def __init__(self, tileSet, tileId, image, properties={}):
        GraphicObject.__init__(self, tileSet, pygame.Rect(0, 0, tileSet.tileWidth, tileSet.tileHeight) if tileSet else None, properties)

        self.parent = tileSet
        self.tileId = tileId
        self.originalImage = self.image = image

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
            self.image = self.parent.getTile(self.animation[self.animationState-1]).getOriginalImage()
            self.animationState += 1

    # This x,y coordinates are screen coordinates
    # TileArray, Platform, etc.. converts coordinates of objects acordly beforw invoking it
    def draw(self, renderer, rect):
        size = renderer.getSize()
        renderer.blit(self.image, rect.topleft)

    def blit(self, toImage, rect):
        size = toImage.getSize()
        toImage.blit(self.image, rect.topleft)

    def getOriginalImage(self):
        return self.originalImage

    def getImage(self):
        return self.image

    def setImage(self, surface):
        self.image = surface

    def resetImage(self):
        self.image = self.originalImage

    def id(self):
        return self.tileId

    def getTileSet(self):
        return self.parent

    def getRect(self):
        return self.rect

    def getSize(self):
        return (self.rect.width, self.rect.height)

    def __unicode__(self):
        return 'Tile {} ({}x{}) ({})'.format(self.tileId, self.image.get_width(), self.image.get_height(), self.properties)
