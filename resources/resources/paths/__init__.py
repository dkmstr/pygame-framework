# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


class PathSegment(object):
    def __init__(self, x, y, x_offset, y_offset):
        self.x, self.y, self.x_offset, self.y_offset = x, y, x_offset, y_offset

        # Calculate gradient
        if x_offset == 0 and y_offset == 0:
            self.x_step = self.y_step = 0
            self.x_at_end = self.y_at_end = lambda x: True
        else:
            div = abs(x_offset) if abs(x_offset) > abs(y_offset) else abs(y_offset)
            self.x_step = (x_offset << 16) / div

            if self.x_step > 0:
                self.x_at_end = lambda x: x >= self.x + self.x_offset
            else:
                self.x_at_end = lambda x: x <= self.x + self.x_offset

            self.y_step = (y_offset << 16) / div

            if self.y_step > 0:
                self.y_at_end = lambda y: y >= self.y + self.y_offset
            else:
                self.y_at_end = lambda y: y <= self.y + self.y_offset

    def getCoords(self, position, step):
        '''
        Very aproximate position using only integers
        '''
        position *= step
        x, y = self.x + ((self.x_step*position) >> 16), self.y + ((self.y_step*position) >> 16)
        if self.x_at_end(x) and self.y_at_end(y):
            return None  # Out of line
        return (x, y)
    
    def __unicode__(self):
        return 'PathSegment: ({},{})-({},{}) {},{}'.format(self.x, self.y, self.x + self.x_offset, self.y + self.y_offset, self.x_step, self.y_step)


######################
# Path               #
######################
class Path(object):
    def __init__(self, segments, properties):
        self.segments = segments
        self.properties = properties
        self.reset()

    def updateAttributes(self):
        self.step = int(self.properties.get('step', '1'))
        self.bounce = self.properties.get('bounce', 'False') == 'False'

    def reset(self):
        self.segment = 0
        self.segment_pos = 0
        self.updateAttributes()

    def iterate(self):
        if self.segment >= len(self.segments):
            return None
        pos = self.segments[self.segment].getCoords(self.segment_pos, self.step)
        if pos is None:
            self.segment += 1
            self.segment_pos = 0
            pos = self.iterate()
            if pos is None:
                self.reset()
                return self.iterate()
        else:
            self.segment_pos += 1
        return pos
    
    def save(self):
        self.saved = (self.segment, self.segment_pos)
        
    def restore(self):
        self.segment, self.segment_pos = self.saved

    def __unicode__(self):
        return 'Path: {}'.format([unicode(s) for s in self.segments])
