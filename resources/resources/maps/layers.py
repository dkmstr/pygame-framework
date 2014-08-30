# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import struct
import pygame
import os
from resources import paths
from tiles import Tile
from objects import ObjectWithPath
from utils import loadProperties

import logging

logger = logging.getLogger(__name__)


######################
# Layer              #
######################
class Layer(object):
    LAYER_TYPE = 'default'
    EMPTY_TILE = Tile(None, 0, None)

    def __init__(self, parentMap=None, layerType=None, properties={}):
        self.name = None
        self.layerType = layerType if layerType is not None else self.LAYER_TYPE
        self.parentMap = parentMap
        self.setProperties(properties)

    def setProperties(self, properties):
        self.properties = properties
        # Set custom "flags" based on properties
        self.updateAttributes()

    def updateAttributes(self):
        self.visible = self.properties.get('visible', 'True') == 'True'
        self.holder = self.properties.get('holder', 'False') == 'True'
        self.parallax = self.properties.get('parallax', 'False') == 'True'
        self.parallaxFactor = (
            int(self.properties.get('parallax_factor_x', '100')),
            int(self.properties.get('parallax_factor_y', '100'))
        )

    def load(self, node):
        pass

    def update(self):
        self.onUpdate()

    def onUpdate(self):
        pass

    # Draw method for layer, better override "on_draw" so we can
    # calculate commono things here (as a parallax efect, for example)
    def draw(self, toSurface, x=0, y=0, width=0, height=0):
        if self.parallax is True:
            x = x * self.parallaxFactor[0] / 100
            y = y * self.parallaxFactor[1] / 100

        width = toSurface.get_width() if width <= 0 else width
        height = toSurface.get_height() if height <= 0 else height

        self.onDraw(toSurface, x, y, width, height)

    def onDraw(self, toSurface, x, y, width, height):
        pass

    def getType(self):
        return self.layerType

    def getTileAt(self, x, y):
        return Layer.EMPTY_TILE

    def isVisible(self):
        return self.visible

    # Collisions
    def getCollisions(self, rect):
        return ()

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this layer
        '''
        return self.properties.get(propertyName)


######################
# ArrayLayer         #
######################
class ArrayLayer(Layer):
    LAYER_TYPE = 'array'

    def load(self, node):
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])

        self.setProperties(loadProperties(node.find('properties')))

        data = node.find('data')
        if data.attrib['encoding'] != 'base64':
            raise Exception('No base 64 encoded')
        self.data = struct.unpack('<' + 'I'*(self.width*self.height), base64.b64decode(data.text))

    def onDraw(self, toSurface, x, y, width, height):
        tiles = self.parentMap.tiles
        tileWidth = self.parentMap.tileWidth
        tileHeight = self.parentMap.tileHeight

        xStart, xLen = x / tileWidth, (width + tileWidth - 1) / tileWidth + 1
        yStart, yLen = y / tileHeight, (height + tileHeight - 1) / tileHeight + 1

        if xStart > width or yStart > height:
            return

        xOffset = x % tileWidth
        yOffset = y % tileHeight

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
            pos = self.width * y
            for x in xrange(xStart, xEnd):
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


######################
# DynamicLayer       #
######################
class DynamicLayer(Layer):
    LAYER_TYPE = 'dynamic'

    def load(self, node):
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])

        self.setProperties(loadProperties(node.find('properties')))
        tilesLayerName = self.properties.get('layer', None)

        self.tiles_layer = self.parentMap.getLayer(tilesLayerName)
        if self.tiles_layer is None:
            logger.error('Linking to an unexistent layer: {}'.format(tilesLayerName))
            return

        pathList = {}
        self.platforms = {}

        for obj in node.findall('object'):
            if obj.attrib['type'] == 'path':  # This is a path, store it in pathList
                name = obj.attrib['name']
                properties = loadProperties(obj.find('properties'))
                polyline = [[int(v) for v in i.split(',')] for i in obj.find('polyline').attrib['points'].split(' ')]
                step = int(properties.get('step', '1'))
                bounce = properties.get('bounce', 'False') == 'False'

                if len(polyline) > 0:
                    origX, origY = int(obj.attrib['x']), int(obj.attrib['y'])
                    x, y = origX + polyline[0][0], origY + polyline[0][1]
                    polyline = polyline[1:]

                    segments = []
                    for line in polyline:
                        xf, yf = origX + line[0], origY + line[1]
                        segments.append(paths.PathSegment(x, y, xf-x, yf-y))
                        x = origX + line[0]
                        y = origY + line[1]

                    pathList[name] = paths.Path(segments, step, bounce)

                    logger.debug('Path {} {}'.format(name, pathList[name]))
            elif obj.attrib['type'] == 'platform':
                name = obj.attrib['name']
                properties = loadProperties(obj.find('properties'))
                startX, startY = int(obj.attrib['x']), int(obj.attrib['y'])
                width, height = int(obj.attrib.get('width', self.parentMap.tileWidth)), int(obj.attrib.get('height', self.parentMap.tileHeight))
                tiles = []

                for y in xrange(startY, startY+height, self.parentMap.tileHeight):
                    t = []
                    for x in xrange(startX, startX+width, self.parentMap.tileWidth):
                        t.append(self.tiles_layer.getTileAt(x, y))
                    tiles.append(t)

                p = ObjectWithPath(startX, startY, width, height, properties.get('path', None), tiles, properties.get('sticky', False))
                self.platforms[obj.attrib['name']] = p

                logger.debug('Platform {}'.format(p))

            # Get obj properties to know that is this
        # After loading, add pathList to Platforms
        erroneous = []
        for k, p in self.platforms.iteritems():
            try:
                p.path = pathList[p.path]
            except:
                logger.error('Path {} doesn\'t exists!!'.format(p.path))
                erroneous.append(k)

        for k in erroneous:
            del self.platforms[k]

    def onDraw(self, toSurface, x, y, width, height):
        for obj in self.platforms.itervalues():
            obj.draw(toSurface, x, y)

    def onUpdate(self):
        for obj in self.platforms.itervalues():
            obj.update()

    def getCollisions(self, rect):
        for obj in self.platforms.itervalues():
            if obj.collide(rect):
                yield (obj.getRect(), obj)

    def __iter__(self):
        for obj in self.platforms.itervalues():
            yield obj

    def __unicode__(self):
        return 'Dinamyc Layer'


class ImageLayer(Layer):
    LAYER_TYPE = 'image'

    def load(self, node):
        logger.debug('Loading image Layer')
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])
        self.image_path = os.path.join(self.parentMap.mapPath, node.find('image').attrib['source'])
        self.image = (pygame.image.load(self.image_path))
        self.cached_size = (-1, -1)

        self.setProperties(loadProperties(node.find('properties')))
        logger.debug('Loaded image Layer {}'.format(self))

    def onDraw(self, toSurface, x, y, width, height):
        if width != self.cached_size[0] or height != self.cached_size[1]:
            logger.debug('Rescaling image layer to {}x{}'.format(width, height))
            self.cached_size = (width, height)
            self.cached_image = pygame.transform.scale(self.image, self.cached_size).convert()

        toSurface.blit(self.cached_image, (0, 0))

    def __unicode__(self):
        return 'Image Layer: {}'.format(self.image_path)
