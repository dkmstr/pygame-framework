# -*- coding: utf-8 -*-

from maps import Maps
from images import Images
from game_state import GameControl
from game_state import GameState


def resource_path(relative):
    import sys
    import os

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)

    return os.path.join(relative)
