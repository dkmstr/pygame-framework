# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)

class Effect(object):
    def __init__(self, rect):
        self.rect = rect
        self.effectId = None

    def update(self):
        '''
        If returns True, means that this effect has finished
        '''
        raise NotImplementedError('update method not implemented!!')

    def getRect(self):
        return self.rect

    def draw(renderer, rect):
        pass
