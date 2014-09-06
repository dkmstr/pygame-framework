# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import os

import logging

logger = logging.getLogger(__name__)


# For loading from pyinstaller
def resource_path(relative):

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)

    return os.path.join(relative)


def loadProperties(node):
    props = {}
    if node is not None:
        for p in node.findall('property'):
            logger.debug('Found property {}={}'.format(p.attrib['name'], p.attrib['value']))
            props[p.attrib['name']] = p.attrib['value']
    return props


def checkTrue(value):
    return unicode(value).lower() == 'true'


class classProperty(property):
    """Subclass property to make classmethod properties possible"""
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()
