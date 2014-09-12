# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import glob

from game.image_cache import ImageCache
from game.util import resource_path
from game.hud.hud_element import HudElement

import logging

logger = logging.getLogger(__name__)

class ScoreableMixin(object):
    def getScore(self):
        return 0

class ScoreFilesHud(HudElement):
    def __init__(self, scoreable, digitsFilesPattern, digits, x, y):
        HudElement.__init__(self, x, y)  # Width and height has te bo be calculated later
        if not isinstance(scoreable, ScoreableMixin):
            raise TypeError('{} Must include ScoreableMixin'.format(type(scoreable)))
        self.scoreable = scoreable
        self.digits = digits
        self.score = scoreable.getScore() - 1
        
        files = sorted(glob.glob(resource_path(digitsFilesPattern)))
        if len(files) != 10:
            logger.error('We need 10 files for score digigts, and file pattern got {} files instead'.format(len(files)))
            raise ValueError('We need 10 files for score digigts, and file pattern got {} files instead'.format(len(files)))
        
        self.images = [ImageCache.cache.load(f).convert_alpha() for f in files]
        
        self.width = max([i.get_width() for i in self.images])
        self.rect.width = self.width * self.digits
        self.rect.height = max([i.get_height() for i in self.images])
        
        self.surface = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)
        
    def draw(self, toSurface):
        toSurface.blit(self.surface, self.rect.topleft)
    
    def update(self):
        if self.score == self.scoreable.getScore():
            return  # No update to rect
        
        score = self.score = self.scoreable.getScore()
        self.surface.fill((0, 0, 0, 0))  # Transparent
        pos = 0
        for digit in [(score/(10**i))%10 for i in xrange(self.digits-1,-1,-1)]:
            self.surface.blit(self.images[digit], (pos, 0))
            pos += self.width
        
    