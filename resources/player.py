# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from resources.actors import Actor
from resources.animation import FilesAnimation
from resources.animation import FlippedAnimation

import pygame

import logging

logger = logging.getLogger(__name__)

BASE_X_SPEED = 4 * 100
BASE_Y_SPEED = 8 * 100

SCREEN_BORDER_X = 300
SCREEN_BORDER_Y = 180


class Player(Actor):
    def __init__(self, parentMap, fromTile, actorType, x=0, y=0, w=None, h=None):
        Actor.__init__(self, parentMap, fromTile, actorType, x, y, 52, 66)
        self.image1 = pygame.Surface((self.rect.width, self.rect.height))
        self.image2 = pygame.Surface((self.rect.width, self.rect.height))
        self.image1.fill(0)
        self.image2.fill(0xFF0000)
        self.image = self.image1
        self.xSpeed = self.ySpeed = 0
        self.animationRight = FilesAnimation('data/actors/rp1_walk*.png', 10)
        self.animationLeft = FlippedAnimation(self.animationRight)
        self.animation = self.animationRight

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
            self.ySpeed = 0
            colRect = c[0]
            if offset > 0:
                self.rect.bottom = colRect.top - 1
            else:
                self.rect.top = colRect.bottom + 1
            return True
        return False

    def getCollisions(self):
        for c in self.parentMap.getCollisions(self.rect):
            yield c

    def move(self, xOffset, yOffset):
        if xOffset == 0 and yOffset == 0:
            pass  # Is something pushes this, this will be calculated elsewhere
        else:
            if xOffset:
                self.rect.x += xOffset
                self.rect.clamp_ip(self.boundary)
                self.checkXCollisions(xOffset)
            if yOffset:
                self.rect.y += yOffset
                self.rect.clamp_ip(self.boundary)
                self.checkYCollisions(yOffset)

    def calculateGravity(self):
        if self.ySpeed == 0:
            self.ySpeed = 800  # Faster than falling platforms or it will be doing "strange things"
        else:
            # Temporary to tests
            self.ySpeed += 35

    def update(self):

        self.calculateGravity()
        if self.xSpeed != 0:
            if self.xSpeed > 0:
                self.animation = self.animationRight
            else:
                self.animation = self.animationLeft
                
            self.animation.iterate()

        self.move(self.xSpeed/100, self.ySpeed/100)

    def draw(self, toSurface):
        x, y = self.parentMap.translateCoordinates(self.rect.x, self.rect.y)
        self.animation.draw(toSurface, x, y)

    def updateMapDisplayPosition(self, displaySurface):
        w, h = displaySurface.get_size()

        boundariesX = (SCREEN_BORDER_X-self.rect.width, SCREEN_BORDER_X)
        boundariesY = (SCREEN_BORDER_Y-self.rect.height, SCREEN_BORDER_Y)

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

    # Custom players method
    def stop(self):
        self.xSpeed = 0
        self.animationRight.reset()
        self.animationLeft.reset()
    
    def goLeft(self):
        self.xSpeed = -BASE_X_SPEED
        
    def goRight(self):
        self.xSpeed = BASE_X_SPEED
        
    def jump(self):
        self.ySpeed = -BASE_Y_SPEED
        