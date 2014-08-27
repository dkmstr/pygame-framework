# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import os
import base64
import struct
import xml.etree.ElementTree as ET

from resources.util import resource_path

import logging

logger = logging.getLogger(__name__)


class Tile(object):
    def __init__(self, tileSet, tileId, surface, properties={}):
        self._tileSet = tileSet
        self._id = tileId
        self._orig_surface = self._surface = surface
        self.setProperties(properties)

    def setProperties(self, properties):
        self.properties = properties
        self.updateAttributes()

    def updateAttributes(self):
        '''
        Updates attributes of the object because properties was set
        '''
        self.sticky = self.properties.get('sticky', 'False') == 'True'
        self.delay = int(self.properties.get('delay', '0'))
        # Animation ids of tiles are relative to tileset
        if self.properties.get('animation') is not None:
            self.animated = True
            self.animation = [int(i) for i in self.properties.get('animation', '-1').split(',')]
            self.animation_orig_delay = self.animation_delay = int(self.properties.get('delay', '1'))
            self.animation_state = 0
            logger.debug('Added animation for tile {}: {}'.format(self._id, self.animation))
        else:
            self.animated = False
            self.animation = None
            self.animation_state = None

    def update(self):
        if self.animated is False:
            return
        self.animation_delay -= 1
        if self.animation_delay > 0:
            return
        self.animation_delay = self.animation_orig_delay
        if self.animation_state >= len(self.animation):
            self.animation_state = 0
            self.resetImage()
        else:
            self._surface = self._tileSet.getTile(self.animation[self.animation_state]).getImage()
            self.animation_state += 1

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName)

    def getImage(self):
        return self._surface

    def setImage(self, surface):
        self._surface = surface

    def resetImage(self):
        self._surface = self._orig_surface

    def id(self):
        return self._id

    def __unicode__(self):
        return 'Tile {} ({}x{}) ({})'.format(self._id, self._surface.get_width(), self._surface.get_height(), self.properties)


class MapObject(Tile):
    def __init__(self, tileId, surface, x, y, properties={}):
        super(MapObject, self).__init__(self, tileId, surface)
        self.x = x
        self.y = y


class Platform(MapObject):
    pass


class TileSet(object):
    def __init__(self, parentMap):
        self.name = None
        self.tilewidth = self.tileheight = self.tilespacing = 0
        self.image_path = ''
        self.image_width = self.image_heigth = 0
        self.firstgid = 0
        self.surface = None
        self.tiles = []
        self.animated_tiles = []
        self.properties = {}
        self.tiles_properties = {}
        self.parent_map = parentMap

    def __loadTilesProperties(self, node):
        self.tiles_properties = {}
        for t in node.findall('tile'):
            tid = int(t.attrib['id'])
            self.tiles_properties[tid] = Maps._loadProperties(t.find('properties'))

    def __loadTileSet(self, relativePath, node):
        image = node.find('image')

        self.name = node.attrib['name']
        self.tilewidth = int(node.attrib['tilewidth'])
        self.tileheight = int(node.attrib['tileheight'])
        self.tilespacing = int(node.attrib.get('spacing', 0))
        self.image_path = image.attrib['source']
        self.image_width = int(image.attrib['width'])
        self.image_height = int(image.attrib['height'])

        image = pygame.image.load(os.path.join(relativePath, self.image_path))

        image = image.convert_alpha()
        image.set_alpha(0, pygame.RLEACCEL)

        self.surface = image  # Store original surface

        self.properties = Maps._loadProperties(node.find('properties'))
        self.__loadTilesProperties(node)

    def __loadExternalTileset(self, relativePath, path):
        print "Loading tileset ", path
        tree = ET.parse(os.path.join(relativePath, path))
        root = tree.getroot()  # Map element
        self.__loadTileSet(relativePath, root)

    def load(self, relativePath, node):
        logger.debug('Loading tileset in path {}'.format(relativePath))
        if 'source' in node.attrib:
            self.__loadExternalTileset(relativePath, node.attrib['source'])
        else:
            self.__loadTileSet(relativePath, node)

        self.firstgid = int(node.attrib['firstgid'])

        logger.debug('Image path: {} {}x{}'.format(self.image_path, self.image_width, self.image_height))

        tilesPerRow = self.surface.get_width() / (self.tilewidth+self.tilespacing)
        tilesRows = self.surface.get_height() / (self.tileheight+self.tilespacing)

        self.tiles = range(tilesRows*tilesPerRow)  # Gens a dummy array of this len

        logger.debug('Tiles Grid size: {}x{}'.format(tilesPerRow, tilesRows))
        for y in xrange(tilesRows):
            for x in xrange(tilesPerRow):
                localTileId = y*tilesPerRow+x
                tileId = self.firstgid+localTileId-1
                # Map data contains global tile id (i.e., tile id + tileset firstgid - 1)
                # We keep here a reference to tiles in thow places (same reference in fact)
                self.tiles[localTileId] = Tile(self,
                    tileId,
                    self.surface.subsurface(((self.tilewidth+self.tilespacing)*x, (self.tileheight+self.tilespacing)*y, self.tilewidth, self.tileheight)),
                    self.tiles_properties.get(localTileId, {})
                )  # Creates reference

        self.animated_tiles = [i for i in self.tiles if i.animated]
        logger.debug(self.animated_tiles)

    def getTile(self, localTileId):
        return self.tiles[localTileId]

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName)

    def update(self):
        for t in self.animated_tiles:
            t.update()

    def __unicode__(self):
        return 'Tileset {}: {}x{} ({})'.format(self.name, self.tilewidth, self.tileheight, self.properties)


