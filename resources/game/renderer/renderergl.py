# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
from OpenGL.GL import *
from math import pow, floor, log, ceil

from game.renderer.renderer import Renderer
from game.renderer.renderer import Image

WRAP = 0
FILTER = 1
MIPMAP = 2

# Lots of fragments from https://github.com/RyanHope/PyGL2D
def closest_power_of_two (x):
    return (pow(2, floor ((log (x) / log (2.0)) + 0.5)))

def next_power_of_two (x):
    return (pow(2, ceil ((log (x) / log (2.0)))))

def previous_power_of_two (x):
    return (pow(2, floor ((log (x) / log (2.0)))))

#returns closest power of 2 which is greater than x_current. Max value is texSize.
def wanted_size (texSize, x_current):
    x_wanted = next_power_of_two (x_current)
    if (x_wanted > texSize): x_wanted = texSize
    return (x_wanted)

def resize (image, texSize):
    H1 = image.get_height()
    W1 = image.get_width()
    H2 = wanted_size(texSize, H1)
    W2 = wanted_size(texSize, W1)
    if (H1 != H2) or (H2 != W2):
        dst_rect = pygame.Rect(0, 0, W2, H2)
        dest = pygame.Surface((W2, H2), 0, image)
        dest.blit(image, (0, 0), dst_rect)
        return dest
    else:
        return image


def surfaceToTexture(surface):
    texture = glGenTextures(1)

    textureData = pygame.image.tostring(surface, "RGBA", 1)

    width = surface.get_width()
    height = surface.get_height()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
                 GL_UNSIGNED_BYTE, textureData)

    return texture

class ImageGL(Image):
    def __init__(self):
        self.surface = None
        self.texture = None
        self.rotation = 0
        self.scalar = 1.0
        self.color = [1.0, 1.0, 1.0, 1.0]
        self.ox = self.oy = 0
        self.width = self.height = 0
        self.dl = None
        self.texture = None

    def __del__(self):
        if self.texture is not None:
            glDeleteTextures(self.texture)
            self.texture = None
        if self.dl is not None:
            glDeleteLists(self.dl, 1)

    def _initTexture(self):
        if self.texture is not None:
            glDeleteTextures(self.texture)
            self.texture = None
        if self.dl is not None:
            glDeleteLists(self.dl, 1)
            self.dl = None

        texSize = glGetIntegerv (GL_MAX_TEXTURE_SIZE)

        oldH = self.surface.get_height()
        oldW = self.surface.get_width()
        image2 = resize(self.surface, texSize)
        newH = image2.get_height()
        newW = image2.get_width()
        fracH = oldH / float(newH)
        fracW = oldW / float(newW)

        self.width, self.height = self.surface.get_size()

        #convert to GL texture
        self.texture = surfaceToTexture(image2)

        #image mods
        self.rotation = 0.0
        self.scalar = 1.0
        self.color = [1.0, 1.0, 1.0, 1.0]
        self.ox, self.oy = self.getWidth() / 2.0, self.getHeight() / 2.0

        #crazy gl stuff :)
        self.dl = glGenLists(1)
        glNewList(self.dl, GL_COMPILE)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)

        glTexCoord2f(0, 1); glVertex3f(-self.width / 2.0, -self.height / 2.0, 0)
        glTexCoord2f(fracW, 1); glVertex3f(self.width / 2.0, -self.height / 2.0, 0)
        glTexCoord2f(fracW, 1 - fracH); glVertex3f(self.width / 2.0, self.height / 2.0, 0)
        glTexCoord2f(0, 1 - fracH); glVertex3f(-self.width / 2.0, self.height / 2.0, 0)

        glEnd()
        glEndList()


    def load(self, path):
        self.surface = pygame.image.load(path).convert_alpha()
        self._initTexture()

    def create(self, width, height):
        self.surface = pygame.Surface((width, height), flags=pygame.SRCALPHA|pygame.HWSURFACE,depth=32)
        self._initTexture()

    def fromSurface(self, surface):
        self.surface = surface
        self._initTexture()

    def copy(self):
        img = ImageGL()
        img.surface = self.surface.copy()
        img._initTexture()
        return img

    def scale(self, width, height):
        img = ImageGL()
        img.surface = pygame.transform.smoothscale(self.surface, (width, height)).convert_alpha()
        img._initTexture()
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
        self._initTexture()

    def draw(self, position):
        #glPushMatrix()
        #glLoadIdentity()
        glTranslatef(position[0] + self.ox, position[1] + self.oy, 0)
        #glTranslatef(position[0], position[1], 0)
        #glColor4f(*self.color)
        #glRotatef(self.rotation, 0.0, 0.0, 1.0)
        #glScalef(self.scalar, self.scalar, self.scalar)
        glCallList(self.dl)
        glTranslatef(-position[0] - self.ox, -position[1] - self.oy, 0)
        #glTranslatef(-position[0], -position[1], 0)
        #glPopMatrix()


    def fill(self, color):
        #self.surface.fill(color)
        pass

    def flip(self, flipX=False, flipY=False, rotate=False):
        if rotate:
            surface = pygame.transform.rotate(self.surface, 90)
        else:
            surface = self.surface
        img = ImageGL()
        img.surface = pygame.transform.flip(surface, flipX, flipY)
        img._initTexture()
        return img

    def subimage(self, rect):
        img = ImageGL()
        img.surface = self.surface.subsurface(rect)
        img._initTexture()
        return img

    def getSize(self):
        return (self.width, self.height)

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height


class RendererGL(Renderer):
    # Static singleton to renderer
    renderer = None

    def init(self):
        flags = pygame.DOUBLEBUF|pygame.OPENGL
        if self.fullScreen:
            flags |= pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(self.resolution, flags, self.depth)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glEnable(GL_TEXTURE_2D)

        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        #glEnable(GL_DEPTH_TEST)
        glEnable(GL_ALPHA_TEST)
        glDepthFunc(GL_LEQUAL)
        #glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glAlphaFunc(GL_NOTEQUAL, 0.0)


    def quit(self):
        pygame.quit()

    def blit(self, image, position=None, area=None, alpha=255):
        image.draw(position)

    def beginDraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # enable 2d
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.resolution[0], self.resolution[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

    def endDraw(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        pygame.display.flip()

    def getSize(self):
        return self.resolution

    def getWidth(self):
        return self.resolution[0]

    def getHeight(self):
        return self.resolution[1]

    def image(self, width, height):
        img = ImageGL()
        img.create(width, height)
        return img

    def imageFromFile(self, path):
        img = ImageGL()
        img.load(path)
        return img

    def imageFromSurface(self, surface):
        img = ImageGL()
        img.fromSurface(surface)
        return img
