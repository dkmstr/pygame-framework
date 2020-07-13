# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class Collidable(object):
    def getColRect(self):
        '''
        Returns the collision rect of this object
        The returned value must be ABSOLUTE rect, not screen rects
        '''
        raise NotImplementedError('You must provide getColRect method for a Collidable')

    def collide(self, rect):
        '''
        Checks if objects collides with a rect
        '''
        raise NotImplementedError('You must provide collide method for a Collidable')

    def positionChanged(self):
        '''
        Provides a method for notify that our position has changed
        '''
        raise NotImplementedError('You must provide positionChanged method for a Collidable')


class Drawable(object):
    def getRect(self):
        raise NotImplementedError('You must provide getRect method for a Drawable')

    def draw(self, renderer, rect):
        '''
        '''
        raise NotImplementedError('You must provide draw method for a Drawable')
