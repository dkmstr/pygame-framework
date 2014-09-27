# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame


class Renderer(object):

    renderer = None

    def __init__(self, width=1024, height=768, depth=32):
        self.resolution = (width, height)
        self.depth = depth
        self.screen = None

        Renderer.renderer = self

        pygame.init()

    def setMode(self, width, heigth, depth=32):
        self.resolution = (width, heigth)
        self.depth = depth

    def init(self):
        self.screen = pygame.display.set_mode(self.resolution, pygame.DOUBLEBUF|pygame.HWSURFACE, self.depth)

    def quit(self):
        pygame.quit()

    def getSize(self):
        return self.resolution

    def getWidth(self):
        return self.resolution[0]

    def getHeight(self):
        return self.resolution[1]

    def blit(self, image, position=None, area=None, alpha=255):
        raise NotImplementedError('blit Method not implemented for class {}'.format(self.__class__))

    def beginDraw(self):
        raise NotImplementedError('beginDraw Method not implemented for class {}'.format(self.__class__))

    def endDraw(self):
        raise NotImplementedError('endDraw Method not implemented for class {}'.format(self.__class__))

    def image(self, width, height):
        raise NotImplementedError('createImage Method not implemented for class {}'.format(self.__class__))

    def imageFromFile(self, path):
        raise NotImplementedError('loadImage Method not implemented for class {}'.format(self.__class__))

    def imageFromSurface(self, surface):
        raise NotImplementedError('loadImage Method not implemented for class {}'.format(self.__class__))

class Image(object):
    def load(self, path):
        raise NotImplementedError('load Method not implemented for class {}'.format(self.__class__))

    def create(self, width, height):
        raise NotImplementedError('create Method not implemented for class {}'.format(self.__class__))

    def fromSurface(self, surface):
        raise NotImplementedError('fromSurface Method not implemented for class {}'.format(self.__class__))

    def copy(self):
        raise NotImplementedError('copy Method not implemented for class {}'.format(self.__class__))

    def scale(self, width, height):
        raise NotImplementedError('scale Method not implemented for class {}'.format(self.__class__))

    def blit(self, srcImage, position=None, area=None, alpha=255):
        raise NotImplementedError('blit Method not implemented for class {}'.format(self.__class__))

    def fill(self, color):
        raise NotImplementedError('fill Method not implemented for class {}'.format(self.__class__))

    def flip(self, flipX=False, flipY=False, rotate=False):
        raise NotImplementedError('flip Method not implemented for class {}'.format(self.__class__))

    def subimage(self, rect):
        raise NotImplementedError('subimage Method not implemented for class {}'.format(self.__class__))

    def getSize(self):
        raise NotImplementedError('getSize Method not implemented for class {}'.format(self.__class__))

    def getWidth(self):
        raise NotImplementedError('getWidth Method not implemented for class {}'.format(self.__class__))

    def getHeight(self):
        raise NotImplementedError('getHeight Method not implemented for class {}'.format(self.__class__))


