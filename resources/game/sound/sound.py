# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import os
from game.util import resource_path

import logging

logger = logging.getLogger(__name__)

class Sound(object):
    def __init__(self, fileName, volume=1.0):
        self.sound = pygame.mixer.Sound(resource_path(fileName))
        self.sound.set_volume(volume)
    
    def play(self):
        self.sound.play()
        
    def stop(self):
        self.sound.stop()
        
        
class SoundsStore(object):
    SOUNDS_DIR = 'data/sounds'
    
    def __init__(self):
        if pygame.mixer.get_init() is None:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            # pygame.mixer.set_num_channels(16)
        self.sounds = {}

    def store(self, soundName, sound, volume=1.0, force=False):
        if soundName in self.sounds and force is False:
            return
        self.sounds[soundName] = sound
        
    def storeFile(self, soundName, fileName, volume=1.0, force=False):
        self.store(soundName, pygame.mixer.Sound(os.path.join(SoundsStore.SOUNDS_DIR, fileName)), volume, force)

    def get(self, soundName):
        return self.sounds[soundName]

    