# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
from game.util import classProperty

import logging

logger = logging.getLogger(__name__)

# Global tiles images caching
# Tiles images do not gets modified, so cachin them to no load
# again and again for each map is nice...
class TilesImageCache(object):
    _cache = None
    
    def __init__(self):
        self.images = {}
    
    @classProperty
    def cache(cls):
        if cls._cache is None:
            cls._cache = TilesImageCache()
        return cls._cache
    
    def load(self, imagePath):
        if self.images.get(imagePath) is not None:
            return self.images[imagePath]
        
        image = pygame.image.load(imagePath)
        image = image.convert_alpha()
        self.images[imagePath] = image
        
        return image
        
    