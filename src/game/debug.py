# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame

DEBUG = False

def drawDebugRect(toSurface, rect, color=(0, 0, 0, 255), width=1):
    if DEBUG is True:
        pygame.draw.rect(toSurface, color, rect, width)
