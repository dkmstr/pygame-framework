# -*- coding: utf-8 -*-

import typing

import pygame

from game.debug import drawDebugRect

if typing.TYPE_CHECKING:
    from game.interfaces import Collidable


class QuadTree:

    MAX_OBJECTS = 10  # Maximun number of objects in quadtree node
    MAX_LEVELS = 5  # Maximun levels of nodes

    level: int
    bounds: pygame.rect.Rect
    objects: typing.List['Collidable']
    nodes: typing.List['QuadTree']

    def __init__(self, level: int, bounds: pygame.rect.Rect) -> None:
        """
        Initialize a quadtree node.

        Args:
            level (int): Current quadtree level. Only informative.
            bounds (pygame.rect.Rect): A rect that will contain all objects in the quadtree.
        """
        self.level = level
        self.bounds = bounds.copy()
        self.objects = []
        self.nodes = []

    def clear(self) -> None:
        """
        Remove all objects from the quadtree node.
        """
        for n in self.nodes:
            n.clear()

        self.nodes[:] = []
        self.objects[:] = []

    def _split(self) -> None:
        '''
        Splits node in 4 quadtrees
        '''
        width, height = self.bounds.size
        midWidth, midHeight = width // 2, height // 2
        endWidth, endHeight = width - midWidth, height - midHeight

        x, y = self.bounds.topleft

        self.nodes = [
            QuadTree(self.level + 1, pygame.Rect(x, y, midWidth, midHeight)),
            QuadTree(self.level + 1, pygame.Rect(x + midWidth, y, endWidth, midHeight)),
            QuadTree(
                self.level + 1, pygame.Rect(x, y + midHeight, midWidth, endHeight)
            ),
            QuadTree(
                self.level + 1,
                pygame.Rect(x + midWidth, y + midHeight, midWidth, endHeight),
            ),
        ]

    def _getInsertNode(self, rect: pygame.rect.Rect) -> typing.Optional['QuadTree']:
        '''
        Inserting a node into a quad must make that quad to fully hold the rect
        '''
        for node in self.nodes:
            if node.bounds.contains(rect):
                return node

        return None

    def _getCollideNodes(self, rect: pygame.Rect) -> typing.Iterable['QuadTree']:
        for node in self.nodes:
            if node.bounds.colliderect(rect):
                yield node

    def insert(self, obj: 'Collidable') -> None:
        node = self._getInsertNode(obj.getColRect())
        if node:
            node.insert(obj)
            return

        self.objects.append(obj)

        if (
            len(self.objects) > QuadTree.MAX_OBJECTS
            and self.level < QuadTree.MAX_LEVELS
        ):
            if not self.nodes:
                self._split()

            total = len(self.objects)
            i = 0
            while i < total:
                node = self._getInsertNode(self.objects[i].getColRect())
                if node is not None:    
                    node.insert(self.objects[i])
                    del self.objects[i]
                else:
                    i += 1

    def retrieve(self, rect: pygame.Rect) -> typing.Iterable['Collidable']:
        '''
        Return all "possible" collidables in rect
        '''
        for node in self._getCollideNodes(rect):
            for i in node.retrieve(rect):
                yield i

        for i in self.objects:
            yield i

    def draw(self, toSurface, rect: pygame.Rect) -> None:
        '''
        For debugging purposes, draws quadtree & collisions rects
        '''
        bounds = self.bounds.move(-rect.x, -rect.y)
        drawDebugRect(
            toSurface, bounds, (self.level * 40, 0, 0, 0), 2 * (6 - self.level)
        )
        for obj in self.objects:
            drawDebugRect(
                toSurface,
                obj.getColRect().move(-rect.x, -rect.y),
                (0, self.level * 50, 0, 0),
                1,
            )
        if self.nodes is not None:
            for n in self.nodes:
                n.draw(toSurface, rect)
