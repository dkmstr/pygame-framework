import logging
import typing

import pygame

import game.objects
from game.debug import drawDebugRect

if typing.TYPE_CHECKING:
    import game.layers
    import game.tiles
    import game.renderer

logger = logging.getLogger(__name__)


class Actor(game.objects.GraphicObject):
    EMPTY_RECT = pygame.Rect(0, 0, 0, 0)
    parent: 'game.layers.ActorsLayer'  # refefine type of parent

    def __init__(
        self,
        parentLayer: 'game.layers.ActorsLayer',
        fromTile: 'game.tiles.Tile',
        actorType: str,
        x: int = 0,
        y: int = 0,
        w: typing.Optional[int] = None,
        h: typing.Optional[int] = None,
    ):
        super().__init__(parentLayer, pygame.Rect(x, y, 0, 0))
        tileRect = fromTile.getRect()
        self.rect.width = tileRect.width if w is None else w
        self.rect.height = tileRect.height if h is None else h
        self.xOffset = tileRect.left
        self.yOffset = tileRect.top

        self.tile = fromTile
        self.boundary = (
            self.parent.parentMap.getRect()
            if self.parent.parentMap
            else Actor.EMPTY_RECT
        )
        self.actorType = actorType
        self.impact = False

    def move(self, xOffset: int, yOffset: int) -> None:
        if xOffset != 0 or yOffset != 0:
            self.rect.left += xOffset
            self.rect.top += yOffset
            self.rect.clamp_ip(self.boundary)
            self.positionChanged()

    def setPosition(self, x: int, y: int) -> None:
        if x != self.rect.left or y != self.rect.top:
            self.rect.top, self.rect.left = x, y
            self.rect.clamp_ip(self.boundary)
            self.positionChanged()

    def positionChanged(self) -> None:
        self.parent.positionChanged(self)

    def getColRect(self):
        return pygame.Rect(
            self.rect.left + self.xOffset,
            self.rect.top + self.yOffset,
            self.rect.width,
            self.rect.height,
        )

    def collide(self, rect):
        if self.impact:
            return False
        return rect.colliderect(
            (
                self.rect.left + self.xOffset,
                self.rect.top + self.yOffset,
                self.rect.width,
                self.rect.height,
            )
        )

    def draw(
        self,
        renderer: 'game.renderer.Renderer',
        rect: typing.Optional[pygame.Rect] = None,
    ) -> None:
        if self.impact:
            return
        if not self.parent.parentMap:
            return

        rect = self.parent.parentMap.translateCoordinates(self.rect)

        self.tile.draw(renderer, rect)
        drawDebugRect(
            renderer,
            typing.cast(pygame.Rect, rect.move(self.xOffset, self.yOffset)),
            width=4,
        )

    def update(self):
        return not self.impact

    def notify(self, sender: typing.Any, message: str) -> None:
        '''
        Used so we can notify things to actors
        By default, it checks if 'hit' is the message, and simply sets "impact" to true
        '''
        if message == 'hit':
            self.impact = True


class ActorsFactory:
    actorTypes: typing.Dict[str, typing.Type[Actor]]

    def __init__(self):
        self.actorTypes = {}

    def registerType(self, actorTypeName: str, actorType: typing.Type[Actor]) -> None:
        self.actorTypes[actorTypeName] = actorType

    def getActor(self, actorType) -> typing.Optional[typing.Type[Actor]]:
        return self.actorTypes.get(actorType)


actorsFactory = ActorsFactory()
