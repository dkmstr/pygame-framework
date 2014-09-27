# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging
from game.util import checkTrue
from game.objects.graphic_object import GraphicObject
from game.collision_cache import WithCollisionCache

logger = logging.getLogger(__name__)

COLLISION_CACHE_THRESHOLD = 50

class ObjectWithPath(GraphicObject, WithCollisionCache):
    '''
    This represents a objtect that has an inplicit path (as a platform)
    The object can be "stopped", and path can be None (in wich case this is a simple static object)
    '''
    def __init__(self, parentLayer, rect, surface, properties):
        WithCollisionCache.__init__(self, parentLayer.parentMap,
                                    cachesActors=True,
                                    cachesObjects=False,
                                    cacheThreshold=32,
                                    collisionRangeCheck=128)
        GraphicObject.__init__(self, parentLayer, rect, properties)

        self.parentLayer = parentLayer
        self.surface = surface

    def updateAttributes(self):
        GraphicObject.updateAttributes(self)
        self.path = self.getProperty('path', None)
        self.sticky = checkTrue(self.getProperty('sticky', 'True'))
        self.stopped = checkTrue(self.getProperty('stopped', 'False'))

    def draw(self, renderer, rect):
        '''
        Draws to specied surface, to coords x, y
        '''
        #rect = pygame.Rect((x, y), toSurface.get_size())
        if not rect.colliderect(self.rect):
            return
        # Translate start to screen coordinates
        renderer.blit(self.surface, (self.rect.left - rect.left, self.rect.top - rect.top))

    def getColRect(self):
        return self.rect

    def update(self):
        if self.path is None or self.stopped is True:
            return

        x, y = self.rect.left, self.rect.top
        self.path.save()  # Keeps a copy before iterating, so if we collide we can return back
        self.rect.left, self.rect.top = self.path.iterate()
        xOffset, yOffset = self.rect.left - x, self.rect.top - y

        # Reduce a lot the numberof tests needed
        self.updateCollisionsCache()

        # First we check what any actor collided moves acordly
        for c in self.getActorsCollisions():
            actorRect, actor, actorLayer = c  # actorRect is a "reference" to actor position, so modifying it will modify actor's position
            if yOffset > 0 or xOffset != 0:  # Do not move if we moved down, left or right
                self.path.restore()
                self.rect.left, self.rect.top = x, y
            else:
                # If actor collides in new position, do not move
                bottom = actor.rect.bottom
                actor.move(0, yOffset)
                # actor.rect.bottom = self.rect.top - 1
                if any(actor.getCollisions()):
                    actor.rect.bottom = bottom
                    self.path.restore()
                    self.rect.left, self.rect.top = x, y

        # Now, it we are "sticky", we move any actor that is "over" this item
        # Sticky is only sticky for actors that are ON this object
        if self.sticky and xOffset != 0:
            # Inflate rect at top to detect collision
            rect = pygame.Rect(self.rect.left, self.rect.top-2, self.rect.width, self.rect.height+2)
            for c in self.getActorsCollisions(rect):
                actorRect, actor, actorLayer = c
                actor.move(xOffset, 0)  # Actor collisions rects do not coincide exactly with blitting pos, so let actor itself modify it's position
                actor.notify(self, 'moved')

    def collide(self, rect):
        return self.rect.colliderect(rect)

    def start(self):
        self.stopped = False

    def stop(self):
        self.stopped = True

    def __unicode__(self):
        return 'Object with path {}'.format(self.path)
