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
    def __init__(self, name, tilewidth, tileheight, tilespacing, image_path, image_width=0, image_height=0):
        self.name = name
        self.tilewidth = tilewidth
        self.tileheight = tileheight
        self.tilespacing = tilespacing
        self.image_path = image_path
        self.image_width = image_width
        self.image_heigth = image_height
        self.firstgid = 0
        self.surface = None
        self.tiles = []
        self.animated_tiles = []
        self.properties = {}
        self.tiles_properties = {}

    @staticmethod
    def fromXml(node):
        image = node.find('image')
        return TileSet(
            node.attrib['name'],
            int(node.attrib['tilewidth']),
            int(node.attrib['tileheight']),
            int(node.attrib.get('spacing', 0)),
            image.attrib['source'],
            int(image.attrib['width']),
            int(image.attrib['height'])
        )

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

    def __init__(self, name, tilemap, data, width=0, height=0, properties={}):
        super(ArrayLayer, self).__init__(name, ArrayLayer.LAYER_TYPE, properties)
        self.width = width
        self.height = height
        self.data = data
        self.tilemap = tilemap

    def draw(self, surface, x=0, y=0, width=0, height=0):
        tiles = self.tilemap.tiles
        tileWidth = self.tilemap.tilewidth
        tileHeight = self.tilemap.tileheight

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
        x /= self.tilemap.tileWidth
        y /= self.tilemap.tileHeight
        tile = self.data[y*self.width+x]
        if tile == 0:
            return Layer.EMPTY_TILE
        return self.tilemap.tiles[tile-1]

    def __unicode__(self):
        return 'ArrayLayer {}: {}x{} ({})'.format(self.name, self.width, self.height, self.properties)


class DynamicLayer(Layer):
    LAYER_TYPE = 'dynamic'

    def __init__(self, name, properties={}):
        super(DynamicLayer, self).__init__(name, DynamicLayer.LAYER_TYPE, properties)
        self.objects = []