class Layer(object):
    EMPTY_TILE = Tile(None, 0, None)

    def __init__(self, name, layerType, properties={}):
        self.name = name
        self.type = layerType
        self.setProperties(properties)

    def setProperties(self, properties):
        self.properties = properties
        # Set custom "flags" based on properties

    def updateAttributes(self):
        self.visible = self.properties.get('visible', 'True') == 'True'

    def update(self):
        pass

    def draw(self):
        pass

    def getType(self):
        return self.type

    def getTileAt(self, x, y):
        return Layer.EMPTY_TILE

    def isVisible(self):
        return self.visible

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this layer
        '''
        return self.properties.get(propertyName)


class ArrayLayer(Layer):
    LAYER_TYPE = 'array'

    def __init__(self, name, parentMap, properties={}):
        super(ArrayLayer, self).__init__(name, ArrayLayer.LAYER_TYPE, properties)
        self.parentMap = parentMap

    def loadFromXml(self, node):
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])
        data = node.find('data')
        if data.attrib['encoding'] != 'base64':
            raise Exception('No base 64 encoded')
        self.data = struct.unpack('<' + 'I'*(self.width*self.height), base64.b64decode(data.text))

    def draw(self, surface, x=0, y=0, width=0, height=0):
        tiles = self.parentMap.tiles
        tileWidth = self.parentMap.tilewidth
        tileHeight = self.parentMap.tileheight

        width = surface.get_width() if width <= 0 else width
        height = surface.get_height() if height <= 0 else height

        xStart, xLen = x / tileWidth, (width + tileWidth - 1) / tileWidth + 1
        yStart, yLen = y / tileHeight, (height + tileHeight - 1) / tileHeight + 1

        if xStart > width or yStart > height:
            return

        xOffset = x % tileWidth
        yOffset = y % tileHeight

        xEnd = self.width if xStart+xLen > self.width else xStart+xLen
        yEnd = self.height if yStart+yLen > self.height else yStart+yLen

        for y in xrange(yStart, yEnd):
            for x in xrange(xStart, xEnd):
                if x >= 0 and y >= 0:
                    tile = self.data[y*self.width+x]
                    if tile > 0:
                        surface.blit(tiles[tile-1].getImage(), ((x-xStart)*tileWidth-xOffset, (y-yStart)*tileHeight-yOffset))

    def update(self):
        super(ArrayLayer, self).update()

    def getTileAt(self, x, y):
        x /= self.parentMap.tileWidth
        y /= self.parentMap.tileHeight
        tile = self.data[y*self.width+x]
        if tile == 0:
            return Layer.EMPTY_TILE
        return self.parentMap.tiles[tile-1]

    def __unicode__(self):
        return 'ArrayLayer {}: {}x{} ({})'.format(self.name, self.width, self.height, self.properties)


class DynamicLayer(Layer):
    LAYER_TYPE = 'dynamic'

    def __init__(self, name, properties={}):
        super(DynamicLayer, self).__init__(name, DynamicLayer.LAYER_TYPE, properties)
        self.objects = []


class Map(object):
    def __init__(self, mapId, path, properties={}):
        self.id = mapId
        self.path = resource_path(path)
        self.reset()

    def __getLayers(self, layersNames):
        if layersNames is None:
            layersNames = self.layers_names
        return layersNames

    def reset(self, fromNode=None):
        self.width = self.height = self.tilewidth = self.tileheight = 0
        self.tilesets = {}
        self.layers_names = []
        self.holders_names = []
        self.layers = {}
        self.tiles = []
        self.properties = {}
        if fromNode is not None:
            self.width = int(fromNode.attrib['width'])
            self.height = int(fromNode.attrib['height'])
            self.tilewidth = int(fromNode.attrib['tilewidth'])
            self.tileheight = int(fromNode.attrib['tileheight'])
            self.properties = Maps._loadProperties(fromNode.find('properties'))

    def load(self):
        mapPath = os.path.dirname(self.path)

        tree = ET.parse(self.path)
        root = tree.getroot()  # Map element

        logger.debug('Loading map "{}" in folder "{}"'.format(self.id, mapPath))

        self.reset(root)

        for tileSet in root.findall('tileset'):
            ts = TileSet(self)
            ts.load(mapPath, tileSet)

            self.tilesets[ts.name] = ts

            self.tiles.extend(ts.tiles)

            # Now load map data into layers, we understand right now only base 64
            # This loads the standard tiles layers
            for layer in root.findall('layer'):
                l = ArrayLayer('tmpName', self, properties=Maps._loadProperties(layer.find('properties')))
                l.loadFromXml(layer)
                # Just a holder
                self.addLayer(l)

            # Now load "object" layers and convert them to DynamicLayer

    def addLayer(self, layer):
        if layer.getProperty('holder') == 'True':
            logger.debug('Layer {} is a holder layer'.format(layer.name))
            self.holders_names.append(layer.name)
        else:
            self.layers_names.append(layer.name)
            self.layers[layer.name] = layer

    def getLayer(self, layerName):
        return self.layers[layerName]

    def draw(self, surface, x=0, y=0, width=0, height=0, layersNames=None):
        layersNames = self.__getLayers(layersNames)

        for layerName in layersNames:
            self.layers[layerName].draw(surface, x, y, width, height)

    def update(self, layersNames=None):
        layersNames = self.__getLayers(layersNames)

        # Keep order intact
        for layerName in layersNames:
            self.layers[layerName].update()

        for ts in self.tilesets.itervalues():
            ts.update()

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this map
        '''
        return self.properties.get(propertyName)

    def __unicode__(self):
        return 'Map {}: {}x{} with tile of  ({})'.format(self.path, self.width, self.height, self.tilewidth, self.tileheight, self.properties)


