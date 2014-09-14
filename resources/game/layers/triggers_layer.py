# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame

from game import paths
from game.util import loadProperties
from game.layers.layer import Layer

import logging

logger = logging.getLogger(__name__)


class TriggersLayer(Layer):
    LAYER_TYPE = 'triggers'

    def __init__(self, parentMap=None, layerType=None, properties=None):
        Layer.__init__(self, parentMap, layerType, properties)
        self.width = self.height = 0

    def load(self, node):
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])

        self.setProperties(loadProperties(node.find('properties')))

        associatedLayerName = self.properties.get('layer', None)
        self.associatedLayerName = self.parentMap.getLayer(associatedLayerName)

        logger.debug('Loading triggers layer {}'.format(self.name))
        
    def onDraw(self, toSurface, rect):
        pass

    def onUpdate(self):
        pass

    def getCollisions(self, rect):
        return []

    def getObject(self, objecName):
        return None

    def __iter__(self):
        for obj in self.platforms:
            yield obj

    def __unicode__(self):
        return 'Dinamyc Layer'
