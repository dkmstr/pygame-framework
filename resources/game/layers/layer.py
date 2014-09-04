# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
from game.util import checkTrue

import logging

logger = logging.getLogger(__name__)


class Layer(object):
    LAYER_TYPE = 'default'

    def __init__(self, parentMap=None, layerType=None, properties=None):
        self.name = None
        self.layerType = layerType if layerType is not None else self.LAYER_TYPE
        self.parentMap = parentMap
        self.visible = True
        self.holder = self.parallax = False
        self.parallaxFactor = ()
        self.properties = {}
        self.setProperties(properties)

    def setProperties(self, properties):
        if properties is not None:
            self.properties = properties
        # Set custom "flags" based on properties
        self.updateAttributes()

    def updateAttributes(self):
        self.visible = checkTrue(self.properties.get('visible', 'True'))
        self.holder = checkTrue(self.properties.get('holder', 'False'))
        self.actor = checkTrue(self.properties.get('actors', 'False'))
        self.parallax = checkTrue(self.properties.get('parallax', 'False'))

        self.parallaxFactor = (
            int(self.properties.get('parallax_factor_x', '100')),
            int(self.properties.get('parallax_factor_y', '100'))
        )

    def load(self, node):
        pass

    def update(self):
        self.onUpdate()

    def onUpdate(self):
        pass

    # Draw method for layer, better override "on_draw" so we can
    # calculate commono things here (as a parallax efect, for example)
    def draw(self, toSurface, x=0, y=0, width=0, height=0):
        if self.parallax is True:
            x = x * self.parallaxFactor[0] / 100
            y = y * self.parallaxFactor[1] / 100

        width = toSurface.get_width() if width <= 0 else width
        height = toSurface.get_height() if height <= 0 else height

        rect = pygame.Rect(x, y, width, height)
        
        self.onDraw(toSurface, rect)

    def onDraw(self, toSurface, rect):
        pass

    def getType(self):
        return self.layerType

    def getTileAt(self, x, y):
        x, y = y, x  # Avoid pylint unused
        return None
    
    def removeTileAt(self, x, y):
        x, y = y, x  # Avoif pylint unused
        pass

    def isVisible(self):
        return self.visible

    # Collisions
    def getCollisions(self, rect):
        del rect   # Avoid pylint unused
        return ()

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this layer
        '''
        return self.properties.get(propertyName)
