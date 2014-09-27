# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import glob

from game.util import resource_path
from game.hud.hud_element import HudElement
from game.renderer import Renderer

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

        self.images = [Renderer.renderer.imageFromFile(f) for f in files]

        self.width = max([i.getWidth() for i in self.images])
        self.rect.width = self.width * self.digits
        self.rect.height = max([i.getHeight() for i in self.images])

        self.image = Renderer.renderer.image(self.rect.width, self.rect.height)

    def draw(self, toSurface):
        toSurface.blit(self.image, self.rect.topleft)

    def update(self):
        if self.score == self.scoreable.getScore():
            return  # No update to rect

        score = self.score = self.scoreable.getScore()
        self.image.fill((0, 0, 0, 0))  # Transparent
        pos = 0
        for digit in [(score/(10**i))%10 for i in xrange(self.digits-1,-1,-1)]:
            self.image.blit(self.images[digit], (pos, 0))
            pos += self.width

