# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from resources.maps.actors import Actor

import pygame
import logging

logger = logging.getLogger(__name__)


class Player(Actor):
    def __init__(self, map, x, y):
        self.map = map
        self.rect = pygame.Rect(x, y, 69, 69)
        self.image1 = pygame.Surface((69, 69))
        self.image2 = pygame.Surface((69, 69))
        self.image1.fill(0)
        self.image2.fill(0xFF0000)
        self.image = self.image1
        
    def checkXCollisions(self, offset):
        if offset == 0:
            return
        for c in self.map.getCollisions(self.rect):
            colRect = c[0]
            if offset > 0:
                self.rect.right = colRect.left - 1
            else:
                self.rect.left = colRect.right + 1
            return True
        return False
    
    def checkYCollisions(self, offset):
        if offset == 0:
            return
        for c in self.map.getCollisions(self.rect):
            colRect = c[0]
            if offset > 0:
                self.rect.bottom = colRect.top - 1
            else:
                self.rect.top = colRect.bottom + 1
            return True
        return False

    def move(self, xOffset, yOffset):
        if xOffset == 0 and yOffset == 0:
            pass # Check someting pushing, from where
        else:
            self.rect.x += xOffset
            self.checkXCollisions(xOffset)
            self.rect.y += yOffset
            self.checkYCollisions(yOffset)

        collisions = None
        for collision in self.map.getCollisions(self.rect):
            collisions = True
            break

        if collisions is not None:
            self.image = self.image2
        else:
            self.image = self.image1

    def setPosition(self, x, y):
        self.rect = pygame.Rect(x, y, 70, 70)

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    def draw(self, toSurface):
        mapDisplay = self.map.getDisplayPosition()
        x, y = self.rect.x - mapDisplay[0], self.rect.y - mapDisplay[1]
        #print x, y
        toSurface.blit(self.image, (x, y))

    def updateMapDisplayPosition(self, displaySurface):
        w, h = displaySurface.get_size()

        boundariesX = (200-70, 200)
        boundariesY = (180-70, 180)

        xMap, yMap = self.map.getDisplayPosition()
        if xMap > self.rect.x - boundariesX[0] and xMap < self.rect.x:
            xMap = self.rect.x - boundariesX[0]
        elif xMap + w - self.rect.x < boundariesX[1]:
            xMap = self.rect.x - w + boundariesX[1]

        if yMap > self.rect.y - boundariesY[0] and yMap < self.rect.y:
            yMap = self.rect.y - boundariesY[0]
        elif yMap + h - self.rect.y < boundariesY[1]:
            yMap = self.rect.y - h + boundariesY[1]

        self.map.setDisplayPosition(xMap, yMap)
