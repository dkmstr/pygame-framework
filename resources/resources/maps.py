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


class PathSegment(object):
    def __init__(self, x, y, x_offset, y_offset):
        self.x, self.y, self.x_offset, self.y_offset = x, y, x_offset, y_offset

        # Calculate gradient
        if x_offset == 0 and y_offset == 0:
            self.x_step = self.y_step = 0
            self.x_at_end = self.y_at_end = lambda x: True
        else:
            div = abs(x_offset) if abs(x_offset) > abs(y_offset) else abs(y_offset)
            self.x_step = (x_offset << 16) / div

            if self.x_step > 0:
                self.x_at_end = lambda x: x >= self.x + self.x_offset
            else:
                self.x_at_end = lambda x: x <= self.x + self.x_offset

            self.y_step = (y_offset << 16) / div

            if self.y_step > 0:
                self.y_at_end = lambda y: y >= self.y + self.y_offset
            else:
                self.y_at_end = lambda y: y <= self.y + self.y_offset

    def getCoords(self, position, step):
        '''
        Very aproximate position using only integers
        '''
        position *= step
        x, y = self.x + ((self.x_step*position) >> 16), self.y + ((self.y_step*position) >> 16)
        if self.x_at_end(x) and self.y_at_end(y):
            return None  # Out of line
        return (x, y)

    def __unicode__(self):
        return 'PathSegment: ({},{})-({},{}) {},{}'.format(self.x, self.y, self.x + self.x_offset, self.y + self.y_offset, self.x_step, self.y_step)


######################
# Path               #
######################
class Path(object):
    def __init__(self, segments, step, bounce=False):
        self.segments = segments
        self.step = step
        self.reset()

    def reset(self):
        self.segment = 0
        self.segment_pos = 0

    def iterate(self):
        if self.segment >= len(self.segments):
            return None
        pos = self.segments[self.segment].getCoords(self.segment_pos, self.step)
        if pos is None:
            self.segment += 1
            self.segment_pos = 0
            pos = self.iterate()
            if pos is None:
                self.reset()
                return self.iterate()
        else:
            self.segment_pos += 1
        return pos

    def __unicode__(self):
        return 'Path: {}'.format([unicode(s) for s in self.segments])


######################
# Tile               #
######################
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

    # This x,y coordinates are screen coordinates
    # TileArray, Platform, etc.. converts coordinates of objects acordly beforw invoking it
    def draw(self, toSurface, x, y):
        if self._surface is not None:
            toSurface.blit(self._surface, (x, y))

    def getImage(self):
        return self._surface

    def setImage(self, surface):
        self._surface = surface

    def resetImage(self):
        self._surface = self._orig_surface

    def id(self):
        return self._id

    def getTileSet(self):
        return self._tileSet

    def __unicode__(self):
        return 'Tile {} ({}x{}) ({})'.format(self._id, self._surface.get_width(), self._surface.get_height(), self.properties)


class Platform(object):
    def __init__(self, origX, origY, width, height, path, tiles, sticky):
        self.rect = pygame.Rect(origX, origY, width, height)
        self.path = path
        self.tiles = tiles
        self.sticky = sticky

    def draw(self, toSurface, x, y):
        '''
        Draws to specied surface, to coords x, y
        '''
        rect = pygame.Rect((x, y), toSurface.get_size())
        if not rect.colliderect(self.rect):
            return
        # Translate start to screen coordinates
        x = self.rect.left - x
        y = self.rect.top - y
        for row in self.tiles:
            xx = x
            for t in row:
                t.draw(toSurface, xx, y)  # tile drawing is in screen coordinates, that is what we have on x & y
                xx += t.getTileSet().tilewidth
            y += t.getTileSet().tileheight

    def update(self):
        self.rect.left, self.rect.top = self.path.iterate()


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
        logger.debug('Loading external tileset: {}'.format(path))
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


######################
# Layer              #
######################
class Layer(object):
    LAYER_TYPE = 'default'
    EMPTY_TILE = Tile(None, 0, None)

    def __init__(self, parentMap=None, layerType=None, properties={}):
        self.name = None
        self.type = layerType if layerType is not None else self.LAYER_TYPE
        self.parentMap = parentMap
        self.setProperties(properties)

    def setProperties(self, properties):
        self.properties = properties
        # Set custom "flags" based on properties

    def updateAttributes(self):
        self.visible = self.properties.get('visible', 'True') == 'True'

    def load(self, node):
        pass

    def update(self):
        pass

    def draw(self, toSurface, x=0, y=0, width=0, height=0):
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


