# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import xml.etree.ElementTree as ET

from resources.util import resource_path
from tileset import TileSet
from layers import ArrayLayer
from layers import DynamicLayer
from layers import ImageLayer
from utils import loadProperties

import logging

logger = logging.getLogger(__name__)


######################
# Map                #
######################
class Map(object):
    def __init__(self, mapId, path, properties={}):
        self.id = mapId
        self.mapFile = resource_path(path)
        self.mapPath = os.path.dirname(self.mapFile)
        self.reset()

    def __getLayers(self, layersNames):
        if layersNames is None:
            layersNames = self.layers_names
        else:
            layersNames = [l for l in layersNames if l in self.layers_names]
        return layersNames

    def __getParallaxLayersNames(self, layersNames):
        if layersNames is None:
            layersNames = self.parallax_names
        else:
            layersNames = [l for l in layersNames if l in self.parallax_names]
        return layersNames

    def reset(self, fromNode=None):
        self.width = self.height = self.tilewidth = self.tileheight = 0
        self.tilesets = {}
        self.layers_names = []
        self.holders_names = []
        self.parallax_names = []
        self.layers = {}
        self.tiles = []
        self.properties = {}
        if fromNode is not None:
            self.width = int(fromNode.attrib['width'])
            self.height = int(fromNode.attrib['height'])
            self.tilewidth = int(fromNode.attrib['tilewidth'])
            self.tileheight = int(fromNode.attrib['tileheight'])
            self.properties = loadProperties(fromNode.find('properties'))

    def load(self):
        tree = ET.parse(self.mapFile)
        root = tree.getroot()  # Map element

        logger.debug('Loading map "{}" in folder "{}"'.format(self.id, self.mapPath))

        self.reset(root)

        for tileSet in root.findall('tileset'):
            ts = TileSet(self)
            ts.load(tileSet)

            self.tilesets[ts.name] = ts

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
        if layer.getProperty('holder') == 'True':
            logger.debug('Layer {} is a holder layer'.format(layer.name))
            self.holders_names.append(layer.name)
        elif layer.getProperty('parallax') == 'True':
            logger.debug('Layer {} is a parallax layer'.format(layer.name))
            self.parallax_names.append(layer.name)
        else:
            self.layers_names.append(layer.name)
        self.layers[layer.name] = layer

    def getLayer(self, layerName):
        return self.layers.get(layerName)

    def draw(self, surface, x=0, y=0, width=0, height=0, layersNames=None):
        # First, we draw "parallax" layers
        for d in (self.__getParallaxLayersNames(layersNames), self.__getLayers(layersNames)):
            for layerName in d:
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


class Maps(object):
    def __init__(self):
        self._maps = {}

    def add(self, mapId, path):
        self._maps[mapId] = Map(mapId, path)

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
