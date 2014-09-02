# -*- coding: utf-8 -*-

import pygame
from game.util import resource_path

import logging

logger = logging.getLogger(__name__)


class Images(object):
    '''
    Resources are images that must be scaled with display
    '''

    def __init__(self, baseRes):
        logger.debug('baseRes: {}'.format(baseRes))
        self.baseRes = baseRes
        self.images = {}

    def addImage(self, imgId, path):
        logger.debug('Adding image {} --> {}'.format(imgId, path))
        self.images[imgId] = {
            'path': resource_path(path),
            'surface': None,
        }

    def load(self, screen):
        '''
        We may add some "callback" later to this
        '''
        display_size = screen.get_size()
        logger.debug('Display size: {}'.format(display_size))
        for imgId, img in self.images.iteritems():
            try:
                image = (pygame.image.load(img['path']))
            except:
                logger.exception('Image not found!')

            if ".png" in img['path']:
                image = image.convert_alpha()
            else:
                image = image.convert()

            img_size = image.get_size()
            proportion = float(display_size[1]) / self.baseRes[1]  # Proportion is based on height, not widht
            logger.debug('Image {0} has {1} size and {2} proportion'.format(img['path'], img_size, proportion))
            img_size = (int(img_size[0] * proportion), int(img_size[1] * proportion))
            logger.debug('Image {0} has been changed to {1} size and {2} proportion'.format(img['path'], img_size, proportion))

            img['surface'] = pygame.transform.scale(image, img_size)

    def get(self, imgId):
        return self.images[imgId]['surface']
