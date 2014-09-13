# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class Collidable(object):
    def getColRect(self):
        '''
        Returns the collision rect of this object
        The returned value must be ABSOLUTE rect, not screen rects
        '''
        raise NotImplemented('You must provide getColRect method for a Collidable')
    
    def collide(self, rect):
        '''
        Checks if objects collides with a rect
        '''
        raise NotImplemented('You must provide collide method for a Collidable')
    
    
class Drawable(object):
    def draw(self, toSurface):
        '''
        '''
        raise NotImplemented('You must provide draw method for a Drawable')