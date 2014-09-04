# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import os
import xml.etree.ElementTree as ET

from game.objects import Tile
from game.util import loadProperties

import logging

logger = logging.getLogger(__name__)


######################
# TileSet            #
######################
class TileSet(object):
    def __init__(self, parentMap):
        self.name = None
        self.tileWidth = self.tileHeight = self.tileSpacing = 0
        self.imageFile = ''
        self.imageWidth = self.imageHeight = 0
        self.firstGid = 0
        self.surface = None
        self.tiles = []
        self.animatedTiles = []
        self.properties = {}
        self.tilesProperties = {}
        self.parentMap = parentMap

    def __loadTilesProperties(self, node):
        self.tilesProperties = {}
        for t in node.findall('tile'):
            tid = int(t.attrib['id'])
            self.tilesProperties[tid] = loadProperties(t.find('properties'))

    def __loadTileSet(self, node):
        image = node.find('image')

        self.name = node.attrib['name']
        self.tileWidth = int(node.attrib['tilewidth'])
        self.tileHeight = int(node.attrib['tileheight'])
        self.tileSpacing = int(node.attrib.get('spacing', 0))
        self.imageFile = image.attrib['source']
        self.imageWidth = int(image.attrib['width'])
        self.imageHeight = int(image.attrib['height'])

        image = pygame.image.load(os.path.join(self.parentMap.mapPath, self.imageFile))

        image = image.convert_alpha()
        image.set_alpha(0, pygame.RLEACCEL)

        self.surface = image  # Store original surface

        self.properties = loadProperties(node.find('properties'))
        self.__loadTilesProperties(node)

    def __loadExternalTileset(self, path):
        logger.debug('Loading external tileset: {}'.format(path))
        tree = ET.parse(os.path.join(self.parentMap.mapPath, path))
        root = tree.getroot()  # Map element
        self.__loadTileSet(root)

    def load(self, node):
        logger.debug('Loading tileset in path {}'.format(self.parentMap.mapPath))
        if 'source' in node.attrib:
            self.__loadExternalTileset(node.attrib['source'])
        else:
            self.__loadTileSet(node)

        self.firstGid = int(node.attrib['firstgid'])

        logger.debug('Image path: {} {}x{}'.format(self.imageFile, self.imageWidth, self.imageHeight))

        tilesPerRow = self.surface.get_width() / (self.tileWidth+self.tileSpacing)
        tilesRows = self.surface.get_height() / (self.tileHeight+self.tileSpacing)

        self.tiles = [None] * (tilesRows*tilesPerRow)  # Gens a dummy array of this len

        logger.debug('Tiles Grid size: {}x{}'.format(tilesPerRow, tilesRows))
        for y in xrange(tilesRows):
            for x in xrange(tilesPerRow):
                localTileId = y*tilesPerRow+x
                tileId = self.firstGid+localTileId-1
                # Map data contains global tile id (i.e., tile id + tileset firstgid - 1)
                # We keep here a reference to tiles in thow places (same reference in fact)
                self.tiles[localTileId] = Tile(self,
                    tileId,
                    self.surface.subsurface(((self.tileWidth+self.tileSpacing)*x, (self.tileHeight+self.tileSpacing)*y, self.tileWidth, self.tileHeight)),
                    self.tilesProperties.get(localTileId, {})
                )  # Creates reference

        self.animatedTiles = [i for i in self.tiles if i.animated]

    def getTile(self, localTileId):
        return self.tiles[localTileId]

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this tileset
        '''
        return self.properties.get(propertyName)

    def update(self):
        for t in self.animatedTiles:
            t.update()

    def __unicode__(self):
        return 'Tileset {}: {}x{} ({})'.format(self.name, self.tileWidth, self.tileHeight, self.properties)
