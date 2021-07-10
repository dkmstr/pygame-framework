import logging
import typing

import pygame

from game.util import checkTrue

import game.interfaces

if typing.TYPE_CHECKING:
    import game.layers
    import game.tiles
    import game.renderer

logger = logging.getLogger(__name__)

ParentType = typing.Union['game.layers.Layer', 'game.tiles.TileSet']

class GraphicObject(game.interfaces.Collidable, game.interfaces.Drawable):
    parent: ParentType
    properties: typing.Dict[str, str]
    collission: bool
    blocks: bool
    rect: pygame.Rect
    name: typing.Optional[str]
    objType: typing.Optional[str]

    def __init__(
        self,
        parent: ParentType,
        rect: typing.Optional[pygame.Rect],
        properties: typing.Optional[typing.Dict[str, str]] = None,
    ) -> None:
        self.parent = parent
        self.properties = {}
        self.rect = rect if rect is not None else pygame.Rect(0, 0, 0, 0)
        # Attributes defaults
        self.name = ''
        self.collission = False
        self.block = False
        self.objType = ''
        self.setProperties(properties)

    def updateAttributes(self) -> None:
        '''
        Updates attributes of the object because properties was set
        '''
        # Possible attributes
        self.collission = checkTrue(self.getProperty('collission', 'False'))
        self.blocks = checkTrue(self.getProperty('blocks', 'True'))
        self.objType = self.getProperty('type')
        self.name = self.getProperty('name')

        # Ladder and collectables do not blocks
        if self.objType in ('ladder', 'collectable'):
            self.blocks = False

    def setProperties(self, properties: typing.Optional[typing.Dict[str, str]]) -> None:
        self.properties = properties if properties else {}
        self.updateAttributes()

    def setProperty(self, prop: str, value: str) -> None:
        self.properties[prop] = value

    def getProperty(self, propertyName: str, default=None) -> typing.Optional[str]:
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName, default)

    def getRect(self) -> pygame.Rect:
        return self.rect

    def getColRect(self) -> pygame.Rect:
        return self.rect

    def hasProperty(self, prop: str) -> bool:
        return prop in self.properties

    def isA(self, objType: str) -> bool:
        '''
        returns True if the object if of the specified type
        '''
        return self.objType == objType

    def collide(self, rect: pygame.Rect) -> bool:
        '''
        By default do not collides :-)
        '''
        return False

    def positionChanged(self) -> None:
        '''
        By default, does nothing
        '''
        logger.debug('Position changed invoked for {}'.format(str(self)))

    # Draw is invoked with three parameters:
    # Renderer: rendereable wher to draw
    # x, y: Relative position of the surface. This means that if a surface, is,
    # for example, at 100, 100
    # we will have to translate blitting to X, y
    def draw(self, renderer: 'game.renderer.Renderer', rect: pygame.Rect) -> None:
        pass

    def update(self) -> None:
        pass
