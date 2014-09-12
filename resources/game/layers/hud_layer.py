# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from game.layers.layer import Layer

import logging

logger = logging.getLogger(__name__)

class HudLayer(Layer):
    LAYER_TYPE = 'hud'

    def __init__(self, parentMap=None, layerType=None, properties=None):
        Layer.__init__(self, parentMap, layerType, properties)
        
        self.hudElementsList = []
        
    def onUpdate(self):
        for hudElement in self.hudElementsList:
            hudElement.update()
        
    def onDraw(self, toSurface, rect):
        for hudElement in self.hudElementsList:
            hudElement.draw(toSurface)
        
    def addElement(self, hudElement):
        self.hudElementsList.append(hudElement)