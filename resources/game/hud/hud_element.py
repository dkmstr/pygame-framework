# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame

class HudElement(object):
    def __init__(self, x, y, w=0, h=0):
        self.rect = pygame.Rect(x, y, w, h)
        
    def draw(self, toSurface):
        pass
    
    def update(self):
        pass
