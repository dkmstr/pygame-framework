# -*- coding: utf-8 -*-

import logging

import pygame
from .effects import Effect
from .. import dialog
from ..renderer import Renderer


logger = logging.getLogger(__name__)

class FadingTextEffect(Effect):
    def __init__(self, x, y, text, fontSize=60, fontColor=(0, 0, 0), ticks=200):
        Effect.__init__(self, pygame.Rect(x, y, 0, 0))

        font = pygame.font.Font(None, fontSize)

        # First, calculate containing rect needed space
        txtLines = text.splitlines()

        for txt in txtLines:
            txtSize = font.size(txt)
            self.rect.width = txtSize[0] if self.rect.width < txtSize[0] else self.rect.width
            self.rect.height += txtSize[1]

        borderSize = 2 * (fontSize / 8)
        if borderSize < 4:
            borderSize = 4

        halfBorderSize = borderSize / 2

        self.rect.width += borderSize
        self.rect.height += borderSize

        self.textSurface = dialog.Dialog.builder.genDialog(self.rect.width, self.rect.height, dialog.TRANSPARENT)
        #self.textSurface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        #self.textSurface.fill((0, 0, 200, 255))

        #tmpSurface = self.textSurface.subsurface(pygame.Rect(halfBorderSize, halfBorderSize, self.rect.width-borderSize, self.rect.height-borderSize))
        #tmpSurface.fill((255, 255, 255, 0))
        #tmpSurface = None

        #self.textSurface = self.textSurface.convert_alpha()

        # Center speech bubble
        self.rect.top -= self.textSurface.getHeight()
        self.rect.left -= self.textSurface.getWidth() / 2

        yPos = halfBorderSize
        for txt in txtLines:
            tmpSurface = Renderer.renderer.imageFromSurface(font.render(txt, True, fontColor))
            self.textSurface.blit(tmpSurface, ((self.rect.width-tmpSurface.getWidth())/2, yPos))
            yPos += tmpSurface.getHeight()

        self.ticks = self.totalTicks = ticks

    def update(self):
        self.ticks -= 1
        if self.ticks <= 0:
            return True
        return False

    def draw(self, renderer, rect):
        if self.ticks > 100:
            alpha = 255
        else:
            alpha = 255 * self.ticks / 100
        renderer.blit(self.textSurface, (self.rect.x-rect.x, self.rect.y-rect.y), alpha=alpha)

