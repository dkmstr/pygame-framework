# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import glob

from game.util import resource_path
from game.image_cache import ImageCache


import logging

logger = logging.getLogger(__name__)


class Animation(object):
    def __init__(self, delay, startingPosition=0):
        self.images = []
        self.position = self.startingPosition = startingPosition
        self.baseDelay = self.delay = delay
        self.associatedSounds = {}

    def associateSound(self, frame, sound):
        self.associatedSounds[frame] = sound

    def iterate(self):
        self.delay -= 1
        if self.delay <= 0:
            self.delay = self.baseDelay
            self.position = (self.position + 1) % len(self.images)
            
    def getPosition(self, inPercent=False):
        if inPercent:
            return 100 * self.position / len(self.images)
        return self.position

    def reset(self):
        self.position = self.startingPosition
        self.delay = self.baseDelay

    def get(self):
        return self.images[self.position]

    def draw(self, toSurface, rect, effect=None):
        image = self.images[self.position]
        if effect == 'laplacian':
            image = pygame.transform.laplacian(image)
        toSurface.blit(image, rect.topleft)
        
    def play(self):
        # Only play sounds on start of delays
        if self.delay == self.baseDelay:
            snd = self.associatedSounds.get(self.position)
            if snd is not None:
                snd.play()
        
    def copy(self):
        '''
        Returns a "partial copy" of this animation
        This means that we return same reference to images, but own control variables
        '''
        anim = Animation(self.baseDelay, self.startingPosition)
        anim.associatedSounds = self.associatedSounds
        anim.images = self.images


class FilesAnimation(Animation):
    def __init__(self, fileListPattern, delay, startingPosition=0):
        Animation.__init__(self, delay, startingPosition)
        files = sorted(glob.glob(resource_path(fileListPattern)))

        # Load image files
        self.images = [ImageCache.cache.load(f).convert_alpha() for f in files]
        # for i in self.images:
        #    i.set_alpha(0, pygame.RLEACCEL)

class SpriteSheetAnimation(Animation):
    def __init__(self, fileName, width, delay, startingPosition=0):
        Animation.__init__(self, delay, startingPosition)
        self.image = pygame.image.load(resource_path(fileName)).convert_alpha()
        widh, height = self.image.get_size()
        self.images = [self.image.subsurface(x, 0, width, height) for x in xrange(0, self.image.get_width(), width)]

class FlippedAnimation(Animation):
    def __init__(self, animation):
        Animation.__init__(self, animation.baseDelay, animation.startingPosition)
        self.associatedSounds = animation.associatedSounds

        self.images = [pygame.transform.flip(i, True, False) for i in animation.images]

class AnimationsStore(object):
    def __init__(self):
        self.animations = {}

    def store(self, animationName, animation):
        self.animations[animationName] = animation

    def get(self, animationName):
        return self.animations[animationName].copy()

animationStore = AnimationsStore()
    