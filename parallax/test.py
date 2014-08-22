#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import resources
import parallax

WIDTH = 800
HEIGHT = 600

WIDTHF = 1920
HEIGHTF = 1050


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.mouse.set_visible(0)


images = resources.Images((1280, 2880))

images.addImage('bck1', 'images/far-background.png')
images.addImage('bck2', 'images/near-background.png')
images.load(screen)

pygame.mixer.music.load('sound/forest_0.ogg')
pygame.mixer.music.play(-1)

#images.get('bck2').set_colorkey((0xff, 0x00, 0xea), pygame.RLEACCEL)
#images.get('bck3').set_colorkey((0xff, 0x00, 0xea), pygame.RLEACCEL)

bg = parallax.ParallaxSurface((WIDTH, HEIGHT), pygame.RLEACCEL)

bg.add_surface(images.get('bck1'), 5)
bg.add_surface(images.get('bck2'), 3)


run = True
full = False
speed = 0
base_speed = 10
t_ref = 0
while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                speed += base_speed
            elif event.key == K_LEFT:
                speed -= base_speed
            elif event.key == 113:
                run = False
            elif event.key == K_f:
                if full is False:
                    screen = pygame.display.set_mode((WIDTHF, HEIGHTF), pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.FULLSCREEN)
                    bg = parallax.ParallaxSurface((WIDTHF, HEIGHTF), pygame.RLEACCEL)
                    base_speed = 60
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
                    bg = parallax.ParallaxSurface((WIDTH, HEIGHT), pygame.RLEACCEL)
                    base_speed = 10
                images.load(screen)
                bg.add_surface(images.get('bck1'), 5)
                bg.add_surface(images.get('bck2'), 3)
                full = not full
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                speed -= base_speed
            if event.key == K_LEFT:
                speed += base_speed

    bg.scroll(speed)
    t = pygame.time.get_ticks()
    pygame.time.wait(60-t+t_ref)
    bg.draw(screen)
    pygame.display.flip()
