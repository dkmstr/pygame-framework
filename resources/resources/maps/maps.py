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
from actors import ActorList

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
            layersNames = self.layerNames
        else:
            layersNames = [l for l in layersNames if l in self.layerNames]
        return layersNames

    def __getParallaxLayersNames(self, layersNames):
        if layersNames is None:
            layersNames = self.parallaxNames
        else:
            layersNames = [l for l in layersNames if l in self.parallaxNames]
        return layersNames

    def reset(self, fromNode=None):
        self.width = self.height = self.tileWidth = self.tileHeight = 0
        self.tileSets = {}
        self.layerNames = []
        self.holderNames = []
        self.parallaxNames = []
        self.layers = {}
        self.tiles = []
        self.properties = {}
        self.actors = ActorList()
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
        logger.debug('Adding layer {} to layer list'.format(layer))
        if layer.getProperty('actors') == 'True':
            self.actors.addActorsFromArrayLayer(layer)
            return   # This layer is completly removed
        elif layer.getProperty('holder') == 'True':
            logger.debug('Layer {} is a holder layer'.format(layer.name))
            self.holderNames.append(layer.name)
        elif layer.getProperty('parallax') == 'True':
            logger.debug('Layer {} is a parallax layer'.format(layer.name))
            self.parallaxNames.append(layer.name)
        else:
            self.layerNames.append(layer.name)
        self.layers[layer.name] = layer

    def getLayer(self, layerName):
        return self.layers.get(layerName)

    def getActorList(self):
        return self.actors

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

        for ts in self.tileSets.itervalues():
            ts.update()

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this map
        '''
        return self.properties.get(propertyName)

    def __unicode__(self):
        return 'Map {}: {}x{} with tile of  ({})'.format(self.path, self.width, self.height, self.tileWidth, self.tileHeight, self.properties)


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
        r = ''
        for v in self.maps:
            r += unicode(v)
