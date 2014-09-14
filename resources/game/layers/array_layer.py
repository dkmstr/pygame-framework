# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import base64
import struct
import itertools
from game.util import loadProperties
from game.layers.layer import Layer

import logging

logger = logging.getLogger(__name__)


class ArrayLayer(Layer):
    LAYER_TYPE = 'array'

    def __init__(self, parentMap=None, layerType=None, properties=None):
        Layer.__init__(self, parentMap, layerType, properties)
        self.width = self.height = 0
        self.data = []

    def load(self, node):
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])

        self.setProperties(loadProperties(node.find('properties')))

        data = node.find('data')
        if data.attrib['encoding'] != 'base64':
            raise Exception('No base 64 encoded')
        self.data = list(struct.unpack('<' + 'I'*(self.width*self.height), base64.b64decode(data.text)))
        
        # Scan data for "flipped" tiles and request parentMap to append a flipped tile to it
        for i in xrange(len(self.data)):
            tileId = self.data[i] 
            if tileId & 0xF0000000 != 0:
                logger.debug('Fipped tile found!: {:X}'.format(tileId&0xF0000000))
                # Tiles can be flipped on TILED, for now, we ignore this and all tiles ar got as they are
                # const unsigned FLIPPED_HORIZONTALLY_FLAG = 0x80000000;
                # const unsigned FLIPPED_VERTICALLY_FLAG   = 0x40000000;
                # const unsigned FLIPPED_DIAGONALLY_FLAG   = 0x20000000;
                flipX = flipY = rotate = False
                if tileId & 0x80000000 != 0:
                    flipX = True
                if tileId & 0x40000000 != 0:
                    flipY = True
                if tileId & 0x20000000 != 0:
                    rotate = True
                self.data[i] = self.parentMap.addTileFromTile(tileId&0x0FFFFFFF, flipX, flipY, rotate)
                
    def onDraw(self, toSurface, rect):
        tiles = self.parentMap.tiles
        tileWidth = self.parentMap.tileWidth
        tileHeight = self.parentMap.tileHeight

        # Calculate positions inside tile array
        xStart, xLen = rect.x / tileWidth, (rect.width + tileWidth - 1) / tileWidth + 1
        yStart, yLen = rect.y / tileHeight, (rect.height + tileHeight - 1) / tileHeight + 1

        # If drawing zone is outside map, skip
        # if xStart > self.width or yStart > self.height or xStart + xLen < 0 or yStart + yLen < 0:
        #    return

        # If start drawing outside screen, skip outside zone
        yPos = 0
        if yStart < 0:
            yLen += yStart
            yPos = -yStart * tileHeight
            yStart = 0
          
        xPos = 0  
        if xStart < 0:
            xLen += xStart
            xPos = -xStart * tileWidth
            xStart = 0
            
        xPos -= rect.x % tileWidth  # Offset inside first drawing tile
        yPos -= rect.y % tileHeight

        # Adjust ends so we don't go off limits
        xEnd = self.width if xStart+xLen > self.width else xStart+xLen
        yEnd = self.height if yStart+yLen > self.height else yStart+yLen

        drawingRect = pygame.Rect(xPos, yPos, tileWidth, tileHeight)

        for y in xrange(yStart, yEnd):
            pos = self.width * y
            drawingRect.x = xPos
            for tile in itertools.islice(self.data, pos+xStart, pos+xEnd):
                if tile > 0:
                    tiles[tile-1].draw(toSurface, drawingRect)
                drawingRect.x += tileWidth
            drawingRect.y += tileHeight

    def onUpdate(self):
        pass

    def getObjectAt(self, x, y):
        x /= self.parentMap.tileWidth
        y /= self.parentMap.tileHeight
        tile = self.data[y*self.width+x]
        if tile == 0:
            return Layer.EMPTY_TILE
        return self.parentMap.tiles[tile-1]
    
    def removeObjectAt(self, x, y):
        x /= self.parentMap.tileWidth
        y /= self.parentMap.tileHeight
        self.data[y*self.width+x] = 0
        

    def getCollisions(self, rect):
        tiles = self.parentMap.tiles
        tileWidth = self.parentMap.tileWidth
        tileHeight = self.parentMap.tileHeight

        xStart = rect.left / tileWidth
        xEnd = (rect.right + tileWidth - 2) / tileWidth
        yStart = rect.top / tileHeight
        yEnd = (rect.bottom + tileHeight - 2) / tileHeight

        for y in xrange(yStart, yEnd):
            if y < 0 or y >= self.height:  # Skips out of bounds rows
                continue
            pos = self.width * y
            for x in xrange(xStart, xEnd):
                if x < 0 or x >= self.width:  # Skips out of bounds columns
                    continue
                tile = self.data[pos+x]
                if tile > 0:
                    t = tiles[tile-1]
                    tileRect = t.getRect().move(x*tileWidth, y*tileHeight)
                    if tileRect.colliderect(rect):
                        yield (tileRect, t)

    def __iter__(self):
        '''
         Iterates over all non empty tiles of this map
         return (x, y, tile) where x,y are integers and tile is an Tile object
         x and 6 are "Absolute map coords in pixels"
        '''
        for y in xrange(0, self.height):
            pos = self.width * y
            for x in xrange(0, self.width):
                tile = self.data[pos+x]
                if tile > 0:
                    yield(x*self.parentMap.tileWidth, y*self.parentMap.tileHeight, self.parentMap.tiles[tile-1])

    def __unicode__(self):
        return 'ArrayLayer {}: {}x{} ({})'.format(self.name, self.width, self.height, self.properties)
