#!/usr/bin/python
# -*- coding: utf-8 -*-
from conversions import trans_to_egsa, trans_to_wgs
import math


class Point(object):
    def __init__(self, x, y, source=4326):
        if source == 2100:
            self.x, self.y = trans_to_wgs(x, y)
        else:
            self.x = x
            self.y = y

    def wgs(self):
        return self.x, self.y

    def egsa(self):
        return trans_to_egsa(self.x, self.y)

    def __str__(self):
        return ','.join([str(c) for c in list(self.egsa())])


class Box(object):
    def __init__(self, ll, ur):
        self.ll = ll
        self.lr = Point(ur.x, ll.y)
        self.ul = Point(ll.x, ur.y)
        self.ur = ur
        self.width = self.square_width()
        self.height = self.square_height()

    def wgs(self):
        return ','.join(str(c) for c in (self.ll.x, self.ll.y, self.ur.x, self.ur.y))

    def egsa(self):
        return (trans_to_egsa(self.ll.x, self.ll.y),
                trans_to_egsa(self.ul.x, self.ul.y),
                trans_to_egsa(self.ur.x, self.ur.y),
                trans_to_egsa(self.lr.x, self.lr.y))

    def square_width(self):
        llx, lly = trans_to_egsa(self.ll.x, self.ll.y)
        urx, ury = trans_to_egsa(self.ur.x, self.ur.y)
        return urx - llx

    def square_height(self):
        llx, lly = trans_to_egsa(self.ll.x, self.ll.y)
        urx, ury = trans_to_egsa(self.ur.x, self.ur.y)
        return ury - lly

    def egsa_width(self):
        llx, lly = trans_to_egsa(self.ll.x, self.ll.y)
        lrx, lry = trans_to_egsa(self.lr.x, self.lr.y)
        return lrx - llx

    def egsa_height(self):
        llx, lly = trans_to_egsa(self.ll.x, self.ll.y)
        ulx, uly = trans_to_egsa(self.ul.x, self.ul.y)
        return uly - lly

    def egsa_rotation(self):
        """DEPRECATED - Using pixmap transformations now
        Calculates mean rotation angle for left and right side of box
        """
        llx, lly = self.ll.egsa()
        ulx, uly = self.ul.egsa()
        dx = ulx - llx
        dy = uly - lly
        lrads = math.atan2(dy, -dx)
        lrads -= math.pi/2
        langle = math.degrees(lrads)

        lrx, lry = self.lr.egsa()
        urx, ury = self.ur.egsa()
        dx = urx - lrx
        dy = ury - lry
        rrads = math.atan2(dy, -dx)
        rrads -= math.pi/2
        rangle = math.degrees(rrads)

        angle = (langle + rangle) / 2
        return angle
