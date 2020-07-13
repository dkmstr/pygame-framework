# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame

from game import paths
from game.objects import ObjectWithPath
from game.util import loadProperties
from game.layers.layer import Layer

import logging

logger = logging.getLogger(__name__)


class PlatformsLayer(Layer):
    LAYER_TYPE = 'platforms'

    def __init__(self, parentMap=None, layerType=None, properties=None):
        Layer.__init__(self, parentMap, layerType, properties)
        self.width = self.height = 0
        self.tilesLayer = None
        self.paths = {}
        self.platforms = []

    def load(self, node):
        self.name = node.attrib['name']

        self.setProperties(loadProperties(node.find('properties')))
        tilesLayerName = self.properties.get('layer', None)

        self.tilesLayer = self.parentMap.getLayer(tilesLayerName)

        self.paths = {}
        self.platforms = []

        for obj in node.findall('object'):
            if obj.attrib['type'] == 'path':  # This is a path, store it in pathList
                name = obj.attrib['name']
                properties = loadProperties(obj.find('properties'))
                polyline = [[int(v) for v in i.split(',')] for i in obj.find('polyline').attrib['points'].split(' ')]

                if len(polyline) > 0:
                    origX, origY = int(obj.attrib['x']), int(obj.attrib['y'])
                    x, y = origX + polyline[0][0], origY + polyline[0][1]
                    polyline = polyline[1:]

                    segments = []
                    for line in polyline:
                        xf, yf = origX + line[0], origY + line[1]
                        segments.append(paths.PathSegment(x, y, xf-x, yf-y))
                        x = origX + line[0]
                        y = origY + line[1]

                    self.paths[name] = paths.Path(segments, properties)

                    logger.debug('Path {} {}'.format(name, self.paths[name]))
            elif obj.attrib['type'] == 'platform':
                if self.tilesLayer is None:
                    logger.error('Linking to an unexistent layer: {}. Skipped'.format(tilesLayerName))
                    continue

                name = obj.attrib['name']
                properties = loadProperties(obj.find('properties'))
                startX, startY = int(obj.attrib['x']), int(obj.attrib['y'])
                width, height = int(obj.attrib.get('width', self.parentMap.tileWidth)), int(obj.attrib.get('height', self.parentMap.tileHeight))

                # Build graphic object from tiles
                logger.debug('Building image of {}x{}'.format(width, height))
                image = self.getRenderer().image(width, height)
                image.fill((0, 0, 0, 0))  # Transparent background

                for y in range(startY, startY+height, self.parentMap.tileHeight):
                    t = []
                    for x in range(startX, startX+width, self.parentMap.tileWidth):
                        tile = self.tilesLayer.getObjectAt(x, y)
                        tile.blit(image, pygame.Rect(x-startX, y-startY, self.parentMap.tileWidth, self.parentMap.tileHeight))

                p = ObjectWithPath(self, pygame.Rect(startX, startY, width, height), image, properties)
                self.platforms.append(p)

                logger.debug('Platform {}'.format(p))

            # Get obj properties to know that is this
        # After loading, add pathList to Platforms
        erroneous = []
        for p in self.platforms:
            if p.path is None:
                continue
            try:
                p.path = self.paths[p.path]
            except KeyError:
                logger.error('Path {} doesn\'t exists (found on platform {}, on layer {})!!'.format(p.path, p.name, self.name))
                erroneous.append(k)

        for p in erroneous:
            self.platforms.remove(p)

    def onDraw(self, renderer, rect):
        for obj in self.platforms:
            if obj.collide(rect):
                obj.draw(renderer, rect)

    def onUpdate(self):
        for obj in self.platforms:
            obj.update()

    def getCollisions(self, rect):
        for obj in self.platforms:
            if obj.collide(rect):
                yield (obj.getRect(), obj)

    def getObject(self, objecName):
        for obj in self.platforms:
            if obj.name == objecName:
                return obj
        return None

    def getPath(self, pathName):
        return self.paths.get(pathName)

    def __iter__(self):
        for obj in self.platforms:
            yield obj

    def __unicode__(self):
        return 'Dinamyc Layer'
