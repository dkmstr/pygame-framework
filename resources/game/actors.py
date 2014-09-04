# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging

logger = logging.getLogger(__name__)

class Actor(object):
    EMPTY_RECT = pygame.Rect(0, 0, 0, 0)
    
    def __init__(self, parentMap, fromTile, actorType, x=0, y=0, w=None, h=None):
        tileRect = fromTile.getRect()
        w = tileRect.width if w is None else w
        h = tileRect.height if h is None else h
        self.xOffset = tileRect.left
        self.yOffset = tileRect.top

        self.rect = pygame.Rect(x+self.xOffset, y+self.yOffset, w, h)
        
        self.tile = fromTile
        self.parentMap = parentMap
        self.boundary = self.parentMap.getRect()
        self.actorType = actorType
        self.impact = False
        
    def move(self, xOffset, yOffset):
        self.rect.left += xOffset
        self.rect.top += yOffset
        self.rect.clamp_ip(self.boundary)

    def setPosition(self, x, y):
        self.rect.top, self.rect.left = x, y
        self.rect.clamp_ip(self.boundary)

    def getRect(self):
        return self.rect

    def collide(self, rect):
        if self.impact:
            return False
        return  self.rect.colliderect(rect)

    def draw(self, toSurface):
        if self.impact:
            return
        x, y = self.parentMap.translateCoordinates(self.rect.x-self.xOffset, self.rect.y-self.yOffset) 
        self.tile.draw(toSurface, x, y)

    def update(self):
        return not self.impact
    
    def notify(self, sender, message):
        '''
        Used so we can notify things to actors
        By default, it checks if 'hit' is the message, and simply sets "impact" to true
        '''
        if message == 'hit':
            self.impact = True


class ActorsFactory(object):
    def __init__(self):
        self.actorTypes = {}

    def registerType(self, actorTypeName, actorType):
        self.actorTypes[actorTypeName] = actorType

    def getActor(self, actorType):
        return self.actorTypes.get(actorType)

actorsFactory = ActorsFactory()
