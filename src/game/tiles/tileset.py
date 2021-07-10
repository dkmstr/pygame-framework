# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import logging
import typing

import pygame

import xml.etree.ElementTree as ET

from game.util import loadProperties
from game.tiles import Tile

if typing.TYPE_CHECKING:
    import game.maps
    import game.tiles
    import game.renderer

logger = logging.getLogger(__name__)


######################
# TileSet            #
######################
class TileSet(object):
    name: typing.Optional[str]
    tileWidth: int
    tileHeight: int
    tileSpacing: int
    imageFile: str
    imageWidth: int
    imageHeight: int
    firstGid: int
    image: typing.Optional['game.renderer.renderer.Image']
    tiles: typing.List[typing.Optional['game.tiles.Tile']]
    animatedTiles: typing.List['game.tiles.Tile']
    properties: typing.Dict[str, str]
    tilesProperties: typing.Dict[int, typing.Dict[str, str]]
    parentMap: 'game.maps.Map'

    def __init__(self, parentMap: 'game.maps.Map') -> None:
        self.name = None
        self.tileWidth = self.tileHeight = self.tileSpacing = 0
        self.imageFile = ''
        self.imageWidth = self.imageHeight = 0
        self.firstGid = 0
        self.image = None
        self.tiles = []
        self.animatedTiles = []
        self.properties = {}
        self.tilesProperties = {}
        self.parentMap = parentMap

    def __loadTilesProperties(self, node: ET.Element) -> None:
        self.tilesProperties = {}
        for t in node.findall('tile'):
            tid = int(t.attrib['id'])
            self.tilesProperties[tid] = loadProperties(t.find('properties'))

    def __loadTileSet(self, node: ET.Element) -> None:
        image = node.find('image')
        if image is None:
            return

        self.name = node.attrib['name']
        self.tileWidth = int(node.attrib['tilewidth'])
        self.tileHeight = int(node.attrib['tileheight'])
        self.tileSpacing = int(node.attrib.get('spacing', 0))
        self.imageFile = image.attrib['source']
        self.imageWidth = int(image.attrib['width'])
        self.imageHeight = int(image.attrib['height'])

        self.image = self.getRenderer().imageFromFile(
            os.path.join(self.parentMap.mapPath, self.imageFile)
        )

        self.properties = loadProperties(node.find('properties'))
        self.__loadTilesProperties(node)

    def __loadExternalTileset(self, path):
        logger.debug('Loading external tileset: {}'.format(path))
        tree = ET.parse(os.path.join(self.parentMap.mapPath, path))
        root = tree.getroot()  # Map element
        self.__loadTileSet(root)

    def getRenderer(self) -> 'game.renderer.Renderer':
        return self.parentMap.getController().renderer

    def load(self, node: ET.Element) -> None:
        logger.debug('Loading tileset in path {}'.format(self.parentMap.mapPath))
        if 'source' in node.attrib:
            self.__loadExternalTileset(node.attrib['source'])
        else:
            self.__loadTileSet(node)

        self.firstGid = int(node.attrib['firstgid'])

        logger.debug(
            'Image path: {} {}x{}'.format(
                self.imageFile, self.imageWidth, self.imageHeight
            )
        )

        if self.image is None:
            return

        tilesPerRow = int(self.image.getWidth() / (self.tileWidth + self.tileSpacing))
        tilesRows = int(self.image.getHeight() / (self.tileHeight + self.tileSpacing))

        self.tiles = [None] * (
            tilesRows * tilesPerRow
        )  # Gens a dummy array of this len

        logger.debug('Tiles Grid size: {}x{}'.format(tilesPerRow, tilesRows))
        for y in range(tilesRows):
            for x in range(tilesPerRow):
                localTileId = y * tilesPerRow + x
                tileId = self.firstGid + localTileId - 1
                # Map data contains global tile id (i.e., tile id + tileset firstgid - 1)
                # We keep here a reference to tiles in thow places (same reference in fact)
                self.tiles[localTileId] = Tile(
                    self,
                    tileId,
                    self.image.subimage(
                        (
                            (self.tileWidth + self.tileSpacing) * x,
                            (self.tileHeight + self.tileSpacing) * y,
                            self.tileWidth,
                            self.tileHeight,
                        )
                    ),
                    self.tilesProperties.get(localTileId, {}),
                )  # Creates reference

        self.animatedTiles = [i for i in self.tiles if i.animated]

    def addTileFromTile(self, srcTile, flipX, flipY, rotate):
        if rotate:
            image = pygame.transform.rotate(srcTile.getOriginalImage(), 90)
        else:
            image = srcTile.getOriginalImage()
        image = srcTile.getOriginalImage().flip(flipX, flipY, rotate)
        tile = Tile(self, len(self.tiles) + 1, image, srcTile.properties)
        self.tiles.append(tile)
        return tile

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
        return 'Tileset {}: {}x{} ({})'.format(
            self.name, self.tileWidth, self.tileHeight, self.properties
        )
