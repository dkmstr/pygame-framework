# -*- coding: utf-8 -*-

import typing

import pygame
from OpenGL import GL as gl
from math import pow, floor, log, ceil

from .renderer import Renderer
from .renderer import Image

WRAP = 0
FILTER = 1
MIPMAP = 2

# Lots of fragments from https://github.com/RyanHope/PyGL2D


def closest_power_of_two(x: float) -> float:
    return pow(2, floor((log(x) / log(2.0)) + 0.5))


def next_power_of_two(x: float) -> float:
    return pow(2, ceil((log(x) / log(2.0))))


def previous_power_of_two(x: float) -> float:
    return pow(2, floor((log(x) / log(2.0))))


def wanted_size(texSize: float, x_current: float) -> float:
    x_wanted = next_power_of_two(x_current)
    if x_wanted > texSize:
        x_wanted = texSize
    return x_wanted


def resize(image: pygame.surface.Surface, texSize: float) -> pygame.surface.Surface:
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


def surfaceToTexture(surface: pygame.surface.Surface) -> typing.Any:
    texture = gl.glGenTextures(1)

    textureData = pygame.image.tostring(surface, "RGBA", True)

    width = surface.get_width()
    height = surface.get_height()

    texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGBA,
        width,
        height,
        0,
        gl.GL_RGBA,
        gl.GL_UNSIGNED_BYTE,
        textureData,
    )

    return texture


class ImageGL(Image):
    texture: typing.Any
    rotation: float
    scalar: float
    color: typing.List[float]
    ox: float
    oy: float
    width: int
    height: int
    dl: typing.Optional[typing.List[typing.Any]]

    def __init__(self):
        self.surface = None
        self.texture = None
        self.rotation = 0
        self.scalar = 1.0
        self.color = [1.0, 1.0, 1.0, 1.0]
        self.ox = self.oy = 0.0
        self.width = self.height = 0
        self.dl = None
        self.texture = None

    def __del__(self) -> None:
        if self.texture is not None:
            gl.glDeleteTextures(self.texture)
            self.texture = None
        if self.dl is not None:
            gl.glDeleteLists(self.dl, 1)

    def _initTexture(self) -> None:
        if self.texture:
            gl.glDeleteTextures(self.texture)
            self.texture = None

        if self.dl:
            gl.glDeleteLists(self.dl, 1)
            self.dl = None

        if not self.surface:
            return

        texSize = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)

        oldH = self.surface.get_height()
        oldW = self.surface.get_width()
        image2 = resize(self.surface, texSize)
        newH = image2.get_height()
        newW = image2.get_width()
        fracH = oldH / float(newH)
        fracW = oldW / float(newW)

        self.width, self.height = self.surface.get_size()

        # convert to GL texture
        self.texture = surfaceToTexture(image2)

        # image mods
        self.rotation = 0.0
        self.scalar = 1.0
        self.color = [1.0, 1.0, 1.0, 1.0]
        self.ox, self.oy = self.getWidth() / 2.0, self.getHeight() / 2.0

        # crazy gl stuff :)
        self.dl = gl.glGenLists(1)
        gl.glNewList(self.dl, gl.GL_COMPILE)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glBegin(gl.GL_QUADS)

        gl.glTexCoord2f(0, 1)
        gl.glVertex3f(-self.width / 2.0, -self.height / 2.0, 0)
        gl.glTexCoord2f(fracW, 1)
        gl.glVertex3f(self.width / 2.0, -self.height / 2.0, 0)
        gl.glTexCoord2f(fracW, 1 - fracH)
        gl.glVertex3f(self.width / 2.0, self.height / 2.0, 0)
        gl.glTexCoord2f(0, 1 - fracH)
        gl.glVertex3f(-self.width / 2.0, self.height / 2.0, 0)

        gl.glEnd()
        gl.glEndList()

    def load(self, path: str) -> None:
        self.surface = pygame.image.load(path).convert_alpha()
        self._initTexture()

    def create(self, width: int, height: int) -> None:
        self.surface = pygame.Surface(
            (width, height), flags=pygame.SRCALPHA | pygame.HWSURFACE, depth=32
        )
        self._initTexture()

    def fromSurface(self, surface: pygame.surface.Surface) -> None:
        self.surface = surface
        self._initTexture()

    def copy(self) -> 'ImageGL':
        img = ImageGL()
        if not self.surface:
            return img
        img.surface = self.surface.copy()
        img._initTexture()
        return img

    def scale(self, width: int, height: int) -> 'ImageGL':
        img = ImageGL()
        if not self.surface:
            return img
        img.surface = pygame.transform.smoothscale(
            self.surface, (width, height)
        ).convert_alpha()
        img._initTexture()
        return img

    def blit(
        self,
        srcImage: Image,
        position: typing.Optional[typing.Tuple[int, int]] = None,
        area: typing.Optional[pygame.Rect] = None,
        alpha: int = 255,
    ) -> None:
        if not self.surface or not srcImage.surface:
            return

        if position is None:
            position = (0, 0)

        if alpha != 255:  # Add transparency if required
            surface = srcImage.surface.copy()
            surface.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        else:
            surface = srcImage.surface

        self.surface.blit(surface, position, area)
        self._initTexture()

    def draw(
        self, position: typing.Tuple[typing.Union[float, int], typing.Union[float, int]]
    ) -> None:
        # glPushMatrix()
        # glLoadIdentity()
        gl.glTranslatef(position[0] + self.ox, position[1] + self.oy, 0)
        # glTranslatef(position[0], position[1], 0)
        # glColor4f(*self.color)
        # glRotatef(self.rotation, 0.0, 0.0, 1.0)
        # glScalef(self.scalar, self.scalar, self.scalar)
        gl.glCallList(self.dl)
        gl.glTranslatef(-position[0] - self.ox, -position[1] - self.oy, 0)
        # glTranslatef(-position[0], -position[1], 0)
        # glPopMatrix()

    def fill(self, color: typing.Tuple) -> None:
        # self.surface.fill(color)
        pass

    def flip(
        self, flipX: bool = False, flipY: bool = False, rotate: bool = False
    ) -> 'ImageGL':
        img = ImageGL()
        if not self.surface:
            return img
        if rotate:
            surface = pygame.transform.rotate(self.surface, 90)
        else:
            surface = self.surface
        img.surface = pygame.transform.flip(surface, flipX, flipY)
        img._initTexture()
        return img

    def subimage(self, rect: pygame.Rect) -> 'ImageGL':
        img = ImageGL()
        if not self.surface:
            return img

        img.surface = self.surface.subsurface(rect)
        img._initTexture()
        return img

    def getSize(self) -> typing.Tuple[int, int]:
        return (self.width, self.height)

    def getWidth(self) -> int:
        return self.width

    def getHeight(self) -> int:
        return self.height


