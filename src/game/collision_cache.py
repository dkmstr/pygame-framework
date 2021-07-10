# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame

from game.interfaces import Collidable
from game.interfaces import Drawable

import logging

logger = logging.getLogger(__name__)

class CollisionCache(object):
    def __init__(self, parentMap, cachesActors=False, cachesObjects=False, cacheThreshold=32, collisionRangeCheck=128):
        self._parentMap = parentMap
        self._cachesActors = cachesActors
        self._cachesObjects = cachesObjects
        self._cacheThreshold = cacheThreshold
        self._collisionRange = collisionRangeCheck
        
        self._colCacheActors = None
        self._colCacheObjects = None
        self._cachedPos = (-100000, -10000)
        
        
    def resetCollisionsCache(self, rect: pygame.Rect) -> None:
        self._colCacheActors = self._colCacheObjects = None
        self._cachedPos = rect.topleft
        
    def updateCollisionsCache(self, rect: pygame.Rect) -> None:
        if abs(self._cachedPos[0] - rect.x) > self._cacheThreshold or abs(self._cachedPos[1] - rect.y) > self._cacheThreshold:
            self.resetCollisionsCache(rect)
        
        if self._colCacheActors is None:
            self._colCacheActors = self._parentMap.getPossibleActorsCollisions(rect, self._collisionRange, self._collisionRange)
        if self._colCacheObjects is None:
            self._colCacheObjects = self._parentMap.getPossibleCollisions(rect, self._collisionRange, self._collisionRange)
        
    @property
    def actorsCache(self):
        return self._colCacheActors
    
    @property
    def objectCache(self):
        return self._colCacheObjects

    def getActorsCollissions(self, rect):
        self.updateCollisionsCache(rect)
        return self._parentMap.getActorsCollisions(rect, self._colCacheActors)
    
    def getObjectsCollisions(self, rect):
        self.updateCollisionsCache(rect)
        return self._parentMap.getCollisions(rect, self._colCacheObjects)
    
class WithCollisionCache(Collidable):
    def __init__(self, parentMap, cachesActors=False, cachesObjects=False, cacheThreshold=32, collisionRangeCheck=128):
        self.collisionCache = CollisionCache(parentMap, cachesActors, cachesObjects, cacheThreshold, collisionRangeCheck)
    
    def resetCollisionsCache(self):
        self.collisionCache.resetCollisionsCache(self.getColRect())
        
    def updateCollisionsCache(self):
        self.collisionCache.updateCollisionsCache(self.getColRect())

    def getCollisions(self, rect=None):
        rect = self.getColRect() if rect is None else rect
        return self.collisionCache.getObjectsCollisions(rect)
    
    def getActorsCollisions(self, rect=None):
        rect = self.getColRect() if rect is None else rect
        return self.collisionCache.getActorsCollissions(rect)
    