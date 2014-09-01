# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import os
from resources.maps.utils import loadProperties
from resources.layers.layer import Layer

import logging

logger = logging.getLogger(__name__)


class ImageLayer(Layer):
    LAYER_TYPE = 'image'

    def __init__(self, parentMap=None, layerType=None, properties=None):
        Layer.__init__(self, parentMap, layerType, properties)
        self.width = self.height = 0
        self.image_path = self.image = None
        self.cached_size = (-1, -1)
        self.cached_image = None

    def load(self, node):
        logger.debug('Loading image Layer')
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])
        self.image_path = os.path.join(self.parentMap.mapPath, node.find('image').attrib['source'])
        self.image = (pygame.image.load(self.image_path))
        self.cached_size = (-1, -1)

        self.setProperties(loadProperties(node.find('properties')))
        logger.debug('Loaded image Layer {}'.format(self))

    def onDraw(self, toSurface, rect):
        if rect.width != self.cached_size[0] or rect.height != self.cached_size[1]:
            logger.debug('Rescaling image layer to {}x{}'.format(rect.width, rect.height))
            self.cached_size = (rect.width, rect.height)
            self.cached_image = pygame.transform.scale(self.image, self.cached_size).convert()

        toSurface.blit(self.cached_image, (0, 0))

    def __unicode__(self):
        return 'Image Layer: {}'.format(self.image_path)
