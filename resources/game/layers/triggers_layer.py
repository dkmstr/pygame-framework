# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame

from game import paths
from game.util import loadProperties
from game.layers.layer import Layer
from game.objects.triggers import Trigger
from game.objects.triggers import Triggered


import logging

logger = logging.getLogger(__name__)


class TriggersLayer(Layer):
    LAYER_TYPE = 'triggers'

    def __init__(self, parentMap=None, layerType=None, properties=None):
        Layer.__init__(self, parentMap, layerType, properties)
        self.width = self.height = 0
        self.triggersList = []
        self.triggeredsList = []
        self.associatedLayer = None

    def load(self, node):
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])
        self.triggersList = []
        self.triggeredsList = []

        self.setProperties(loadProperties(node.find('properties')))

        associatedLayerName = self.properties.get('layer', None)
        self.associatedLayer = self.parentMap.getLayer(associatedLayerName)

        logger.debug('Loading triggers layer {}'.format(self.name))
        
        for obj in node.findall('object'):
            type_ = obj.attrib.get('type')
            name = obj.attrib.get('name')
            if type_ not in ('trigger', 'triggered'):
                logger.debug('Object {} is on a triggers layer but is neither a trigger nor a triggered'.format(name))
                continue
            properties = loadProperties(obj.find('properties'))
            rect = pygame.Rect( int(obj.attrib['x']),
                int(obj.attrib['y']),
                int(obj.attrib.get('width', self.parentMap.tileWidth)),
                int(obj.attrib.get('height', self.parentMap.tileHeight))
            )
            
            if type_ == 'trigger':
                logger.debug('Adding new trigger: {} on {}'.format(name, rect))
                self.triggersList.append(Trigger(self, name, rect, properties))
            else:
                logger.debug('Adding new triggered {} on {}'.format(name, rect))
                self.triggeredsList.append(Triggered(self, name, rect, properties))
        
        for triggered in self.triggeredsList:
            trigger = self.getTrigger(triggered.by)
            if trigger is None:
                logger.error('Triggered {} on layer {} does not has "by" property or it is incorrect'.format(triggered.name, self.name))
                continue
            logger.debug('Triggered {} is executed by trigger {}'.format(triggered.name, trigger.name))
            trigger.appendTriggered(triggered)
        
    def onDraw(self, toSurface, rect):
        pass

    def onUpdate(self):
        pass

    def getCollisions(self, rect):
        for obj in self.triggersList:
            if obj.collide(rect):
                yield (obj.getRect(), obj)
        

    def getTrigger(self, objecName):
        for t in self.triggersList:
            if t.name == objecName:
                return t
        return None
    
    def removeTrigger(self, trigger):
        try:
            self.triggersList.remove(trigger)
        except Exception:
            logger.exception('Removing trigger')

    def __iter__(self):
        for obj in self.platforms:
            yield obj

    def __unicode__(self):
        return 'Dinamyc Layer'
