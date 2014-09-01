# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import glob

from resources.util import resource_path

import logging

logger = logging.getLogger(__name__)


class Animation(object):
    def __init__(self, delay, startingPosition=0):
        self.images = []
        self.position = self.startingPosition = startingPosition
        self.baseDelay = self.delay = delay

    def iterate(self):
        self.delay -= 1
        if self.delay <= 0:
            self.delay = self.baseDelay
            self.position = (self.position + 1) % len(self.images)

    def reset(self):
        self.position = self.startingPosition
        self.delay = self.baseDelay

    def get(self):
        return self.images[self.position]
    
    def draw(self, toSurface, x, y, effect=None):
        image = self.images[self.position]
        if effect == 'laplacian':
            image = pygame.transform.laplacian(image)
        toSurface.blit(image, (x, y))


class FilesAnimation(Animation):
    def __init__(self, fileListPattern, delay, startingPosition=0):
        Animation.__init__(self, delay)
        files = sorted(glob.glob(resource_path(fileListPattern)))

        # Load image files
        self.images = [pygame.image.load(f).convert_alpha() for f in files]
        for i in self.images:
            i.set_alpha(0, pygame.RLEACCEL)

class FlippedAnimation(Animation):
    def __init__(self, animation):
        Animation.__init__(self, animation.baseDelay, animation.startingPosition)
        
        self.images = [pygame.transform.flip(i,True,False) for i in animation.images]
