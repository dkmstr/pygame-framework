# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging

logger = logging.getLogger(__name__)


class Actor(object):
    def __init__(self, parentMap, fromTile, actorType, x=0, y=0, w=None, h=None):
        size = fromTile.getSize()
        w = size[0] if w is None else w
        h = size[1] if h is None else h
        self.rect = pygame.Rect(x, y, w, h)
        self.tile = fromTile
        self.parentMap = parentMap
        self.boundary = self.parentMap.getRect()
        self.actorType = actorType
        
    def move(self, xOffset, yOffset):
        self.rect.left += xOffset
        self.rect.top += yOffset
        
    def setPosition(self, x, y):
        self.rect.top, self.rect.left = x, y
        
    def getRect(self):
        return self.rect
    
    def collide(self, rect):
        return self.rect.colliderect(rect)
        
    def draw(self, toSurface):
        x, y = self.parentMap.translateCoordinates(self.rect.x, self.rect.y)
        self.tile.draw(toSurface, x, y)

    def update(self):
        pass
    

class ActorsFactory(object):
    def __init__(self):
        self.actorTypes = {}
        
    def registerType(self, actorTypeName, actorType):
        self.actorTypes[actorTypeName] = actorType
        
    def getActor(self, actorType):
        return self.actorTypes.get(actorType)
    
actorsFactory = ActorsFactory()