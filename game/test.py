#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
from pygame.locals import *
import resources
import parallax

WIDTH = 800
HEIGHT = 600

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.mouse.set_visible(0)

images = resources.Images((1280, 2880))

images.addImage('bck1', 'data/far-background.png')
images.addImage('bck2', 'data/near-background.png')
images.load(screen)

pygame.mixer.music.load('data/forest_0.ogg')
pygame.mixer.music.play(-1)


maps = resources.Maps()
maps.add('level0', 'data/test.tmx')
#maps.add('level1', 'data/test1.tmx')

maps.load()

m = maps.get('level0')

bg = parallax.ParallaxSurface((WIDTH, HEIGHT), pygame.RLEACCEL)

bg.add_surface(images.get('bck1'), 5)
bg.add_surface(images.get('bck2'), 3)

#m.drawTo(screen, 0, 100)

#clock = pygame.time.Clock()

run = True
full = False
t_ref = 0
x = y = 0
x_speed = 0
y_speed = 0
speed = 0
base_speed = 10

while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            if event.key == 113:
                run = False
            elif event.key == K_RIGHT:
                x_speed = 1
                speed = 2
            elif event.key == K_LEFT:
                x_speed = -1
                speed = -2
            elif event.key == K_UP:
                y_speed = -1
            elif event.key == K_DOWN:
                y_speed = 1

        if event.type == KEYUP:
            if event.key in (K_RIGHT, K_LEFT):
                x_speed = 0
                speed = 0
            elif event.key in (K_UP, K_DOWN):
                y_speed = 0

    bg.draw(screen)
    bg.scroll(speed)
    m.drawTo(screen, x, y)
    x += x_speed
    y += y_speed

    t = pygame.time.get_ticks()
    pygame.time.wait(16-t+t_ref)
    t_ref = t
    pygame.display.flip()
    #screen.fill(0)

    #caption = "{} - FPS: {:.2f}".format('Tile map', clock.get_fps())
    #pygame.display.set_caption(caption)

pygame.quit()
