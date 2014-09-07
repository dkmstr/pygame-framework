# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from game.layers.layer import Layer

import logging

logger = logging.getLogger(__name__)


class EffectsLayer(Layer):
    LAYER_TYPE = 'effects'

    def __init__(self, parentMap):
        Layer.__init__(self, parentMap)
        self.effectsList = []  # Empty effects list

    def onUpdate(self):
        toRemove = [effect for effect in self.effectsList if effect.update()]
        for effectToRemove in toRemove:
            self.removeEffect(effectToRemove)
        
    def onDraw(self, toSurface, rect):
        for effect in self.effectsList:
            effect.draw(toSurface, rect)  # Effects are always drawn right now
        
    def addEffect(self, effectId, effect):
        if effectId is not None:
            for e in self.effectsList:
                if e.effectId == effectId:
                    return  # Do not add it again if it already exists
        
        self.effectsList.append(effect)
        effect.effectId = effectId
        
    def removeEffect(self, effect):
        try:
            self.effectsList.remove(effect)
        except ValueError:
            return False
        return True
        