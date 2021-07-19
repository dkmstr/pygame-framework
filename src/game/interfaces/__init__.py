import typing

import pygame

if typing.TYPE_CHECKING:
    import game.renderer

class Collidable:
    def getColRect(self) -> pygame.rect.Rect:
        '''
        Returns the collision rect of this object
        The returned value must be ABSOLUTE rect, not screen rects
        '''
        raise NotImplementedError('You must provide getColRect method for a Collidable')

    def collide(self, rect: pygame.Rect) -> bool:
        '''
        Checks if objects collides with a rect
        '''
        raise NotImplementedError('You must provide collide method for a Collidable')

    def positionChanged(self) -> None:
        '''
        Provides a method for notify that our position has changed
        '''
        raise NotImplementedError('You must provide positionChanged method for a Collidable')


class Drawable:
    def getRect(self) -> pygame.Rect:
        raise NotImplementedError('You must provide getRect method for a Drawable')

    def draw(self, renderer: 'game.renderer.Renderer', rect: pygame.Rect) -> None:
        '''
        Draws this object to renderer
        '''
        raise NotImplementedError('You must provide draw method for a Drawable')
