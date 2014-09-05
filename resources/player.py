# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from game.actors import Actor
from game.animation import FilesAnimation
from game.animation import FlippedAnimation
from game.sound import soundsStore
from game.effects import FadingTextEffect

import logging

logger = logging.getLogger(__name__)

BASE_X_SPEED = 4 * 100
BASE_Y_SPEED = 8 * 100

SCREEN_BORDER_X = 300
SCREEN_BORDER_Y = 180

COLLISION_CACHE_EXTEND = 40
COLLISION_CACHE_THRESHOLD = 10


class Player(Actor):
    def __init__(self, parentMap, fromTile, actorType, x=0, y=0, w=None, h=None):
        Actor.__init__(self, parentMap, fromTile, actorType, x, y, 52, 66)
        self.xSpeed = self.ySpeed = 0
        self.animationLeft = FilesAnimation('data/actors/player1/player*.png', 2, 8)
        self.animationLeft.associateSound(4, soundsStore.get('foot_left'))
        self.animationLeft.associateSound(12, soundsStore.get('foot_right'))
        self.animationRight = FlippedAnimation(self.animationLeft)
        self.animation = self.animationRight
        self.keys = {}
        self.collisionsCache = None  # First is objects collisions cache, second is actors collisions cache
        self.cachedX = self.cachedY = -100000
        self.updateCacheCount = 0
        
        
        # What the player has
        self.hasYellowKey = False
        
    def resetCollisionsCache(self):
        logger.debug('Reseting collision cache')
        self.collisionsCache = None
        self.cachedX, self.cachedY =  self.rect.x, self.rect.y  # Will be updated on this possition
        
        self.updateCacheCount += 1
        logger.debug('Cache will be updated for {} time'.format(self.updateCacheCount))
        
    def updateCollisionCache(self):
        if abs(self.cachedX - self.rect.x) > COLLISION_CACHE_THRESHOLD or abs(self.cachedY - self.rect.y) > COLLISION_CACHE_THRESHOLD:
            self.resetCollisionsCache()
            
        if self.collisionsCache is None:
            logger.debug('Updating collisions cache for objects and actors')
            self.collisionsCache = (
                self.parentMap.getPossibleCollisions(self.rect, COLLISION_CACHE_EXTEND, COLLISION_CACHE_EXTEND),
                self.parentMap.getPossibleActorsCollisions(self.rect, COLLISION_CACHE_EXTEND, COLLISION_CACHE_EXTEND, exclude=self)
            )
            

    def getCollisions(self):
        self.updateCollisionCache()
        return self.parentMap.getCollisions(self.rect, self.collisionsCache[0])
    
    def getActorsCollisions(self):
        self.updateCollisionCache()
        return self.parentMap.getActorsCollisions(self.rect, self.collisionsCache[1])

    def checkXCollisions(self, offset):
        if offset == 0:
            return
        for c in self.getCollisions():
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
        
        for c in self.getCollisions():
            self.ySpeed = 0
            colRect = c[0]
            if offset > 0:
                if self.rect.bottom > colRect.top - 1:
                    self.rect.bottom = colRect.top - 1
            else:
                if self.rect.top < colRect.bottom + 1:
                    self.rect.top = colRect.bottom + 1

    def checkActionsOnCollision(self):
        for c in self.getCollisions():
            colRect, element, layer = c
            if element.lethal is True:
                # Die!! :-)
                pass
            if element.hasProperty('needsYellowKey'):
                if self.hasYellowKey:
                    logger.debug('We have the yellow key and we are colliding with a yellow key needing brick!')
                    layer.removeObjectAt(colRect.x, colRect.y)
                    self.resetCollisionsCache()
                    soundsStore.get('open_lock').play()
                else:
                    self.parentMap.addEffect('jqntlla', FadingTextEffect(colRect.x-50, colRect.y, 'Look for Yellow Key'))

    def move(self, xOffset, yOffset):
        if xOffset == 0 and yOffset == 0:
            pass  # Is something pushes this, this will be calculated elsewhere
        else:
            #self.resetCollisionsCache()
            if xOffset:
                self.rect.left += xOffset
                self.rect.clamp_ip(self.boundary)
                self.checkActionsOnCollision()
                self.checkXCollisions(xOffset)
            if yOffset:
                self.rect.top += yOffset
                self.rect.clamp_ip(self.boundary)
                self.checkActionsOnCollision()
                self.checkYCollisions(yOffset)

    def calculateGravity(self):
        if self.ySpeed == 0:
            self.ySpeed = 800  # Faster than falling platforms or it will be doing "strange things"
        else:
            # Temporary to tests
            if self.ySpeed < 1600:
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

        if self.xSpeed != 0 or self.ySpeed != 0:
            for c in self.getActorsCollisions():
                actorRect, actor, actorLayer = c
                actor.notify(self, 'hit')
            
        return True  # IF we return false, we will get removed!! :)

    def draw(self, toSurface):
        if self.ySpeed == 0:
            self.animation.play()
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
        
       
    def notify(self, sender, message):
        if message == 'YellowKey':
            logger.debug('Player has got yellow key')
            self.hasYellowKey = True
        elif message == 'moved':
            self.updateCollisionCache()

soundsStore.storeSoundFile('foot_left', 'step_grass_l.ogg', volume=0.3)
soundsStore.storeSoundFile('foot_right', 'step_grass_r.ogg', volume=0.3)
soundsStore.storeSoundFile('open_lock', 'open_lock.ogg')