######################
# ArrayLayer         #
######################
class ArrayLayer(Layer):
    LAYER_TYPE = 'array'

    def load(self, node):
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])

        self.properties = Maps._loadProperties(node.find('properties'))

        data = node.find('data')
        if data.attrib['encoding'] != 'base64':
            raise Exception('No base 64 encoded')
        self.data = struct.unpack('<' + 'I'*(self.width*self.height), base64.b64decode(data.text))

    def draw(self, toSurface, x=0, y=0, width=0, height=0):
        tiles = self.parentMap.tiles
        tileWidth = self.parentMap.tilewidth
        tileHeight = self.parentMap.tileheight

        width = toSurface.get_width() if width <= 0 else width
        height = toSurface.get_height() if height <= 0 else height

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
                        tiles[tile-1].draw(toSurface, (x-xStart)*tileWidth-xOffset, (y-yStart)*tileHeight-yOffset)

    def update(self):
        super(ArrayLayer, self).update()

    def getTileAt(self, x, y):
        x /= self.parentMap.tilewidth
        y /= self.parentMap.tileheight
        tile = self.data[y*self.width+x]
        if tile == 0:
            return Layer.EMPTY_TILE
        return self.parentMap.tiles[tile-1]

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

        self.properties = Maps._loadProperties(node.find('properties'))
        tiles_layer_name = self.properties.get('layer', None)

        self.tiles_layer = self.parentMap.getLayer(tiles_layer_name)
        if self.tiles_layer is None:
            logger.error('Linking to an unexistent layer: {}'.format(tiles_layer_name))
            return

        paths = {}
        self.platforms = {}

        for obj in node.findall('object'):
            if obj.attrib['type'] == 'path':  # This is a path, store it in paths
                name = obj.attrib['name']
                properties = Maps._loadProperties(obj.find('properties'))
                polyline = [[int(v) for v in i.split(',')] for i in obj.find('polyline').attrib['points'].split(' ')]
                step = int(properties.get('step', '1'))
                bounce = properties.get('bounce', 'False') == 'False'

                if len(polyline) > 0:
                    orig_x, orig_y = int(obj.attrib['x']), int(obj.attrib['y'])
                    x, y = orig_x + polyline[0][0], orig_y + polyline[0][1]
                    polyline = polyline[1:]

                    segments = []
                    for line in polyline:
                        xf, yf = orig_x + line[0], orig_y + line[1]
                        segments.append(PathSegment(x, y, xf-x, yf-y))
                        x = orig_x + line[0]
                        y = orig_y + line[1]

                    paths[name] = Path(segments, step, bounce)

                    logger.debug('Path {} {}'.format(name, paths[name]))
            elif obj.attrib['type'] == 'platform':
                name = obj.attrib['name']
                properties = Maps._loadProperties(obj.find('properties'))
                startX, startY = int(obj.attrib['x']), int(obj.attrib['y'])
                width, height = int(obj.attrib.get('width', self.parentMap.tilewidth)), int(obj.attrib.get('height', self.parentMap.tileheight))
                tiles = []

                for y in xrange(startY, startY+height, self.parentMap.tileheight):
                    t = []
                    for x in xrange(startX, startX+width, self.parentMap.tilewidth):
                        t.append(self.tiles_layer.getTileAt(x, y))
                    tiles.append(t)

                p = Platform(startX, startY, width, height, properties.get('path', None), tiles, properties.get('sticky', False))
                self.platforms[obj.attrib['name']] = p

                logger.debug('Platform {}'.format(p))

            # Get obj properties to know that is this
        # After loading, add paths to Platforms
        erroneous = []
        for k, p in self.platforms.iteritems():
            try:
                p.path = paths[p.path]
            except:
                logger.error('Path {} doesn\'t exists!!'.format(p.path))
                erroneous.append(k)

        for k in erroneous:
            del self.platforms[k]

    def draw(self, toSurface, x=0, y=0, width=0, height=0):
        for obj in self.platforms.itervalues():
            obj.draw(toSurface, x, y)

    def update(self):
        for obj in self.platforms.itervalues():
            obj.update()


######################
# Map                #
######################
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

        # Load Layer
        # Remember that object layers must reference tiles layer, and that tiles layer must
        # be BEFORE (i.e. down in the tiled editor layers list) the objects layer because reference must
        # exists. To avoit problems, always put (if posible) linked tiles layers at bottom in tiled so they get
        # loaded FIRST
        for elem in root:
            if elem.tag in ('layer', 'objectgroup'):
                l = ArrayLayer(self) if elem.tag == 'layer' else DynamicLayer(self)
                l.load(elem)
                self.addLayer(l)

    def addLayer(self, layer):
        if layer.getProperty('holder') == 'True':
            logger.debug('Layer {} is a holder layer'.format(layer.name))
            self.holders_names.append(layer.name)
        else:
            self.layers_names.append(layer.name)
        self.layers[layer.name] = layer

    def getLayer(self, layerName):
        return self.layers.get(layerName)

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
