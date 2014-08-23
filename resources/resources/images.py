# -*- coding: utf-8 -*-

import pygame


class Images(object):
    '''
    Resources are images that must be scaled with display
    '''

    def __init__(self, baseRes):
        self._baseRes = baseRes
        self._resources = {}

    def addImage(self, resId, path):
        self._resources[resId] = {
            'path': path,
            'surface': None,
        }

    def load(self, screen):
        '''
        We may add some "callback" later to this
        '''
        display_size = screen.get_size()
        print 'Display_size: ', display_size
        for resId, resource in self._resources.iteritems():
            try:
                image = (pygame.image.load(resource['path']))
            except:
                print "Image not found!"

            if ".png" in resource['path']:
                image = image.convert_alpha()
            else:
                image = image.convert()

            img_size = image.get_size()
            proportion = float(display_size[1]) / self._baseRes[1]  # Proportion is based on height, not widht
            print 'Image {0} has {1} size and {2} proportion'.format(resource['path'], img_size, proportion)
            img_size = (int(img_size[0] * proportion), int(img_size[1] * proportion))
            print 'Image {0} has {1} size and {2} proportion'.format(resource['path'], img_size, proportion)

            resource['surface'] = pygame.transform.scale(image, img_size)

    def get(self, resId):
        return self._resources[resId]['surface']
