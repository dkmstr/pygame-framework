# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import xml.etree.ElementTree as ET

from resources.util import resource_path
from resources.maps.tileset import TileSet

from resources.maps.layers import ArrayLayer
from resources.maps.layers import DynamicLayer
from resources.maps.layers import ImageLayer
from resources.maps.layers import ActorsLayer

from resources.maps.utils import loadProperties
from resources.maps.utils import checkTrue

import logging

logger = logging.getLogger(__name__)


######################
# Map                #
######################
class Map(object):
    def __init__(self, mapId, path, properties=None):
        self.id = mapId
        self.mapFile = resource_path(path)
        self.mapPath = os.path.dirname(self.mapFile)
        self.properties = properties if properties is not None else {}
        self.width = self.height = self.tileWidth = self.tileHeight = 0
        self.tileSets = {}
        self.layerNames = []
        self.holderNames = []
        self.layers = {}
        self.tiles = []
        self.displayPosition = (0, 0)
        self.reset()

    def __getLayers(self, layersNames):
        if layersNames is None:
            layersNames = self.layerNames
        else:
            layersNames = [l for l in layersNames if l in self.layerNames]
        return layersNames

    def reset(self, fromNode=None):
        self.width = self.height = self.tileWidth = self.tileHeight = 0
        self.tileSets = {}
        self.layerNames = []
        self.holderNames = []
        self.layers = {}
        self.tiles = []
        self.properties = {}
        self.displayPosition = (0, 0)
        if fromNode is not None:
            self.width = int(fromNode.attrib['width'])
            self.height = int(fromNode.attrib['height'])
            self.tileWidth = int(fromNode.attrib['tilewidth'])
            self.tileHeight = int(fromNode.attrib['tileheight'])
            self.properties = loadProperties(fromNode.find('properties'))

    def load(self):
        tree = ET.parse(self.mapFile)
        root = tree.getroot()  # Map element

        logger.debug('Loading map "{}" in folder "{}"'.format(self.id, self.mapPath))

        self.reset(root)

        for tileSet in root.findall('tileset'):
            ts = TileSet(self)
            ts.load(tileSet)

            self.tileSets[ts.name] = ts

            self.tiles.extend(ts.tiles)

        # Load Layer
        # Remember that object layers must reference tiles layer, and that tiles layer must
        # be BEFORE (i.e. down in the tiled editor layers list) the objects layer because reference must
        # exists. To avoit problems, always put (if posible) linked tiles layers at bottom in tiled so they get
        # loaded FIRST
        t = {
            'layer': ArrayLayer,
            'objectgroup': DynamicLayer,
            'imagelayer': ImageLayer
        }
        for elem in root:
            if elem.tag in ('layer', 'objectgroup', 'imagelayer'):
                l = t[elem.tag](self)
                l.load(elem)
                self.addLayer(l)

    def addLayer(self, layer):
        logger.debug('Adding layer {} to layer list (visible: {})'.format(layer, layer.visible))
        if checkTrue(layer.getProperty('holder')):
            logger.debug('Layer {} is a holder layer'.format(layer.name))
            self.holderNames.append(layer.name)
        else:
            self.layerNames.append(layer.name)
            
        if checkTrue(layer.getProperty('actors')):
            layer = ActorsLayer(self, layer)
            
        self.layers[layer.name] = layer

    def getLayer(self, layerName):
        return self.layers.get(layerName)

    def getActors(self, actorType=None, layersNames=None):
        for layerName in self.__getLayers(layersNames):
            if checkTrue(self.layers[layerName].getProperty('actors')):
                for actor in self.layers[layerName].getActors(actorType):
                    yield actor

    def draw(self, surface, layersNames=None):
        # First, we draw "parallax" layers
        x, y = self.displayPosition
        width, height = surface.get_size()
        for layerName in self.__getLayers(layersNames):
            self.layers[layerName].draw(surface, x, y, width, height)

    def update(self, layersNames=None):
        # Keep order intact
        for layerName in self.__getLayers(layersNames):
            if self.layers[layerName].visible:
                self.layers[layerName].update()

        for ts in self.tileSets.itervalues():
            ts.update()

    # Current display position of the map
    def setDisplayPosition(self, x, y):
        self.displayPosition = (x, y)

    def getDisplayPosition(self):
        return self.displayPosition

    # Collisions
    def getCollisions(self, rect, layersNames=None):
        for layerName in self.__getLayers(layersNames):
            if checkTrue(self.layers[layerName].getProperty('parallax')):
                continue

            for col in self.layers[layerName].getCollisions(rect):
                yield col

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this map
        '''
        return self.properties.get(propertyName)

    def __unicode__(self):
        return 'Map {}: {}x{} with tile of  ({}x{}) and {} properties'.format(self.mapFile, self.width, self.height, self.tileWidth, self.tileHeight, self.properties)


class Maps(object):
    def __init__(self):
        self.maps = {}

    def add(self, mapId, path):
        self.maps[mapId] = Map(mapId, path)

    def load(self, mapId=None, force=False):
        if mapId is None:
            for mId in self.maps:
                self.load(mId, force)
            return

        if mapId not in self.maps:
            return False

        m = self.maps[mapId]
        m.load()

    def get(self, mapId):
        return self.maps[mapId]

    def __unicode__(self):
        return [unicode(v) for v in self.maps].join(',')
        
