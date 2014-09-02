# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from game.actors import actorsFactory
from game.actors import Actor

import logging

logger = logging.getLogger(__name__)


class Key(Actor):
    pass

actorsFactory.registerType('YellowKey', Key)
