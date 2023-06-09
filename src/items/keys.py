# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from game.actors import actorsFactory
from game.actors import Actor
from game.sound.sound import SoundsStore

import logging

logger = logging.getLogger(__name__)


class Key(Actor):
    def __init__(self, parentMap, fromTile, actorType, x=0, y=0, w=None, h=None):
        Actor.__init__(self, parentMap, fromTile, actorType, x, y, w, h)

        # Register and load sounds for keys
        SoundsStore.store.storeSoundFile('key', 'key.ogg')

        self.soundGetKey = SoundsStore.store.get('key')

    def notify(self, sender, message):
        Actor.notify(self, sender, message)
        self.soundGetKey.play()
        sender.notify(self, self.actorType)


actorsFactory.registerType('YellowKey', Key)
