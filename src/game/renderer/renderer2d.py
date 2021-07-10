import typing

import pygame

from . import renderer


class Image2D(renderer.Image):
    def __init__(self) -> None:
        super().__init__()

    def load(self, path: str) -> None:
        self.surface = typing.cast(
            pygame.Surface, pygame.image.load(path).convert_alpha()
        )

    def create(self, width: int, height: int) -> None:
        self.surface = pygame.Surface(
            (width, height), flags=pygame.SRCALPHA | pygame.HWSURFACE
        )

    def fromSurface(self, surface: pygame.Surface) -> None:
        self.surface = surface

    def copy(self) -> 'renderer.Image':
        img = Image2D()
        if self.surface:
            img.surface = typing.cast(pygame.Surface, self.surface.copy())
        return img

    def scale(self, width: int, height: int) -> 'Image':
        img = Image2D()
        if self.surface:
            img.surface = typing.cast(
                pygame.Surface,
                pygame.transform.smoothscale(
                    self.surface, (int(width), int(height))
                ).convert_alpha(),
            )
        return img

    def blit(
        self,
        srcImage: 'renderer.Image',
        position: typing.Optional[typing.Tuple[int, int]] = None,
        area: typing.Optional[pygame.Rect] = None,
        alpha: int = 255,
    ) -> None:
        if (
            not self.surface
            or not isinstance(srcImage, Image2D)
            or not srcImage.surface
        ):
            return

        if not self.surface or not srcImage.surface:
            return

        if alpha != 255:  # Add transparency if required
            surface = srcImage.surface.copy()
            surface.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        else:
            surface = srcImage.surface

        self.surface.blit(surface, position, area)

    def fill(self, color: typing.Any):
        if self.surface:
            self.surface.fill(color)

    def flip(
        self, flipX: bool = False, flipY: bool = False, rotate: bool = False
    ) -> 'Image2D':
        img = Image2D()
        if self.surface:
            if rotate:
                surface = pygame.transform.rotate(self.surface, 90)
            else:
                surface = self.surface
            img.surface = typing.cast(
                pygame.Surface, pygame.transform.flip(surface, flipX, flipY)
            )
        return img

    def subimage(self, rect: pygame.Rect) -> 'Image2D':
        img = Image2D()
        if self.surface:
            img.surface = typing.cast(pygame.Surface, self.surface.subsurface(rect))
        return img

    def getSize(self) -> typing.Tuple[int, int]:
        if self.surface:
            return self.surface.get_size()
        return (0, 0)

    def getWidth(self) -> int:
        if self.surface:
            return self.surface.get_width()
        return 0

    def getHeight(self) -> int:
        if self.surface:
            return self.surface.get_height()
        return 0


class Renderer2D(renderer.Renderer):
    screen: pygame.Surface

    def init(self):
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        if self.fullScreen:
            flags |= pygame.FULLSCREEN
        self.screen = typing.cast(
            pygame.Surface, pygame.display.set_mode(self.resolution, flags, self.depth)
        )

    def quit(self):
        pygame.quit()

    def blit(
        self,
        image: 'renderer.Image',
        position: typing.Optional[typing.Tuple[int, int]] = None,
        area: typing.Optional[pygame.Rect] = None,
        alpha: int = 255,
    ):
        if not image.surface or not isinstance(image, Image2D):
            return

        if position is None:
            position = (0, 0)

        if alpha != 255:  # Add transparency if required
            image = image.copy()
            typing.cast(pygame.Surface, image.surface).fill(
                (255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT
            )

        self.screen.blit(typing.cast(pygame.Surface, image.surface), position, area)

    def beginDraw(self) -> None:
        pass

    def endDraw(self) -> None:
        pygame.display.flip()

    def getSize(self) -> typing.Tuple[int, int]:
        return self.resolution

    def getWidth(self) -> int:
        return self.resolution[0]

    def getHeight(self) -> int:
        return self.resolution[1]

    def image(self, width: int, height: int) -> renderer.Image:
        img = Image2D()
        img.create(width, height)
        return img

    def imageFromFile(self, path: str) -> renderer.Image:
        img = Image2D()
        img.load(path)
        return img

    def imageFromSurface(self, surface: pygame.Surface) -> renderer.Image:
        img = Image2D()
        img.fromSurface(surface)
        return img
