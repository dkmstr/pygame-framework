# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging
from game.util import checkTrue

logger = logging.getLogger(__name__)

class GraphicObject(object):
    def __init__(self, properties):
        self.properties = None
        self.setProperties(properties)

    def updateAttributes(self):
        pass
    
    def setProperties(self, properties):
        self.properties = properties
        self.updateAttributes()

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName)

    # Draw is invoked with three parameters:
    # toSurface: Surface where to draw
    # x, y: Relative position of the surface. This means that if a surface, is, for example, at 100, 100
    # we will have to translate blitting to X, y
    def draw(self, toSurface, x, y):
        pass

    