# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from resources.maps.actors import Actor

import pygame
import logging

logger = logging.getLogger(__name__)


class Player(Actor):
    def __init__(self, parentMap, actorType, x=0, y=0, w=0, h=0):
        Actor.__init__(self, parentMap, actorType, x, y, 60, 69)
        self.image1 = pygame.Surface((self.rect.width, self.rect.height))
        self.image2 = pygame.Surface((self.rect.width, self.rect.height))
        self.image1.fill(0)
        self.image2.fill(0xFF0000)
        self.image = self.image1
        self.xSpeed = self.ySpeed = 0
        
    def checkXCollisions(self, offset):
        if offset == 0:
            return
        for c in self.parentMap.getCollisions(self.rect):
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
        for c in self.parentMap.getCollisions(self.rect):
            colRect = c[0]
            if offset > 0:
                self.rect.bottom = colRect.top - 1
            else:
                self.rect.top = colRect.bottom + 1
            return True
        return False

    def move(self, xOffset, yOffset):
        if xOffset == 0 and yOffset == 0:
            pass  # Is something pushes this, this will be calculated elsewhere
        else:
            self.rect.x += xOffset
            self.checkXCollisions(xOffset)
            self.rect.y += yOffset
            self.checkYCollisions(yOffset)

        collisions = None
        for collision in self.parentMap.getCollisions(self.rect):
            collisions = True
            break

        if collisions is not None:
            self.image = self.image2
        else:
            self.image = self.image1
            
    def update(self):
        self.move(self.xSpeed, self.ySpeed)

    def draw(self, toSurface):
        mapDisplay = self.parentMap.getDisplayPosition()
        x, y = self.rect.x - mapDisplay[0], self.rect.y - mapDisplay[1]
        #print x, y
        toSurface.blit(self.image, (x, y))

    def updateMapDisplayPosition(self, displaySurface):
        w, h = displaySurface.get_size()

        boundariesX = (200-70, 200)
        boundariesY = (180-70, 180)

        xMap, yMap = self.parentMap.getDisplayPosition()
        if xMap > self.rect.x - boundariesX[0] and xMap < self.rect.x:
            xMap = self.rect.x - boundariesX[0]
        elif xMap + w - self.rect.x < boundariesX[1]:
            xMap = self.rect.x - w + boundariesX[1]

        if yMap > self.rect.y - boundariesY[0] and yMap < self.rect.y:
            yMap = self.rect.y - boundariesY[0]
        elif yMap + h - self.rect.y < boundariesY[1]:
            yMap = self.rect.y - h + boundariesY[1]

        self.parentMap.setDisplayPosition(xMap, yMap)
