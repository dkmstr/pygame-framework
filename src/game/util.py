# -*- coding: utf-8 -*-
import sys
import os
import logging
import typing

if typing.TYPE_CHECKING:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


# For loading from pyinstaller
def resource_path(relativePath: str) -> str:

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(getattr(sys, '_MEIPASS'), relativePath)

    return os.path.join(relativePath)


def loadProperties(node: typing.Optional['ET.Element']) -> typing.Dict[str, str]:
    props = {}
    if node:
        for p in node.findall('property'):
            logger.debug(
                'Found property {}={}'.format(p.attrib['name'], p.attrib['value'])
            )
            props[p.attrib['name']] = p.attrib['value']
    return props


def checkTrue(value: typing.Any) -> bool:
    return str(value).lower() == 'true'


class classProperty(property):
    """Subclass property to make classmethod properties possible"""

    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()
