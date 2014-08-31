# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


def loadProperties(node):
    props = {}
    if node is not None:
        for p in node.findall('property'):
            logger.debug('Found property {}={}'.format(p.attrib['name'], p.attrib['value']))
            props[p.attrib['name']] = p.attrib['value']
    return props

def checkTrue(value):
    return unicode(value).lower() == 'true'

    