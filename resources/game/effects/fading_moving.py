# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
from game.util import resource_path
from game.effects import Effect
from game import dialog
from game.renderer import Renderer

import logging

logger = logging.getLogger(__name__)

NUMBER_SIZE = 32

class FadingMovingValueEffect(Effect):

    numbersImage = None
    numbers = None

    def __init__(self, x, y, value, ticks=50):
        Effect.__init__(self, pygame.Rect(x, y, 0, 0))


        if FadingMovingValueEffect.numbersImage is None:
            FadingMovingValueEffect.initializeNumbers()

        value = unicode(value)
        self.image = surface = Renderer.renderer.createImage(len(value)*NUMBER_SIZE, NUMBER_SIZE)
        self.image.fill((255, 255, 255, 0))
        pos = 0
        for v in value:
            self.image.blit( FadingMovingValueEffect.numbers[v], (pos, 0))
            pos += NUMBER_SIZE

        self.ticks =  self.totalTicks = ticks

        self.rect.top -= NUMBER_SIZE
        self.rect.left -=  NUMBER_SIZE * len(value) / 2
        self.y = self.rect.top

    def update(self):
        self.ticks -= 1
        self.rect.top = self.y + 10 * self.ticks / self.totalTicks
        if self.ticks <= 0:
            return True
        return False

    def draw(self, renderer, rect):
        alpha = 255 * self.ticks / self.totalTicks

        renderer.blit(self.image, (self.rect.x-rect.x, self.rect.y-rect.y), alpha=alpha)

    @staticmethod
    def initializeNumbers():
        FadingMovingValueEffect.numbersImage = Renderer.renderer.loadImage(resource_path('data/images/numbers/numbers-sheet-32.png'))
        FadingMovingValueEffect.numbers = { unicode(i): FadingMovingValueEffect.numbersImage.subimage((i*NUMBER_SIZE, 0, NUMBER_SIZE, NUMBER_SIZE)) for i in xrange(10) }

