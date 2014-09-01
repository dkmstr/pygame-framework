# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from resources.actors import actorsFactory
from resources.actors import Actor

import pygame

import logging

logger = logging.getLogger(__name__)


class Key(Actor):
    pass

actorsFactory.registerType('YellowKey', Key)
