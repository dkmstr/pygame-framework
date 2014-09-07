# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging
from game.util import checkTrue

logger = logging.getLogger(__name__)

class GraphicObject(object):
    def __init__(self, rect, properties):
        self.properties = None
        self.rect = rect if rect is not None else pygame.Rect(0, 0, 0, 0)
        self.setProperties(properties)

    def updateAttributes(self):
        '''
        Updates attributes of the object because properties was set
        '''
        # Possible attributes
        self.collission = checkTrue(self.getProperty('collission', 'False'))
        self.blocks = checkTrue(self.getProperty('blocks', 'True'))
        self.ladder = checkTrue(self.getProperty('ladder', 'False'))
        self.lethal = checkTrue(self.getProperty('lethal', 'False'))
    
    def setProperties(self, properties):
        self.properties = properties
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

    def hasProperty(self, prop):
        return prop in self.properties

    def collide(self, rect):
        '''
        By default do not collides :-)
        '''
        return False
    
    # Draw is invoked with three parameters:
    # toSurface: Surface where to draw
    # x, y: Relative position of the surface. This means that if a surface, is, for example, at 100, 100
    # we will have to translate blitting to X, y
    def draw(self, toSurface, x, y):
        pass

    def update(self):
        pass

    