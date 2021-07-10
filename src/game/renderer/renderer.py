# -*- coding: utf-8 -*-
import typing

import pygame
from pygame import surface

if typing.TYPE_CHECKING:
    pass


class Image:
    surface: typing.Optional[pygame.Surface]

    def __init__(self) -> None:
        self.surface = None

    def load(self, path: str) -> None:
        raise NotImplementedError(
            'load Method not implemented for class {}'.format(self.__class__)
        )

    def create(self, width: int, height: int) -> None:
        raise NotImplementedError(
            'create Method not implemented for class {}'.format(self.__class__)
        )

    def fromSurface(self, surface: pygame.Surface) -> None:
        raise NotImplementedError(
            'fromSurface Method not implemented for class {}'.format(self.__class__)
        )

    def copy(self) -> 'Image':
        raise NotImplementedError(
            'copy Method not implemented for class {}'.format(self.__class__)
        )

    def scale(self, width: int, height: int) -> 'Image':
        raise NotImplementedError(
            'scale Method not implemented for class {}'.format(self.__class__)
        )

    def blit(
        self,
        srcImage: 'Image',
        position: typing.Optional[typing.Tuple[int, int]] = None,
        area: typing.Optional[pygame.Rect] = None,
        alpha: int = 255,
    ) -> None:
        raise NotImplementedError(
            'blit Method not implemented for class {}'.format(self.__class__)
        )

    def fill(self, color: typing.Any) -> None:
        raise NotImplementedError(
            'fill Method not implemented for class {}'.format(self.__class__)
        )

    def flip(
        self, flipX: bool = False, flipY: bool = False, rotate: bool = False
    ) -> 'Image':
        raise NotImplementedError(
            'flip Method not implemented for class {}'.format(self.__class__)
        )

    def subimage(self, rect: pygame.Rect) -> 'Image':
        raise NotImplementedError(
            'subimage Method not implemented for class {}'.format(self.__class__)
        )

    def getSize(self) -> typing.Tuple[int, int]:
        raise NotImplementedError(
            'getSize Method not implemented for class {}'.format(self.__class__)
        )

    def getWidth(self) -> int:
        raise NotImplementedError(
            'getWidth Method not implemented for class {}'.format(self.__class__)
        )

    def getHeight(self) -> int:
        raise NotImplementedError(
            'getHeight Method not implemented for class {}'.format(self.__class__)
        )


class Renderer:

    renderer: typing.ClassVar['Renderer']
    resolution: typing.Tuple[int, int]
    depth: int
    fullScreen: bool

    def __init__(
        self,
        width: int = 1024,
        height: int = 768,
        depth: int = 32,
        fullScreen: bool = False,
    ):
        self.resolution = (width, height)
        self.depth = depth
        self.fullScreen = fullScreen
        self.screen = None

        Renderer.renderer = self

        pygame.init()

    def setMode(self, width: int, heigth: int, depth: int = 32) -> None:
        self.resolution = (width, heigth)
        self.depth = depth

    def init(self) -> None:
        raise NotImplementedError(
            'init Method not implemented for class {}'.format(self.__class__)
        )

    def quit(self) -> None:
        pygame.quit()

    def getSize(self) -> typing.Tuple[int, int]:
        return self.resolution

    def getWidth(self) -> int:
        return self.resolution[0]

    def getHeight(self) -> int:
        return self.resolution[1]

    def blit(
        self,
        image: Image,
        position: typing.Optional[typing.Tuple[int, int]] = None,
        area: typing.Optional[pygame.Rect] = None,
        alpha: int = 255,
    ) -> None:
        raise NotImplementedError(
            'blit Method not implemented for class {}'.format(self.__class__)
        )

    def beginDraw(self) -> None:
        raise NotImplementedError(
            'beginDraw Method not implemented for class {}'.format(self.__class__)
        )

    def endDraw(self) -> None:
        raise NotImplementedError(
            'endDraw Method not implemented for class {}'.format(self.__class__)
        )

    def image(self, width: int, height: int) -> Image:
        raise NotImplementedError(
            'createImage Method not implemented for class {}'.format(self.__class__)
        )

    def imageFromFile(self, path: str) -> Image:
        raise NotImplementedError(
            'loadImage Method not implemented for class {}'.format(self.__class__)
        )

    def imageFromSurface(self, surface: pygame.Surface) -> Image:
        raise NotImplementedError(
            'loadImage Method not implemented for class {}'.format(self.__class__)
        )
