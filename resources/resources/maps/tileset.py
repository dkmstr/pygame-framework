# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import os
import xml.etree.ElementTree as ET

from tiles import Tile
from utils import loadProperties

import logging

logger = logging.getLogger(__name__)


######################
# TileSet            #
######################
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
        self.parentMap = parentMap

    def __loadTilesProperties(self, node):
        self.tiles_properties = {}
        for t in node.findall('tile'):
            tid = int(t.attrib['id'])
            self.tiles_properties[tid] = loadProperties(t.find('properties'))

    def __loadTileSet(self, node):
        image = node.find('image')

        self.name = node.attrib['name']
        self.tilewidth = int(node.attrib['tilewidth'])
        self.tileheight = int(node.attrib['tileheight'])
        self.tilespacing = int(node.attrib.get('spacing', 0))
        self.image_path = image.attrib['source']
        self.image_width = int(image.attrib['width'])
        self.image_height = int(image.attrib['height'])

        image = pygame.image.load(os.path.join(self.parentMap.mapPath, self.image_path))

        image = image.convert_alpha()
        image.set_alpha(0, pygame.RLEACCEL)

        self.surface = image  # Store original surface

        self.properties = loadProperties(node.find('properties'))
        self.__loadTilesProperties(node)

    def __loadExternalTileset(self, path):
        logger.debug('Loading external tileset: {}'.format(path))
        tree = ET.parse(os.path.join(self.parentMap.mapPath, path))
        root = tree.getroot()  # Map element
        self.__loadTileSet(self.parentMap.mapPath, root)

    def load(self, node):
        logger.debug('Loading tileset in path {}'.format(self.parentMap.mapPath))
        if 'source' in node.attrib:
            self.__loadExternalTileset(node.attrib['source'])
        else:
            self.__loadTileSet(node)

        self.firstgid = int(node.attrib['firstgid'])

        logger.debug('Image path: {} {}x{}'.format(self.image_path, self.image_width, self.image_height))

        tilesPerRow = self.surface.get_width() / (self.tilewidth+self.tilespacing)
        tilesRows = self.surface.get_height() / (self.tileheight+self.tilespacing)

        self.tiles = [None] * (tilesRows*tilesPerRow)  # Gens a dummy array of this len

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
