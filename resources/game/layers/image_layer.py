# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import os
from game.util import loadProperties
from game.layers.layer import Layer

import logging

logger = logging.getLogger(__name__)


class ImageLayer(Layer):
    LAYER_TYPE = 'image'

    def __init__(self, parentMap=None, layerType=None, properties=None):
        Layer.__init__(self, parentMap, layerType, properties)
        self.width = self.height = 0
        self.image_path = self.image = None
        self.cached_size = -1
        self.cached_image = None

    def load(self, node):
        logger.debug('Loading image Layer')
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])
        self.image_path = os.path.join(self.parentMap.mapPath, node.find('image').attrib['source'])
        self.image = self.getRenderer().loadImage(self.image_path)
        self.cached_size = (-1, -1)

        self.setProperties(loadProperties(node.find('properties')))
        logger.debug('Loaded image Layer {}'.format(self))

    def onDraw(self, renderer, rect):
        if rect.height != self.cached_size[1]:
            width, height = self.image.getSize()
            width = width * rect.height / height
            height = rect.height
            self.cached_size = (width, height)
            logger.debug('Rescaling image layer to {}x{}'.format(width, height))

            self.cached_image = self.image.scale(width, height)

        width, height = self.cached_size

        posX = 0
        if self.parallax:
            posX = (rect.left * self.parallaxFactor[0] / 100) % width
            renderer.blit(self.cached_image, (0, 0),
                        (posX, 0, width, height))
            renderer.blit(self.cached_image,
                        (self.cached_image.getWidth() - posX, 0),
                         (0, 0, posX, height))
        else:
            renderer.blit(self.cached_image, (0, 0))

    def __unicode__(self):
        return 'Image Layer: {}'.format(self.image_path)
