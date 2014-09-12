# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
from game.util import classProperty

import logging

logger = logging.getLogger(__name__)

# Global tiles images caching
# Tiles images do not gets modified, so cachin them to no load
# again and again for each map is nice...
class ImageCache(object):
    _cache = None
    
    def __init__(self):
        self.images = {}
    
    @classProperty
    def cache(cls):
        if cls._cache is None:
            cls._cache = ImageCache()
        return cls._cache
    
    def load(self, imagePath):
        if self.images.get(imagePath) is not None:
            image = self.images[imagePath]
        else:
            image = pygame.image.load(imagePath)
            self.images[imagePath] = image
        
        return image.convert_alpha()
        
    