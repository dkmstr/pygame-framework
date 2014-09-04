# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from game import paths
from game.objects import ObjectWithPath
from game.util import loadProperties
from game.layers.layer import Layer

import logging

logger = logging.getLogger(__name__)


class DynamicLayer(Layer):
    LAYER_TYPE = 'dynamic'

    def __init__(self, parentMap=None, layerType=None, properties=None):
        Layer.__init__(self, parentMap, layerType, properties)
        self.width = self.height = 0
        self.tilesLayer = None
        self.paths = {}
        self.platforms = {}

    def load(self, node):
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])

        self.setProperties(loadProperties(node.find('properties')))
        tilesLayerName = self.properties.get('layer', None)

        self.tilesLayer = self.parentMap.getLayer(tilesLayerName)

        self.paths = {}
        self.platforms = {}

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
                    logger.error('Linking to an unexistent layer: {}. Skypped'.format(tilesLayerName))
                    continue

                name = obj.attrib['name']
                properties = loadProperties(obj.find('properties'))
                startX, startY = int(obj.attrib['x']), int(obj.attrib['y'])
                width, height = int(obj.attrib.get('width', self.parentMap.tileWidth)), int(obj.attrib.get('height', self.parentMap.tileHeight))
                tiles = []

                for y in xrange(startY, startY+height, self.parentMap.tileHeight):
                    t = []
                    for x in xrange(startX, startX+width, self.parentMap.tileWidth):
                        t.append(self.tilesLayer.getTileAt(x, y))
                    tiles.append(t)

                p = ObjectWithPath(self, startX, startY, width, height, tiles, properties)
                self.platforms[obj.attrib['name']] = p

                logger.debug('Platform {}'.format(p))

            # Get obj properties to know that is this
        # After loading, add pathList to Platforms
        erroneous = []
        for k, p in self.platforms.iteritems():
            try:
                p.path = self.paths[p.path]
            except KeyError:
                logger.error('Path {} doesn\'t exists!!'.format(p.path))
                erroneous.append(k)

        for k in erroneous:
            del self.platforms[k]

    def onDraw(self, toSurface, rect):
        for obj in self.platforms.itervalues():
            if obj.collide(rect):
                obj.draw(toSurface, rect.x, rect.y)

    def onUpdate(self):
        for obj in self.platforms.itervalues():
            obj.update()

    def getCollisions(self, rect):
        for obj in self.platforms.itervalues():
            if obj.collide(rect):
                yield (obj.getRect(), obj)

    def getObject(self, objecName):
        return self.platforms.get(objecName)

    def getPath(self, pathName):
        return self.paths.get(pathName)

    def __iter__(self):
        for obj in self.platforms.itervalues():
            yield obj

    def __unicode__(self):
        return 'Dinamyc Layer'
