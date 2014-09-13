# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging

from game.objects import GraphicObject
from game.debug import drawDebugRect

logger = logging.getLogger(__name__)

class Actor(GraphicObject): 
    EMPTY_RECT = pygame.Rect(0, 0, 0, 0)
    
    def __init__(self, parentLayer, fromTile, actorType, x=0, y=0, w=None, h=None):
        GraphicObject.__init__(self, parentLayer, pygame.Rect(x, y, 0, 0))
        tileRect = fromTile.getRect()
        self.rect.width = tileRect.width if w is None else w
        self.rect.height = tileRect.height if h is None else h
        self.xOffset = tileRect.left
        self.yOffset = tileRect.top

        self.tile = fromTile
        self.boundary = self.parent.parentMap.getRect()
        self.actorType = actorType
        self.impact = False
        
    def move(self, xOffset, yOffset):
        if xOffset != 0 or yOffset != 0:
            self.rect.left += xOffset
            self.rect.top += yOffset
            self.rect.clamp_ip(self.boundary)
            self.positionChanged()

    def setPosition(self, x, y):
        if x != self.rect.left or y != self.rect.top:
            self.rect.top, self.rect.left = x, y
            self.rect.clamp_ip(self.boundary)
            self.positionChanged()

    def positionChanged(self):
        self.parent.positionChanged(self)

    def getColRect(self):
        return pygame.Rect(self.rect.left+self.xOffset, self.rect.top+self.yOffset, self.rect.width, self.rect.height)

    def collide(self, rect):
        if self.impact:
            return False
        return  rect.colliderect((self.rect.left+self.xOffset, self.rect.top+self.yOffset, self.rect.width, self.rect.height))

    def draw(self, toSurface):
        if self.impact:
            return
        rect = self.parent.parentMap.translateCoordinates(self.rect) 
        self.tile.draw(toSurface, rect)
        drawDebugRect(toSurface, rect.move(self.xOffset, self.yOffset), width=4)

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
