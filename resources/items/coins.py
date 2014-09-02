# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from game.actors import actorsFactory
from game.actors import Actor
from game.sound import soundsStore

import logging

logger = logging.getLogger(__name__)


class Coin(Actor):
    def __init__(self, parentMap, fromTile, actorType, x=0, y=0, w=None, h=None):
        Actor.__init__(self, parentMap, fromTile, actorType, x, y, w, h)
        self.soundGetCoin = soundsStore.get('pop')

    def hit(self, sender):
        Actor.hit(self, sender)
        self.soundGetCoin.play()

actorsFactory.registerType('BronceCoin', Coin)
actorsFactory.registerType('SilverCoin', Coin)
actorsFactory.registerType('GoldCoin', Coin)

# Register and load sounds for coins
soundsStore.storeSoundFile('pop', 'coin.ogg')
