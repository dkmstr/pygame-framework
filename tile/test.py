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
x = y = 0
x_speed = 0
y_speed = 0

while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            if event.key == 113:
                run = False
            elif event.key == K_RIGHT:
                x_speed = 1
            elif event.key == K_LEFT:
                x_speed = -1
            elif event.key == K_UP:
                y_speed = -1
            elif event.key == K_DOWN:
                y_speed = 1

        if event.type == KEYUP:
            if event.key in (K_RIGHT, K_LEFT):
                x_speed = 0
            elif event.key in (K_UP, K_DOWN):
                y_speed = 0

    m.draw(screen, x, y)
    x += x_speed
    y += y_speed

    t = pygame.time.get_ticks()
    #pygame.time.wait(60-t+t_ref)
    pygame.display.flip()
    screen.fill(0)

    #caption = "{} - FPS: {:.2f}".format('Tile map', clock.get_fps())
    #pygame.display.set_caption(caption)

pygame.quit()