class RendererGL(Renderer):
    def init(self) -> None:
        flags = pygame.DOUBLEBUF | pygame.OPENGL
        if self.fullScreen:
            flags |= pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(self.resolution, flags, self.depth)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_MODULATE)
        gl.glEnable(gl.GL_TEXTURE_2D)

        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        gl.glClearDepth(1.0)
        # glEnable(GL_DEPTH_TEST)
        gl.glEnable(gl.GL_ALPHA_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        # glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        gl.glAlphaFunc(gl.GL_NOTEQUAL, 0.0)

    def quit(self) -> None:
        pygame.quit()

    def blit(self, image, position=None, area=None, alpha=255) -> None:
        image.draw(position)

    def beginDraw(self) -> None:
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)  # type: ignore
        gl.glLoadIdentity()

        # enable 2d
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(0, self.resolution[0], self.resolution[1], 0, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

    def endDraw(self) -> None:
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPopMatrix()

        pygame.display.flip()

    def getSize(self) -> typing.Tuple[int, int]:
        return self.resolution

    def getWidth(self) -> int:
        return self.resolution[0]

    def getHeight(self) -> int:
        return self.resolution[1]

    def image(self, width: int, height: int) -> 'ImageGL':
        img = ImageGL()
        img.create(width, height)
        return img

    def imageFromFile(self, path: str) -> 'ImageGL':
        img = ImageGL()
        img.load(path)
        return img

    def imageFromSurface(self, surface: pygame.Surface) -> 'ImageGL':
        img = ImageGL()
        img.fromSurface(surface)
        return img
