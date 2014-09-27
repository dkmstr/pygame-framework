# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging
from game.util import checkTrue

from game.interfaces import Collidable
from game.interfaces import Drawable

logger = logging.getLogger(__name__)

class GraphicObject(Collidable, Drawable):
    def __init__(self, parent, rect, properties=None):
        self.parent = parent
        self.properties = None
        self.rect = rect if rect is not None else pygame.Rect(0, 0, 0, 0)
        # Attributes defaults
        self.blocks = self.name = self.collission = self.objType = None
        self.setProperties(properties)

    def updateAttributes(self):
        '''
        Updates attributes of the object because properties was set
        '''
        # Possible attributes
        self.collission = checkTrue(self.getProperty('collission', 'False'))
        self.blocks = checkTrue(self.getProperty('blocks', 'True'))
        self.objType = self.getProperty('type')
        self.name = self.getProperty('name')

        # Ladder and collectables do not blocks
        if self.objType in ('ladder', 'collectable'):
            self.blocks = False

    def setProperties(self, properties):
        self.properties = properties if properties is not None else {}
        self.updateAttributes()

    def setProperty(self, prop, value):
        self.properties[prop] = value

    def getProperty(self, propertyName, default=None):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName, default)

    def getRect(self):
        return self.rect

    def getColRect(self):
        return self.rect

    def hasProperty(self, prop):
        return prop in self.properties

    def isA(self, objType):
        '''
        returns True if the object if of the specified type
        '''
        return self.objType == objType

    def collide(self, rect):
        '''
        By default do not collides :-)
        '''
        return False

    def positionChanged(self):
        '''
        By default, does nothing
        '''
        logger.debug('Position changed invoked for {}'.format(unicode(self)))

    # Draw is invoked with three parameters:
    # Renderer: rendereable wher to draw
    # x, y: Relative position of the surface. This means that if a surface, is,
    # for example, at 100, 100
    # we will have to translate blitting to X, y
    def draw(self, renderer, rect):
        pass

    def update(self):
        pass

