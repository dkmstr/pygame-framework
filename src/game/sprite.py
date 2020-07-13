from __future__ import unicode_literals


import pygame
import logging

logger = logging.getLogger(__name__)


class Sprite(object):

    def __init__(self, map, x, y, width, height, images=None, delay=None):
        self.map = map
        self.rect = pygame.Rect(x, y, width, height)

        if images is None:

            self.images = [pygame.Surface((width, height))]
            self.images[0].fill(pygame.Color(0xFF0000))
        else:
            self.images = [i.copy() for i in images]

        self.currentImage = 0

    def draw(self, toSurface):
        '''
        x & y are "screen" coordinates
        '''
        toSurface.draw(self.images[self.currentImage], self.rect)

    def update(self):
        pass
