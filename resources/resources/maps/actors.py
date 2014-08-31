# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


class Actor(object):
    def __init__(self, parentMap, actorType, x=0, y=0):
        self.parentMap = parentMap
        self._x = x
        self._y = y
        self.actorType = actorType
        
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