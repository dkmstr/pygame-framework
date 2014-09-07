# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from game.actors import Actor
from game.animation import FilesAnimation
from game.animation import SpriteSheetAnimation
from game.animation import FlippedAnimation
from game.sound.sound import SoundsStore
from game.effects import FadingTextEffect
from game.collision_cache import WithCollisionCache

import logging

logger = logging.getLogger(__name__)

BASE_X_SPEED = 4 * 100
BASE_Y_SPEED = 8 * 100

SCREEN_BORDER_X = 300
SCREEN_BORDER_Y = 180

class Player(Actor, WithCollisionCache):
    def __init__(self, parentMap, fromTile, actorType, x=0, y=0, w=None, h=None):
        #Actor.__init__(self, parentMap, fromTile, actorType, x, y, 52, 66)
        Actor.__init__(self, parentMap, fromTile, actorType, x, y)
        WithCollisionCache.__init__(self, parentMap, 
                                    cachesActors=True, 
                                    cachesObjects=True, 
                                    cacheThreshold=32, 
                                    collisionRangeCheck=128)
        # Used sounds
        SoundsStore.store.storeSoundFile('foot_left', 'step_grass_l.ogg', volume=0.3)
        SoundsStore.store.storeSoundFile('foot_right', 'step_grass_r.ogg', volume=0.3)
        SoundsStore.store.storeSoundFile('open_lock', 'open_lock.ogg')
        
        self.xSpeed = self.ySpeed = 0
        self.inLadder = False
        
        # self.animationLeft = FilesAnimation('data/actors/player1/player*.png', 2, 8)
        self.animationUp = SpriteSheetAnimation('data/actors/player3-up.png', 48, 2, 7)
        self.animationLeft = SpriteSheetAnimation('data/actors/player3-side.png', 48, 2, 7)
        self.animationLeft.associateSound(3, SoundsStore.store.get('foot_left'))
        self.animationLeft.associateSound(6, SoundsStore.store.get('foot_right'))
        self.animationRight = FlippedAnimation(self.animationLeft)
        self.animation = self.animationRight
        self.keys = {}
        self.alive = True
        
        # What the player has
        self.hasYellowKey = False
        
    def getColRect(self):
        return self.rect.move(self.xOffset, self.yOffset)

    def checkXCollisions(self, offset):
        if offset == 0:
            return
        for c in self.getCollisions():
            colRect, obj, layer = c
            if obj.blocks is False:
                continue
            if offset > 0:
                self.rect.right = colRect.left - 1 - self.xOffset # Actor position is not exactly where it collides
            else:
                self.rect.left = colRect.right + 1 - self.xOffset  # Actor position is not exactly where it collides
            return True
        return False

    def checkYCollisions(self, offset):
        '''
        Our rect is not exactly where the animation is drawn, it's offseted
        '''
        if offset == 0:
            return

        for c in self.getCollisions():
            colRect, obj, layer = c
            if obj.blocks is False:
                continue
            self.ySpeed = 0
            if offset > 0:
                if self.rect.bottom > colRect.top - 1 - self.yOffset: # Actor position is not exactly where it collides
                    self.rect.bottom = colRect.top - 1 - self.yOffset
            else:
                if self.rect.top < colRect.bottom + 1 - self.yOffset: # Actor position is not exactly where it collides
                    self.rect.top = colRect.bottom + 1 - self.yOffset

    def checkActionsOnCollision(self):
        inLadder = False
        for c in self.getCollisions():
            colRect, element, layer = c
            if element.lethal is True:
                # Die!! :-)
                self.parentMap.addEffect('die', FadingTextEffect(colRect.x+colRect.width/2, colRect.y-10, 'DIE!!! :-)', 24))
                self.isAlive = False
            
            if element.ladder is True:
                inLadder = True
                
            if element.hasProperty('needsYellowKey'):
                if self.hasYellowKey:
                    logger.debug('We have the yellow key and we are colliding with a yellow key needing brick!')
                    layer.removeObjectAt(colRect.x, colRect.y)
                    self.resetCollisionsCache()
                    SoundsStore.store.get('open_lock').play()
                else:
                    self.parentMap.addEffect('jqntlla', FadingTextEffect(colRect.x+colRect.width/2, colRect.y-10, 'You need\nthe Yellow Key', 24))
                    
        # If ladder is true, maybe we haven't hanged on it
        if inLadder is False:
            self.inLadder = False

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
        if self.inLadder:
            return
        
        if self.ySpeed == 0:
            self.ySpeed = 800  # Faster than falling platforms or it will be doing "strange things"
        else:
            # Temporary to tests
            if self.ySpeed < 1600:
                self.ySpeed += 35

    def update(self):
        self.calculateGravity()
        if self.inLadder is True and self.ySpeed != 0:
            self.animation = self.animationUp
            self.animation.iterate()
        elif self.xSpeed != 0:
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
        import pygame
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
    def stopLeft(self):
        self.xSpeed += BASE_X_SPEED
        self.animationLeft.reset()
        
    def stopRight(self):
        self.xSpeed -= BASE_X_SPEED
        self.animationRight.reset()
        
    def stopUp(self):
        if self.inLadder:
            self.ySpeed  = 0
    
    def stopDown(self):
        if self.inLadder:
            self.ySpeed  = 0
    
    def stopJump(self):
        pass
    
    def goLeft(self):
        self.xSpeed -= BASE_X_SPEED
        
    def goRight(self):
        self.xSpeed += BASE_X_SPEED
        
    def _checkLadderCollision(self):
        for c in self.getCollisions():
            if c[1].ladder is True:
                self.inLadder = True
                return True
        return False
        
    def goUp(self):
        if self._checkLadderCollision():
            self.ySpeed = -BASE_X_SPEED
        
    def goDown(self):
        if self._checkLadderCollision():
            self.ySpeed = BASE_Y_SPEED
        
    def jump(self):
        self.ySpeed = -BASE_Y_SPEED
        
    def isAlive(self):
        return self.isAlive
       
    def notify(self, sender, message):
        if message == 'YellowKey':
            logger.debug('Player has got yellow key')
            self.hasYellowKey = True
        elif message == 'moved':
            self.updateCollisionsCache()
