# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from game.actors import actorsFactory
from game.layers.layer import Layer

import logging

logger = logging.getLogger(__name__)


class ActorsLayer(Layer):
    LAYER_TYPE = 'actors'

    def __init__(self, parentMap, arrayLayer):
        Layer.__init__(self, parentMap)

        self.name = arrayLayer.name
        self.width = self.height = 0
        self.actorList = []
        self.setProperties(arrayLayer.properties)

        logger.debug('Adding actors from {}'.format(arrayLayer))
        # Sort actors by type, we can later iterate this dictionary
        for actor in arrayLayer:
            x, y, tile, actorType = actor[0], actor[1], actor[2], actor[2].getProperty('type')
            if actorType is None:
                logger.error('Found an actor without type: {} (ignored)'.format(actorType))
                continue
            aClass = actorsFactory.getActor(actorType)
            if aClass is None:
                logger.error('Found an unregistered actor class: {}'.format(actorType))
                continue
            self.actorList.append(aClass(self.parentMap, tile, actorType, x, y))

        logger.debug(unicode(self))

    def onDraw(self, toSurface, rect):
        for actor in self.actorList:
            if actor.collide(rect):  # Only draws if actor is visible
                actor.draw(toSurface)

    def onUpdate(self):
        toRemove = [actor for actor in self.actorList if actor.update() is False]
        for actorToRemove in toRemove:
            self.removeActor(actorToRemove)

    def getCollisions(self, rect):
        for actor in self.actorList:
            if actor.collide(rect):
                yield (actor.getRect(), actor)

    def getActors(self, actorType=None):
        for actor in self.actorList:
            if actorType is None:
                yield actor
            elif actor.actorType == actorType:
                yield actor

    def removeActor(self, actor):
        try:
            self.actorList.remove(actor)
        except ValueError:
            return False
        return True
