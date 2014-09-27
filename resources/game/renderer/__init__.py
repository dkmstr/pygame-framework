# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame

class Renderer(object):
    # Static singleton to renderer
    renderer = None

    def __init__(self, width=1024, height=768, depth=32):
        self.resolution = (width, height)
        self.depth = depth
        self.screen = None

        pygame.init()

    def setMode(self, width, heigth, depth=32):
        flags |= pygame.DOUBLEBUF | pygame.HWSURFACE
        self.resolution = (width, heigth)
        self.depth = depth

    def init(self):
        self.screen = pygame.display.set_mode(self.resolution, pygame.DOUBLEBUF|pygame.HWSURFACE, self.depth)

    def quit(self):
        pygame.quit()

    def blit(self, image, position=None, area=None):
        if position is None:
            position = (0,0)

        self.screen.blit(image, position, area)

    def update(self):
        pygame.display.flip()

    def getSize(self):
        return self.resolution

    def getWidth(self):
        return self.resolution[0]

    def getHeight(self):
        return self.resolution[1]
