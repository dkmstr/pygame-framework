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
        self.lines = None
        self.lineOffsets = None

    def updateCacheLine(self, y):
        tiles = self.parentMap.tiles

        def tileAt(x):
            return self.data[y*self.width+x]-1

        self.lines[y] = [(x, tileAt(x)) for x in range(self.width) if tileAt(x) >= 0]

        self.lineOffsets[y] = [-1]*self.width

        curr = 0
        counter = 0
        for x, tile in self.lines[y]:
            while curr <= x:
                self.lineOffsets[y][curr] = counter
                curr += 1
            counter += 1

        logger.debug(self.lineOffsets[y])

    def updateAllCacheLines(self):
        self.lines = [[]] * self.height
        self.lineOffsets = [[]] * self.height
        for y in range(self.height):
            self.updateCacheLine(y)

    def load(self, node):
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])

        self.setProperties(loadProperties(node.find('properties')))

        data = node.find('data')
        if data.attrib['encoding'] != 'base64':
            raise Exception('No base 64 encoded')
        self.data = list(struct.unpack('<' + 'I'*(self.width*self.height), base64.b64decode(data.text)))

        cached = {} # So we got only 1 tile generated from 1 source and 1 transormation
        # Scan data for "flipped" tiles and request parentMap to append a flipped tile to it
        for i in range(len(self.data)):
            tileId = self.data[i]
            if tileId & 0xF0000000 != 0:
                if cached.get(tileId) is None:
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
                    self.data[i] = cached[tileId] = self.parentMap.addTileFromTile(tileId&0x0FFFFFFF, flipX, flipY, rotate)
                else:
                    self.data[i] = cached[tileId]

        # Fill line "strides" of not empty tiles
        self.updateAllCacheLines()

    def onDraw(self, renderer, rect):
        tiles = self.parentMap.tiles
        tileWidth = self.parentMap.tileWidth
        tileHeight = self.parentMap.tileHeight

        # Calculate positions inside tile array
        xStart, xLen = int(rect.x / tileWidth), int((rect.width + tileWidth - 1) / tileWidth + 1)
        yStart, yLen = int(rect.y / tileHeight),int((rect.height + tileHeight - 1) / tileHeight + 1)

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

        xPos -= rect.x % tileWidth + xStart * tileWidth  # Offset inside first drawing tile
        yPos -= rect.y % tileHeight

        # Adjust ends so we don't go off limits
        xEnd = self.width if xStart+xLen > self.width else xStart+xLen
        yEnd = self.height if yStart+yLen > self.height else yStart+yLen

        drawingRect = pygame.Rect(xPos, yPos, tileWidth, tileHeight)

        for y in range(yStart, yEnd):
            xo = self.lineOffsets[y][xStart]
            line = self.lines[y]
            if xo != -1:  # Maybe the line do not holds anything at all, skip it
                (x, tileId) = line[xo]
                pos = self.width * y

                for x, tileId in itertools.islice(line, xo, None):
                    if x >= xEnd:
                        break
                    drawingRect.x = xPos + x * tileWidth
                    tiles[tileId].draw(renderer, drawingRect)
            drawingRect.y += tileHeight

    def onUpdate(self):
        pass

    def getObjectAt(self, x, y):
        x //= self.parentMap.tileWidth
        y //= self.parentMap.tileHeight
        tile = self.data[y*self.width+x]
        if tile == 0:
            return Layer.EMPTY_TILE
        return self.parentMap.tiles[tile-1]

    def removeObjectAt(self, x, y):
        x //= self.parentMap.tileWidth
        y //= self.parentMap.tileHeight
        self.data[y*self.width+x] = 0
        self.updateCacheLine(y)

    def getCollisions(self, rect):
        tiles = self.parentMap.tiles
        tileWidth = self.parentMap.tileWidth
        tileHeight = self.parentMap.tileHeight

        xStart = rect.left // tileWidth
        xEnd = (rect.right + tileWidth - 2) // tileWidth
        yStart = rect.top // tileHeight
        yEnd = (rect.bottom + tileHeight - 2) // tileHeight

        for y in range(yStart, yEnd):
            if y < 0 or y >= self.height:  # Skips out of bounds rows
                continue
            pos = self.width * y
            for x in range(xStart, xEnd):
                if x < 0 or x >= self.width:  # Skips out of bounds columns
                    continue
                tile = self.data[pos+x]
                if tile > 0:
                    t = tiles[tile-1]
                    tileRect = t.getRect().move(x*tileWidth, y*tileHeight)
                    if tileRect.colliderect(rect):
                        yield (tileRect, t)

    def setTileAt(self, x, y, tileId):
        x //= self.parentMap.tileWidth
        y //= self.parentMap.tileHeight
        self.data[y*self.width+x] = tileId
        self.updateCacheLine(y)

    def __iter__(self):
        '''
         Iterates over all non empty tiles of this map
         return (x, y, tile) where x,y are integers and tile is an Tile object
         x and 6 are "Absolute map coords in pixels"
        '''
        for y in range(0, self.height):
            pos = self.width * y
            for x in range(0, self.width):
                tile = self.data[pos+x]
                if tile > 0:
                    yield(x*self.parentMap.tileWidth, y*self.parentMap.tileHeight, self.parentMap.tiles[tile-1])

    def __unicode__(self):
        return 'ArrayLayer {}: {}x{} ({})'.format(self.name, self.width, self.height, self.properties)
