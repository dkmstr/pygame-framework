# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
from game.effects import Effect

import logging

logger = logging.getLogger(__name__)

class FadingTextEffect(Effect):
    def __init__(self, x, y, text, fontSize=60, fontColor=(0, 0, 0), ticks=200):
        # TODO: Initilalize this correctly
        Effect.__init__(self, pygame.Rect(x, y, 0, 0))
        pygame.font.init()
        font = pygame.font.Font(None, fontSize)
        self.textSurface = font.render(text, True, fontColor)
        size = self.textSurface.get_size()
        self.rect.width, self.rect.height = size[0], size[1]
        self.ticks = self.totalTicks = ticks

    def update(self):
        self.ticks -= 1
        if self.ticks == 0:
            return True
        return False
        
    def draw(self, toSurface, rect):
        image = self.textSurface.copy()
        if self.ticks > 100:
            alpha = 255
        else:
            alpha = 255 * self.ticks / 100
        image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        toSurface.blit(image, (self.rect.x-rect.x, self.rect.y-rect.y))
        
