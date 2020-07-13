# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pygame
import os
from game.util import resource_path
from game.util import classProperty

import logging

logger = logging.getLogger(__name__)

class SoundObject(object):
    def play():
        pass
    
    def stop():
        pass

class Sound(SoundObject):
    def __init__(self, fileName, volume=1.0):
        logger.debug('Loading sound {}'.format(resource_path(fileName)))
        self.sound = pygame.mixer.Sound(resource_path(fileName))
        self.sound.set_volume(volume)

    def play(self):
        self.sound.play()

    def stop(self):
        self.sound.stop()

class Music(SoundObject):
    def __init__(self, fileName, volume=1.0):
        logger.debug('Loading music {}'.format(resource_path(fileName)))
        self.musicFile = resource_path(fileName)
        self.volume = volume
        
    def play(self):
        pygame.mixer.music.load(self.musicFile)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)

    def stop(self):
        pygame.mixer.music.stop()

class SoundsStore(object):
    SOUNDS_DIR = 'data/sounds'
    MUSIC_DIR = 'data/music'
    _store = None

    def __init__(self):
        if pygame.mixer.get_init() is None:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            # pygame.mixer.set_num_channels(16)
        self.sounds = {}
        
    @classProperty
    def store(cls):
        if cls._store is None:
            cls._store = SoundsStore()
        return cls._store

    def storeSound(self, soundName, soundObj, force=False):
        if soundName in self.sounds and force is False:
            logger.debug('Already stored, skipping')
            return self.sounds[soundName]
        self.sounds[soundName] = soundObj
        return soundObj

    def storeSoundFile(self, soundName, fileName, volume=1.0, force=False):
        logger.debug('Storing sound file {}={}'.format(soundName, fileName))
        return self.storeSound(soundName, Sound(os.path.join(SoundsStore.SOUNDS_DIR, fileName), volume), force)
        
    def storeMusicFile(self, musicName, fileName, volume=1.0, force=False):
        logger.debug('Storing music file {}={}'.format(musicName, fileName))
        return self.storeSound(musicName, Music(os.path.join(SoundsStore.MUSIC_DIR, fileName), volume), force)

    def get(self, soundName):
        return self.sounds.get(soundName)
