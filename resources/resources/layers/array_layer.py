# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import struct
from resources.maps.utils import loadProperties
from resources.layers.layer import Layer

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
        self.data = struct.unpack('<' + 'I'*(self.width*self.height), base64.b64decode(data.text))

    def onDraw(self, toSurface, rect):
        tiles = self.parentMap.tiles
        tileWidth = self.parentMap.tileWidth
        tileHeight = self.parentMap.tileHeight

        xStart, xLen = rect.x / tileWidth, (rect.width + tileWidth - 1) / tileWidth + 1
        yStart, yLen = rect.y / tileHeight, (rect.height + tileHeight - 1) / tileHeight + 1

        # If drawing zone is outside map, skip
        # if xStart > self.width or yStart > self.height or xStart + xLen < 0 or yStart + yLen < 0:
        #    return

        xOffset = rect.x % tileWidth
        yOffset = rect.y % tileHeight

        xEnd = self.width if xStart+xLen > self.width else xStart+xLen
        yEnd = self.height if yStart+yLen > self.height else yStart+yLen

        for y in xrange(yStart, yEnd):
            pos = self.width * y
            for x in xrange(xStart, xEnd):
                if x >= 0 and y >= 0:
                    tile = self.data[pos+x]
                    if tile > 0:
                        tiles[tile-1].draw(toSurface, (x-xStart)*tileWidth-xOffset, (y-yStart)*tileHeight-yOffset)

    def onUpdate(self):
        pass

    def getTileAt(self, x, y):
        x /= self.parentMap.tileWidth
        y /= self.parentMap.tileHeight
        tile = self.data[y*self.width+x]
        if tile == 0:
            return Layer.EMPTY_TILE
        return self.parentMap.tiles[tile-1]

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
