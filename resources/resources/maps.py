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
        self.properties = {}

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName)


class Layer(object):
    def __init__(self, tilemap, name, data, width=0, height=0):
        self.name = name
        self.width = width
        self.height = height
        self.data = data
        self.tilemap = tilemap
        self.properties = {}

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
                        surface.blit(tiles[tile-1], ((x-xStart)*tileWidth-xOffset, (y-yStart)*tileHeight-yOffset))

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this layer
        '''
        return self.properties.get(propertyName)


class Map(object):
    def __init__(self, path):
        self.path = resource_path(path)
        self.width = self.height = 0
        self.tilewidth = self.tileheight = 0
        self.tilesets = {}
        self.tiles = []
        self.layers_names = []
        self.layers = {}
        self.properties = {}

    def getLayer(self, layerName):
        return self.layers[layerName]

    def draw(self, surface, x=0, y=0, width=0, height=0, layers=None):
        if layers is None:
            layers = self.layers_names

        for layer in layers:
            self.layers[layer].draw(surface, x, y, width, height)

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this map
        '''
        return self.properties.get(propertyName)


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
        self.properties = {}

    def add(self, mapId, path):
        self._maps[mapId] = Map(path)

    @staticmethod
    def __loadProperties(obj, node):
        if node:
            logger.debug('Loading properties for {}'.format(obj))
            for p in node.findall('property'):
                logger.debug('Found property {}={}'.format(p.attrib['name'], p.attrib['value']))
                obj.properties[p.attrib['name']] = p.attrib['value']

    @staticmethod
    def __getTileSetInfo(tileSet):
        print "Loading tileset ", tileSet
        tree = ET.parse(tileSet)
        root = tree.getroot()  # Map element
        image = root.find('image')
        ts = TileSet(
            root.attrib['name'],
            int(root.attrib['tilewidth']),
            int(root.attrib['tileheight']),
            int(root.attrib.get('spacing', 0)),
            image.attrib['source'],
            int(image.attrib['width']),
            int(image.attrib['height'])
        )
        Maps.__loadProperties(ts, root.find('properties'))

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

        logger.debug('Loading map {} in folder {}'.format(m.map, m.mapPath))

        Maps.__loadProperties(self, root.find('properties'))

        # Get general m info
        m.width = int(root.attrib['width'])
        m.height = int(root.attrib['height'])
        m.tilewidth = int(root.attrib['tilewidth'])
        m.tileheight = int(root.attrib['tileheight'])
        m.layers_names = []
        m.layers = {}
        m.tiles = []

        # Locate tilesets
        for tileSet in root.findall('tileset'):
            if 'source' in tileSet.attrib:
                source = Maps.__getTileSetInfo(os.path.join(mapPath, tileSet.attrib['source']))
            else:
                image = tileSet.find('image')

                source = TileSet(
                    tileSet.attrib['name'],
                    int(tileSet.attrib['tilewidth']),
                    int(tileSet.attrib['tileheight']),
                    int(tileSet.attrib.get('spacing', 0)),
                    image.attrib['source'],
                    int(image.attrib['width']),
                    int(image.attrib['height'])
                )
                Maps.__loadProperties(source, tileSet.find('properties'))

            source.firstgid = int(tileSet.attrib['firstgid'])

            print source.name, '-->', os.path.join(mapPath, source.image_path), ' - {0}x{1}'.format(m.width, m.height), ' spacing: {}'.format(source.tilespacing)
            # TODO: Load tileset and associate it to m
            try:
                image = pygame.image.load(os.path.join(mapPath, source.image_path))
            except Exception as e:
                print "Image not found!: {0}".format(e)

            image = image.convert_alpha()
            image.set_alpha(0, pygame.RLEACCEL)

            source.surface = image  # Store original surface

            tilewidth, tileheight = source.tilewidth, source.tileheight
            tilesPerRow = image.get_width() / (tilewidth+source.tilespacing)
            tilesRows = image.get_height() / (tileheight+source.tilespacing)

            if len(m.tiles) <= source.firstgid:
                m.tiles.extend(xrange(source.firstgid+tilesRows*tilesPerRow-len(m.tiles)))

            print 'Tiles Cols/Rows', tilesPerRow, tilesRows, tilewidth, tileheight, source.firstgid
            for y in xrange(tilesRows):
                for x in xrange(tilesPerRow):
                    m.tiles[source.firstgid+y*tilesPerRow+x-1] = (image.subsurface(((tilewidth+source.tilespacing)*x, (tileheight+source.tilespacing)*y, tilewidth, tileheight)))  # Creates reference

            m.tilesets[source.name] = source  # Keep source image stored, tiles are references to it

        # Now load m data, we understand right now only base 64
        for layer in root.findall('layer'):
            layerName, layerWidth, layerHeight = layer.attrib['name'], int(layer.attrib['width']), int(layer.attrib['height'])
            data = layer.find('data')
            if data.attrib['encoding'] != 'base64':
                print 'No base 64'
            m.layers_names.append(layerName)
            m.layers[layerName] = Layer(
                m,
                layerName,
                struct.unpack('<' + 'I'*(layerWidth*layerHeight), base64.b64decode(data.text)),
                layerWidth,
                layerHeight
            )
            Maps.__loadProperties(m.layers[layerName], layer.find('properties'))

    def get(self, mapId):
        return self._maps[mapId]
