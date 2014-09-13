# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import pygame
import xml.etree.ElementTree as ET

from game.util import resource_path
from game.util import loadProperties
from game.tiles import TileSet

from game import layers

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
        self.tileSets = []
        self.layers = []
        self.tiles = []
        self.effectsLayer = None
        self.hudLayer = None
        self.displayPosition = (0, 0)
        self.boundary = pygame.Rect(0, 0, 0, 0)
        self.reset()

    def getRenderingLayers(self):
        return [l for l in self.layers if l.holder is False and l.visible is True]

    def getActorsLayers(self):
        return [l for l in self.layers if l.actor is True]

    def getCollisionsLayers(self):
        return [l for l in self.layers if l.holder is False and l.visible is True and l.actor is False and l.parallax is False]

    def reset(self, fromNode=None):
        self.width = self.height = self.tileWidth = self.tileHeight = 0
        self.tileSets = []
        self.layers = []
        self.effectsLayer = layers.EffectsLayer(self)
        self.hudLayer = layers.HudLayer(self)
        self.tiles = []
        self.properties = {}
        self.displayPosition = (0, 0)
        if fromNode is not None:
            self.width = int(fromNode.attrib['width'])
            self.height = int(fromNode.attrib['height'])
            self.tileWidth = int(fromNode.attrib['tilewidth'])
            self.tileHeight = int(fromNode.attrib['tileheight'])
            self.properties = loadProperties(fromNode.find('properties'))
            self.boundary = pygame.Rect(0, 0, self.width*self.tileHeight, self.height*self.tileHeight)
        else:
            self.width = self.height = self.tileWidth = self.tileHeight = 0
            self.properties = {}
            self.boundary = pygame.Rect(0, 0, 0, 0)

    def load(self):
        tree = ET.parse(self.mapFile)
        root = tree.getroot()  # Map element

        logger.debug('Loading map "{}" in folder "{}"'.format(self.id, self.mapPath))

        self.reset(root)

        for tileSet in root.findall('tileset'):
            ts = TileSet(self)
            ts.load(tileSet)

            self.tileSets.append(ts)
            self.tiles.extend(ts.tiles)

        # Load Layer
        # Remember that object layers must reference tiles layer, and that tiles layer must
        # be BEFORE (i.e. down in the tiled editor layers list) the objects layer because reference must
        # exists. To avoit problems, always put (if posible) linked tiles layers at bottom in tiled so they get
        # loaded FIRST
        t = {
            'layer': layers.ArrayLayer,
            'objectgroup': layers.DynamicLayer,
            'imagelayer': layers.ImageLayer
        }
        for elem in root:
            if elem.tag in ('layer', 'objectgroup', 'imagelayer'):
                l = t[elem.tag](self)
                l.load(elem)
                self.addLayer(l)

    def addTileFromTile(self, srcTileId, flipX, flipY):
        tile = self.tiles[srcTileId-1]
        self.tiles.append(tile.parent.addTileFromTile(tile, flipX, flipY))
        return len(self.tiles)

    def addLayer(self, layer):
        if layer.actor:
            layer = layers.ActorsLayer(self, layer)

        self.layers.append(layer)

    def getLayer(self, layerName):
        for l in self.layers:
            if l.name == layerName:
                return l
        return None

    def getActors(self, actorType=None):
        for layer in self.getActorsLayers():
            for actor in layer.getActors(actorType):
                yield actor

    def removeActor(self, actor):
        for layer in self.getActorsLayers():
            layer.removeActor(actor)
            
    def addEffect(self, effectId, effect):
        self.effectsLayer.addEffect(effectId, effect)
        
    def addHudElement(self, hudElement):
        self.hudLayer.addElement(hudElement)

    def draw(self, surface):
        # First, we draw "parallax" layers
        x, y = self.displayPosition
        width, height = surface.get_size()
        for layer in self.getRenderingLayers():
            layer.draw(surface, x, y, width, height)

        # draw effects layer
        self.effectsLayer.draw(surface, x, y, width, height)
         
        # And finally, the HUD at topmost
        self.hudLayer.draw(surface, x, y, width, height)

    def update(self):
        # Keep order intact
        for layer in self.getRenderingLayers():
                layer.update()

        # Update tilesets (for animations)
        for ts in self.tileSets:
            ts.update()
            
        # Update effects layer
        self.effectsLayer.update()
        
        # And hud elements
        self.hudLayer.update()

    # Current display position of the map
    def setDisplayPosition(self, x, y):
        self.displayPosition = (x, y)

    def getDisplayPosition(self):
        return self.displayPosition

    def translateCoordinates(self, rect):
        return rect.move(-self.displayPosition[0], -self.displayPosition[1])

    # Collisions
    def getCollisions(self, rect, possibleCollisions=None):
        '''
        If a list of possible collisions is passed in, only this
        elements are used to test collisions
        '''
        if possibleCollisions is not None:
            for col in possibleCollisions:
                if col[0].colliderect(rect):
                    yield col
        
        else:
            for layer in self.getCollisionsLayers():
                if layer.parallax is True:
                    continue
    
                for col in layer.getCollisions(rect):
                    yield (col[0], col[1], layer)
                
    def getPossibleCollisions(self, rect, xRange=32, yRange=32):
        '''
        If needs to get check collisions more than once, this optimizes 
        a lot the process limiting the objects to check
        '''
        rect = rect.inflate(2*xRange, 2*yRange)
        
        return [col for col in self.getCollisions(rect)]
    
    def getActorsCollisions(self, rect, possibleCollisions=None, exclude=None):
        '''
        If a list of possible collisions is passed in, only this
        elements are used to test collisions
        '''
        if possibleCollisions is not None:
            for col in possibleCollisions:
                if col[1].collide(rect):
                    yield col
        else:
            for layer in self.getActorsLayers():
                for col in layer.getCollisions(rect):
                    if col[1] is not exclude:
                        yield col

    def getPossibleActorsCollisions(self, rect, xRange=32, yRange=32, exclude=None):
        '''
        If needs to get check collisions more than once, this optimizes 
        a lot the process limiting the objects to check
        xRange and yRange should be big enought to ensure that the "destination" actor
        (wich also moves) won't hit us without knowing it
        '''
        rect = rect.inflate(2*xRange, 2*yRange)
        
        return [col for col in self.getActorsCollisions(rect) if col[1] is not exclude]

    def getProperty(self, propertyName):
        '''
        Obtains a property associated whit this map
        '''
        return self.properties.get(propertyName)

    def getRect(self):
        return self.boundary

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
