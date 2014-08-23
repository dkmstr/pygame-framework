# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import os


def resource_path(relative):

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)

    return os.path.join(relative)