class Map(object):
    def __init__(self, path, properties={}):
        self.path = resource_path(path)
        self.width = self.height = 0
        self.tilewidth = self.tileheight = 0
        self.tilesets = {}
        self.tiles = []
        self.layers_names = []
        self.layers = {}
        self.properties = properties

    def __getLayers(self, layersNames):
        if layersNames is None:
            layersNames = self.layers_names
        return layersNames

    def getLayer(self, layerName):
        return self.layers[layerName]

    def draw(self, surface, x=0, y=0, width=0, height=0, layersNames=None):
        layersNames = self.__getLayers(layersNames)

        for layerName in layersNames:
            self.layers[layerName].draw(surface, x, y, width, height)

    def update(self, layersNames=None):
        layersNames = self.__getLayers(layersNames)

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
        self._maps[mapId] = Map(path)

    @staticmethod
    def __loadProperties(node):
        props = {}
        if node is not None:
            for p in node.findall('property'):
                logger.debug('Found property {}={}'.format(p.attrib['name'], p.attrib['value']))
                props[p.attrib['name']] = p.attrib['value']
        return props

    @staticmethod
    def __loadTilesProperties(tileSet):
        props = {}
        for t in tileSet.findall('tile'):
            tid = int(t.attrib['id'])
            logger.debug('Found tile {}'.format(tid))
            props[tid] = Maps.__loadProperties(t.find('properties'))
            logger.debug('Properties: {}'.format(tid))
        return props

    @staticmethod
    def __getTileSetInfo(tileSet):
        print "Loading tileset ", tileSet
        tree = ET.parse(tileSet)
        root = tree.getroot()  # Map element
        ts = TileSet.fromXml(root)

        ts.properties = Maps.__loadProperties(root.find('properties'))
        ts.tiles_properties = Maps.__loadTilesProperties(root)

    def load(self, mapId=None, force=False):
        if mapId is None:
            for mId in self._maps:
                self.load(mId, force)
            return

        if mapId not in self._maps:
            return False

        m = self._maps[mapId]

        # Extract path from file
        mapPath = os.path.dirname(m.path)

        tree = ET.parse(m.path)
        root = tree.getroot()  # Map element

        logger.debug('Loading map {} in folder {}'.format(mapId, mapPath))

        # Get general m info
        m.width = int(root.attrib['width'])
        m.height = int(root.attrib['height'])
        m.tilewidth = int(root.attrib['tilewidth'])
        m.tileheight = int(root.attrib['tileheight'])
        m.layers_names = []
        m.layers = {}
        m.tiles = []
        m.properties = Maps.__loadProperties(root.find('properties'))

        # Locate tilesets
        for tileSet in root.findall('tileset'):
            if 'source' in tileSet.attrib:
                source = Maps.__getTileSetInfo(os.path.join(mapPath, tileSet.attrib['source']))
            else:
                source = TileSet.fromXml(tileSet)
                source.properties = Maps.__loadProperties(tileSet.find('properties'))
                source.tiles_properties = Maps.__loadTilesProperties(tileSet)

            source.firstgid = int(tileSet.attrib['firstgid'])

            print source.name, '-->', os.path.join(mapPath, source.image_path), ' - {0}x{1}'.format(m.width, m.height), ' spacing: {}'.format(source.tilespacing)

            try:
                image = pygame.image.load(os.path.join(mapPath, source.image_path))
            except Exception as e:
                logger.exception("Image not found!: {0}".format(e))

            image = image.convert_alpha()
            image.set_alpha(0, pygame.RLEACCEL)

            source.surface = image  # Store original surface

            tilewidth, tileheight = source.tilewidth, source.tileheight
            tilesPerRow = image.get_width() / (tilewidth+source.tilespacing)
            tilesRows = image.get_height() / (tileheight+source.tilespacing)

            source.tiles = range(tilesRows*tilesPerRow)  # Gens a dummy array of this len

            # Extends tile
            if len(m.tiles) <= source.firstgid:
                m.tiles.extend(xrange(source.firstgid+tilesRows*tilesPerRow-len(m.tiles)-1))

            logger.debug('Tiles Grid size: {}x{}'.format(tilesPerRow, tilesRows))
            for y in xrange(tilesRows):
                for x in xrange(tilesPerRow):
                    localTileId = y*tilesPerRow+x
                    tileId = source.firstgid+localTileId-1
                    # Map data contains global tile id (i.e., tile id + tileset firstgid - 1)
                    # We keep here a reference to tiles in thow places (same reference in fact)
                    m.tiles[tileId] = source.tiles[localTileId] = Tile(source,
                        tileId,
                        image.subsurface(((tilewidth+source.tilespacing)*x, (tileheight+source.tilespacing)*y, tilewidth, tileheight)),
                        source.tiles_properties.get(localTileId, {})
                    )  # Creates reference
            source.animated_tiles = [i for i in source.tiles if i.animated]
            m.tilesets[source.name] = source  # Keep source image stored, tiles are references to it

        # Now load m data, we understand right now only base 64
        for layer in root.findall('layer'):
            layerName, layerWidth, layerHeight = layer.attrib['name'], int(layer.attrib['width']), int(layer.attrib['height'])
            data = layer.find('data')
            if data.attrib['encoding'] != 'base64':
                logger.error('No base 64 encoded layer, skyped')
                continue
            m.layers_names.append(layerName)
            m.layers[layerName] = ArrayLayer(
                layerName,
                m,
                struct.unpack('<' + 'I'*(layerWidth*layerHeight), base64.b64decode(data.text)),
                layerWidth,
                layerHeight,
                properties=Maps.__loadProperties(layer.find('properties'))
            )

        # Now load "object" layers and convert them to DynamicLayer

    def get(self, mapId):
        return self._maps[mapId]

    def __unicode__(self):
        r = ''
        for v in self._maps:
            r += unicode(v)
