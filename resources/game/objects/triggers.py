# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import logging
from game.util import checkTrue
from game.interfaces import Collidable
from game.sound.sound import SoundsStore

logger = logging.getLogger(__name__)

class Trigger(Collidable):
    def __init__(self, parent, name, rect, properties=None):
        self.parent = parent
        self.name = name
        self.properties = None
        self.rect = rect if rect is not None else pygame.Rect(0, 0, 0, 0)
        self.triggeredsList = []
        self.tileIdOnTrigger = None
        self.fired = False
        self.sound = None
        self.sound_volume = 1.0
        self.setProperties(properties)
        if self.sound is not None:
            self.sound = SoundsStore.store.storeSoundFile('trigger_{}_snd'.format(self.name), self.sound, volume=self.sound_volume)

    def updateAttributes(self):
        '''
        Updates attributes of the object because properties was set
        '''
        self.sound = self.getProperty('sound', None)
        try:
            self.sound_volume = float(self.getProperty('sound_volume', '1.0'))
        except Exception:
            self.sound_volume = 1.0
            
        try:
            layer = self.parent.associatedLayer
            if layer.layerType == 'array':
                tileId = int(self.getProperty('tile_on_trigger', None))
                if tileId is not None:
                    originalTile = layer.getObjectAt(self.rect.x, self.rect.y)
                    if originalTile is not None:
                        self.tileIdOnTrigger = originalTile.parent.getTile(tileId).tileId + 1
        except Exception:
            self.tileIdOnTrigger = None
    
    def setProperties(self, properties):
        self.properties = properties if properties is not None else {}
        self.updateAttributes()
        
    def setProperty(self, prop, value):
        self.properties[prop] = value

    def getProperty(self, propertyName, default=None):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName, default)
    
    def getRect(self):
        return self.rect
    
    def getColRect(self):
        return self.rect

    def hasProperty(self, prop):
        return prop in self.properties
    
    def isA(self, objType):
        '''
        returns True if the object if of the specified type
        '''
        return self.objType == objType
    
    def appendTriggered(self, triggered):
        self.triggeredsList.append(triggered)

    def collide(self, rect):
        '''
        By default do not collides :-)
        '''
        return self.rect.colliderect(rect)
    
    def update(self):
        pass
    
    def fire(self):
        if self.fired is True:
            logger.error('Trigger {} has already been fired'.format(self.name))
            return
        # Firef just once
        self.parent.removeTrigger(self)
        
        self.fired = True
        for triggered in self.triggeredsList:
            triggered.execute()
        
        if self.sound is not None:
            self.sound.play()
            
        if self.tileIdOnTrigger:
            self.parent.associatedLayer.setTileAt(self.rect.x, self.rect.y, self.tileIdOnTrigger)

class Triggered(object):
    def __init__(self, parentLayer, name, rect, properties=None):
        self.parent = parentLayer
        self.name = name
        self.properties = None
        self.rect = rect if rect is not None else pygame.Rect(0, 0, 0, 0)
        self.action = None
        self.by = None
        self.executed = False
        
        self.setProperties(properties)

    def updateAttributes(self):
        '''
        Updates attributes of the object because properties was set
        '''
        self.action = self.getProperty('action', None)
        self.by = self.getProperty('by', None)
    
    def setProperties(self, properties):
        self.properties = properties if properties is not None else {}
        self.updateAttributes()
        
    def setProperty(self, prop, value):
        self.properties[prop] = value

    def getProperty(self, propertyName, default=None):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName, default)
    
    def getRect(self):
        return self.rect

    def execute(self):
        if self.executed is True:
            logger.error('Triggered {} has already been executed'.format(self.name))
            return
        
        self.executed = True
        
        logger.debug('Executing triggered {}'.format(self.name))
        
        layer = self.parent.associatedLayer
        tileWidth = self.parent.parentMap.tileWidth
        tileHeight = self.parent.parentMap.tileHeight
        if self.action == 'remove':
            for y in xrange(self.rect.top, self.rect.bottom, tileHeight):
                for x in xrange(self.rect.left, self.rect.right, tileWidth):
                    logger.debug('Remove : {},{}'.format(x, y))
                    layer.removeObjectAt(x, y)
        else:
            logger.error('Unknown action in triggered {}: {}'.format(self.name, self.action))