# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


class Actor(object):
    def __init__(self):
        pass


class ActorList(object):
    def __init__(self):
        self.actors = {}

    def addActorsFromArrayLayer(self, arrayLayer):
        '''
        Initializes the actor list from an array layer
        '''
        logger.debug('Adding actors from {}'.format(arrayLayer))
        # Sort actors by type, we can later iterate this dictionary
        for actor in arrayLayer:
            actorType = actor[2].getProperty('type')
            if actorType is None:
                logger.error('Found an actor without type: {} (ignored)'.format(actor[2]))
                continue
            try:
                self.actors[actorType].append(actor)
            except:
                self.actors[actorType] = [actor]

        logger.debug(unicode(self))

    def iteritems(self):
        return self.actors.iteritems()

    def __unicode__(self):
        return 'Actors: {}, ({})'.format(len(self.actors), self.actors)
