# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import struct
import pygame
import os
from resources import paths
from resources.maps.tiles import Tile
from resources.maps.objects import ObjectWithPath
from resources.maps.utils import loadProperties
from resources.maps.utils import checkTrue

from resources.maps.actors import actorsFactory

import logging

logger = logging.getLogger(__name__)


######################
# Layer              #
######################
class Layer(object):
    LAYER_TYPE = 'default'
    EMPTY_TILE = Tile(None, 0, None)

    def __init__(self, parentMap=None, layerType=None, properties=None):
        self.name = None
        self.layerType = layerType if layerType is not None else self.LAYER_TYPE
        self.parentMap = parentMap
        self.visible = True
        self.holder = self.parallax = False
        self.parallaxFactor = ()
        self.properties = {}
        self.setProperties(properties)

    def setProperties(self, properties):
        if properties is not None:
            self.properties = properties
        # Set custom "flags" based on properties
        self.updateAttributes()

    def updateAttributes(self):
        self.visible = checkTrue(self.properties.get('visible', 'True'))
        self.holder = checkTrue(self.properties.get('holder', 'False'))
        self.actor = checkTrue(self.properties.get('actors', 'False'))
        self.parallax = checkTrue(self.properties.get('parallax', 'False'))
        
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
        x, y = y, x  # Avoid pylint unused
        return Layer.EMPTY_TILE

    def isVisible(self):
        return self.visible

    # Collisions
    def getCollisions(self, rect):
        del rect   # Avoid pylint unused
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


######################
# DynamicLayer       #
######################
class DynamicLayer(Layer):
    LAYER_TYPE = 'dynamic'

    def __init__(self, parentMap=None, layerType=None, properties=None):
        Layer.__init__(self, parentMap, layerType, properties)
        self.width = self.height = 0
        self.tilesLayer = None
        self.paths = {}
        self.platforms = {}

    def load(self, node):
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])

        self.setProperties(loadProperties(node.find('properties')))
        tilesLayerName = self.properties.get('layer', None)

        self.tilesLayer = self.parentMap.getLayer(tilesLayerName)

        self.paths = {}
        self.platforms = {}

        for obj in node.findall('object'):
            if obj.attrib['type'] == 'path':  # This is a path, store it in pathList
                name = obj.attrib['name']
                properties = loadProperties(obj.find('properties'))
                polyline = [[int(v) for v in i.split(',')] for i in obj.find('polyline').attrib['points'].split(' ')]

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

                    self.paths[name] = paths.Path(segments, properties)

                    logger.debug('Path {} {}'.format(name, self.paths[name]))
            elif obj.attrib['type'] == 'platform':
                if self.tilesLayer is None:
                    logger.error('Linking to an unexistent layer: {}. Skypped'.format(tilesLayerName))
                    continue

                name = obj.attrib['name']
                properties = loadProperties(obj.find('properties'))
                startX, startY = int(obj.attrib['x']), int(obj.attrib['y'])
                width, height = int(obj.attrib.get('width', self.parentMap.tileWidth)), int(obj.attrib.get('height', self.parentMap.tileHeight))
                tiles = []

                for y in xrange(startY, startY+height, self.parentMap.tileHeight):
                    t = []
                    for x in xrange(startX, startX+width, self.parentMap.tileWidth):
                        t.append(self.tilesLayer.getTileAt(x, y))
                    tiles.append(t)

                p = ObjectWithPath(self, startX, startY, width, height, properties.get('path', None), tiles, checkTrue(properties.get('sticky', False)))
                self.platforms[obj.attrib['name']] = p

                logger.debug('Platform {}'.format(p))

            # Get obj properties to know that is this
        # After loading, add pathList to Platforms
        erroneous = []
        for k, p in self.platforms.iteritems():
            try:
                p.path = self.paths[p.path]
            except KeyError:
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

    def getObject(self, objecName):
        return self.platforms.get(objecName)

    def getPath(self, pathName):
        return self.paths.get(pathName)

    def __iter__(self):
        for obj in self.platforms.itervalues():
            yield obj

    def __unicode__(self):
        return 'Dinamyc Layer'


class ImageLayer(Layer):
    LAYER_TYPE = 'image'

    def __init__(self, parentMap=None, layerType=None, properties=None):
        Layer.__init__(self, parentMap, layerType, properties)
        self.width = self.height = 0
        self.image_path = self.image = None
        self.cached_size = (-1, -1)
        self.cached_image = None

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


class ActorsLayer(Layer):
    LAYER_TYPE = 'actors'

    def __init__(self, parentMap, arrayLayer):
        Layer.__init__(self, parentMap)

        self.name = arrayLayer.name
        self.width = self.height = 0
        self.actorList = []
        self.setProperties(arrayLayer.properties)

        logger.debug('Adding actors from {}'.format(arrayLayer))
        # Sort actors by type, we can later iterate this dictionary
        for actor in arrayLayer:
            x, y, actorType = actor[0], actor[1], actor[2].getProperty('type')
            if actorType is None:
                logger.error('Found an actor without type: {} (ignored)'.format(actorType))
                continue
            aClass = actorsFactory.getActor(actorType)
            if aClass is None:
                logger.error('Found an unregistered actor class: {}'.format(actorType))
                continue
            self.actorList.append(aClass(self.parentMap, actorType, x, y))

        logger.debug(unicode(self))
        
    def onDraw(self, toSurface, x, y, width, height):
        for actor in self.actorList:
            actor.draw(toSurface)
        
    def onUpdate(self):
        for actor in self.actorList:
            actor.update()
            
    def getCollisions(self, rect):
        for actor in self.actorList:
            if actor.collide(rect):
                yield (actor.getRect(), actor)

    def getActors(self, actorType=None):
        for actor in self.actorList:
            if actorType is None:
                yield actor
            elif actor.actorType == actorType:
                yield actor
