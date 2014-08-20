#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
from pygame.locals import *
import resources

pygame.init()
screen = pygame.display.set_mode((640, 480), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.mouse.set_visible(0)


maps = resources.Maps()
maps.add('level0', 'data/test.tmx')
#maps.add('level1', 'data/test1.tmx')

maps.load()

m = maps.get('level0')
m.drawTo(screen, 0, 100)

#clock = pygame.time.Clock()

run = True
full = False
t_ref = 0
x = 0
while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            if event.key == 113:
                run = False
        if event.type == KEYUP:
            pass

    m.drawTo(screen, x, 100)
    x += 1

    t = pygame.time.get_ticks()
    #pygame.time.wait(60-t+t_ref)
    pygame.display.flip()
    screen.fill(0)

    #caption = "{} - FPS: {:.2f}".format('Tile map', clock.get_fps())
    #pygame.display.set_caption(caption)

pygame.quit()
