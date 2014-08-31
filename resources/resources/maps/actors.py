# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging

logger = logging.getLogger(__name__)


class Actor(object):
    def __init__(self, parentMap, actorType, x=0, y=0, w=0, h=0):
        self.rect = pygame.Rect(x, y, w, h)
        self.parentMap = parentMap
        self.actorType = actorType
        
    def setPosition(self, x, y):
        self.rect = pygame.Rect(x, y, 70, 70)
        
    def draw(self, toSurface):
        pass
    
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