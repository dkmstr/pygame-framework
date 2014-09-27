# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
from game.renderer.renderer import Renderer
from game.renderer.renderer import Image


class Image2D(Image):
    def __init__(self):
        self.surface = None

    def load(self, path):
        self.surface = pygame.image.load(path).convert_alpha()

    def create(self, width, height):
        self.surface = pygame.Surface((width, height), flags=pygame.SRCALPHA|pygame.HWSURFACE)

    def fromSurface(self, surface):
        self.surface = surface

    def copy(self):
        img = Image2D()
        img.surface = self.surface.copy()
        return img

    def scale(self, width, height):
        img = Image2D()
        img.surface = pygame.transform.smoothscale(self.surface, (width, height)).convert_alpha()
        return img

    def blit(self, srcImage, position=None, area=None, alpha=255):
        if position is None:
            position = (0,0)

        if alpha != 255:  # Add transparency if required
            surface = srcImage.surface.copy()
            surface.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        else:
            surface = srcImage.surface

        self.surface.blit(surface, position, area)

    def fill(self, color):
        self.surface.fill(color)

    def flip(self, flipX=False, flipY=False, rotate=False):
        if rotate:
            surface = pygame.transform.rotate(self.surface, 90)
        else:
            surface = self.surface
        img = Image2D()
        img.surface = pygame.transform.flip(surface, flipX, flipY)
        return img

    def subimage(self, rect):
        img = Image2D()
        img.surface = self.surface.subsurface(rect)
        return img

    def getSize(self):
        return self.surface.get_size()

    def getWidth(self):
        return self.surface.get_width()

    def getHeight(self):
        return self.surface.get_height()


class Renderer2D(Renderer):
    # Static singleton to renderer
    renderer = None

    def init(self):
        self.screen = pygame.display.set_mode(self.resolution, pygame.DOUBLEBUF|pygame.HWSURFACE, self.depth)

    def quit(self):
        pygame.quit()

    def blit(self, image, position=None, area=None, alpha=255):
        if position is None:
            position = (0,0)

        if alpha != 255:  # Add transparency if required
            image = image.copy()
            image.surface.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

        self.screen.blit(image.surface, position, area)

    def beginDraw(self):
        pass

    def endDraw(self):
        pygame.display.flip()

    def getSize(self):
        return self.resolution

    def getWidth(self):
        return self.resolution[0]

    def getHeight(self):
        return self.resolution[1]

    def image(self, width, height):
        img = Image2D()
        img.create(width, height)
        return img

    def imageFromFile(self, path):
        img = Image2D()
        img.load(path)
        return img

    def fromSurface(self, surface):
        img = Image2D()
        img.surface = surface
        return img