# Loads a TMX file
# TMX properties that will be used:
# For layer:
#   * holder: Defaults to False
#     Indicates that this layer will never been drawn
#     This will be used as a "holder" for "object layers" tiles/sprites
#   * collission: Defaults to False
#     If set to false, collisions against this map will not been check against this layer
# Object layers are used this way: (objectgroups)
#   Rects define the "source tiles" for an object (platform or not)
#   polylines defines paths
#   Object types:
#     * platform, Object that moves and translates the "holding" objects with it
#     * path, Used to describe a path, not drawn (must be set in polilynes for maybe future increased use of this)
#     * object, Simple object. If no type is specified, this is the default type for objects
#   Objects properties:
#     * speed: Speed for this object (used by moving platforms)
#     * path: specifies the path "object" that will describe the movement of this (right now, polylines)
#     * layer: For object and platform types is required, and indicates where to get from the "sprites"

class Maps(object):
    def __init__(self):
        self._maps = {}

    def add(self, mapId, path):
        self._maps[mapId] = Map(mapId, path)

    @staticmethod
    def _loadProperties(node):
        props = {}
        if node is not None:
            for p in node.findall('property'):
                logger.debug('Found property {}={}'.format(p.attrib['name'], p.attrib['value']))
                props[p.attrib['name']] = p.attrib['value']
        return props

    def load(self, mapId=None, force=False):
        if mapId is None:
            for mId in self._maps:
                self.load(mId, force)
            return

        if mapId not in self._maps:
            return False

        m = self._maps[mapId]
        m.load()

    def get(self, mapId):
        return self._maps[mapId]

    def __unicode__(self):
        r = ''
        for v in self._maps:
            r += unicode(v)
