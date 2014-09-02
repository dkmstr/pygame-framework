# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from game.actors import actorsFactory
from game.actors import Actor
from game.sound import soundsStore

import logging

logger = logging.getLogger(__name__)


class Key(Actor):
    def __init__(self, parentMap, fromTile, actorType, x=0, y=0, w=None, h=None):
        Actor.__init__(self, parentMap, fromTile, actorType, x, y, w, h)
        
        self.soundGetKey = soundsStore.get('key')
        
    def hit(self, sender):
        Actor.hit(self, sender)
        self.soundGetKey.play()
        sender.keys['yellowKey'] = True
    

actorsFactory.registerType('YellowKey', Key)
# Register and load sounds for keys
soundsStore.storeFile('key', 'key.ogg')
