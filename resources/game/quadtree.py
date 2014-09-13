# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame

from game.debug import drawDebugRect
from game.interfaces import Collidable

class QuadTree(object):
    
    MAX_OBJECTS = 10
    MAX_LEVELS = 5
    
    def __init__(self, level, bounds):
        self.level = level
        self.bounds = pygame.Rect(bounds)
        self.objects = []
        self.nodes = None
        
    def clear(self):
        self.objects[:] = []
        if self.nodes is not None:
            for n in self.nodes:
                n.clear()
                
        self.nodes = None
                
    def _split(self):
        width, height = self.bounds.size
        startWidth, startHeight = width / 2, height / 2
        endWidth, endHeight = width - startWidth, height - startHeight
       
        x, y = self.bounds.topleft
        
        self.nodes = (
            QuadTree(self.level+1, pygame.Rect(x, y, startWidth, startHeight)),
            QuadTree(self.level+1, pygame.Rect(x + startWidth, y, endWidth, startHeight)),
            QuadTree(self.level+1, pygame.Rect(x, y + startHeight, startWidth, endHeight)),
            QuadTree(self.level+1, pygame.Rect(x + startWidth, y + startHeight, startWidth, endHeight))
        )
        
    def _getInsertNode(self, rect):
        '''
        Inserting a node into a quad must make that quad to fully hold the rect
        '''
        if self.nodes:
            for node in self.nodes:
                if node.bounds.contains(rect):
                    return node
                    
        return None
    
    def _getCollideNodes(self, rect):
        if self.nodes is not None:
            for node in self.nodes:
                if node.bounds.colliderect(rect):
                    yield node

    def insert(self, obj):
        node = self._getInsertNode(obj.getColRect())
        if node is not None:
            node.insert(obj)
            return
        
        self.objects.append(obj)
        
        if len(self.objects) > QuadTree.MAX_OBJECTS and self.level < QuadTree.MAX_LEVELS:
            if self.nodes is None:
                self._split()
                
            i = 0
            while i <  len(self.objects):
                node = self._getInsertNode(self.objects[i].getColRect())
                if node is not None:
                    node.insert(self.objects[i])
                    del self.objects[i]
                else:
                    i += 1
                    
    def retrieve(self, rect):
        for node in self._getCollideNodes(rect):
            for i in node.retrieve(rect):
                yield i
        
        for i in self.objects:
            yield i
    
    def draw(self, toSurface, rect):
        '''
        For debugging pourposes, draws quadtree & collisions rects
        '''
        bounds = self.bounds.move(-rect.x, -rect.y)
        drawDebugRect(toSurface, bounds, (self.level*40, 0, 0, 0), 2*(6-self.level))
        for obj in self.objects:
            drawDebugRect(toSurface, obj.getColRect().move(-rect.x, -rect.y), (0, self.level*50, 0, 0), 1)
        if self.nodes is not None:
            for n in self.nodes:
                n.draw(toSurface, rect)
        