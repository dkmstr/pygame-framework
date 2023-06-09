# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from game.actors import Actor
from game.hud.score import ScoreableMixin
from game.animation import FilesAnimation
from game.animation import SpriteSheetAnimation
from game.animation import FlippedAnimation
from game.sound.sound import SoundsStore
from game.effects import FadingTextEffect
from game.effects import FadingMovingValueEffect
from game.collision_cache import WithCollisionCache

import logging

logger = logging.getLogger(__name__)

BASE_X_SPEED = 32 * 50
BASE_Y_SPEED = 16 * 100

SCREEN_BORDER_X = 300
SCREEN_BORDER_Y = 180

class Player(Actor, WithCollisionCache, ScoreableMixin):
    def __init__(self, parentLayer, fromTile, actorType, x=0, y=0, w=None, h=None):
        #Actor.__init__(self, parentMap, fromTile, actorType, x, y, 52, 66)
        Actor.__init__(self, parentLayer, fromTile, actorType, x, y)
        WithCollisionCache.__init__(self, parentLayer.parentMap,
                                    cachesActors=True,
                                    cachesObjects=True,
                                    cacheThreshold=32,
                                    collisionRangeCheck=256)
        # Used sounds
        SoundsStore.store.storeSoundFile('foot_left', 'step_grass_l.ogg', volume=0.3)
        SoundsStore.store.storeSoundFile('foot_right', 'step_grass_r.ogg', volume=0.3)
        SoundsStore.store.storeSoundFile('open_lock', 'open_lock.ogg')
        SoundsStore.store.storeSoundFile('get_coin', 'coin.ogg', volume=0.2)
        SoundsStore.store.storeSoundFile('key', 'key.ogg')

        self.xSpeed = self.ySpeed = 0
        self.inLadder = False
        self.ladderX = -1000

        # self.animationLeft = FilesAnimation('data/actors/player1/player*.png', 2, 8)
        # self.animationUp = SpriteSheetAnimation('data/actors/player3-up.png', 48, 2, 7)
        self.animationUp = FilesAnimation('data/actors/characters/Blue_Back*.png', 6, 0)
        # self.animationLeft = SpriteSheetAnimation('data/actors/player3-side.png', 48, 2, 7)
        self.animationLeft = FilesAnimation('data/actors/characters/Blue_Left*.png', 6, 0)
        # self.animationLeft.associateSound(0, SoundsStore.store.get('foot_left'))
        # self.animationLeft.associateSound(2, SoundsStore.store.get('foot_right'))
        # self.animationRight = SpriteSheetAnimation('data/actors/viking/viking-walk.png', 70, 2, 0)
        self.animationRight = FlippedAnimation(self.animationLeft)
        # self.animationLeft = FlippedAnimation(self.animationRight)
        self.animation = self.animationRight
        self.keys = {}
        self.alive = True

        self.score = 0

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
            if element.isA('lethal'):
                # Die!! :-)
                self.parent.parentMap.addEffect('die', FadingTextEffect(colRect.centerx, colRect.y-10, 'DIE!!! :-)', 24))
                self.isAlive = False
                continue

            if element.isA('ladder'):
                inLadder = True

            if element.isA('collectable') is True:
                score, snd = int(element.getProperty('score', '0')), element.getProperty('sound')
                layer.removeObjectAt(colRect.x, colRect.y)
                if score is not None:
                    self.score += score
                    self.parent.parentMap.addEffect(None, FadingMovingValueEffect(colRect.x+colRect.width/2, colRect.y, score))

                if snd is not None:
                    try:
                        SoundsStore.store.get(snd).play()
                    except:
                        logger.error('Sound {} is not defined on SoundStore!'.format(snd))
                        pass


                if 'Key' in element.name:
                    self.hasYellowKey = True
                    SoundsStore.store.get('key').play()

                self.resetCollisionsCache()

            if element.isA('lock'):
                if element.getProperty('needs') == 'YellowKey' and self.hasYellowKey:
                    logger.debug('We have the yellow key and we are colliding with a yellow key needing brick!')
                    layer.removeObjectAt(colRect.x, colRect.y)
                    self.resetCollisionsCache()
                    SoundsStore.store.get('open_lock').play()
                else:
                    self.parent.parentMap.addEffect('jqntlla', FadingTextEffect(colRect.x+colRect.width/2, colRect.y-10, 'You need\nthe Yellow Key', 24))
                continue

        # Fire map triggers on our possition
        self.parent.parentMap.checkTriggers(self.getColRect())

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
            self.rect.centerx = self.ladderX
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
        rect = self.parent.parentMap.translateCoordinates(self.rect)
        self.animation.draw(toSurface, rect)
        #toSurface.fill((128, 128, 128, 128), (x+self.xOffset, y+self.yOffset, self.rect.width, self.rect.height), pygame.BLEND_RGBA_MAX)

    def updateMapDisplayPosition(self, renderer):
        w, h = renderer.getSize()

        boundariesX = (SCREEN_BORDER_X-self.rect.width, SCREEN_BORDER_X)
        boundariesY = (SCREEN_BORDER_Y-self.rect.height, SCREEN_BORDER_Y)

        xMap, yMap = self.parent.parentMap.getDisplayPosition()
        if xMap > self.rect.x - boundariesX[0] and xMap < self.rect.x:
            xMap = self.rect.x - boundariesX[0]
        elif xMap + w - self.rect.x < boundariesX[1]:
            xMap = self.rect.x - w + boundariesX[1]

        if yMap > self.rect.y - boundariesY[0] and yMap < self.rect.y:
            yMap = self.rect.y - boundariesY[0]
        elif yMap + h - self.rect.y < boundariesY[1]:
            yMap = self.rect.y - h + boundariesY[1]

        self.parent.parentMap.setDisplayPosition(xMap, yMap)

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
        self.inLadder = False
        self.xSpeed -= BASE_X_SPEED

    def goRight(self):
        self.inLadder = False
        self.xSpeed += BASE_X_SPEED

    def _checkLadderCollision(self):
        for c in self.getCollisions():
            if c[1].isA('ladder') is True:
                self.inLadder = True
                self.ladderX = c[0].centerx - self.xOffset

                return True
        return False

    def goUp(self):
        if self._checkLadderCollision():
            self.ySpeed = -BASE_X_SPEED

    def goDown(self):
        if self._checkLadderCollision():
            self.ySpeed = BASE_Y_SPEED

    def jump(self):
        # Jumpinng goes of ladders
        self.inLadder = False
        self.ySpeed = -BASE_Y_SPEED

    def isAlive(self):
        return self.isAlive

    def getScore(self):
        return self.score

    def notify(self, sender, message):
        if message == 'YellowKey':
            logger.debug('Player has got yellow key')
            self.hasYellowKey = True
        elif message in ('BronceCoin', 'SilverCoin', 'GoldCoin'):
            self.score += 1234
        elif message == 'moved':
            self.updateCollisionsCache()
