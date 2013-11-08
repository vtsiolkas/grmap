#!/usr/bin/python
# -*- coding: utf-8 -*-
from conversions import trans_to_egsa, trans_to_wgs
import math


class Point(object):
    def __init__(self, x, y, z,source=2100):
        if source == 4326:
            self.x, self.y, self.z = trans_to_egsa(x, y, z)
        else:
            self.x = x
            self.y = y
            self.z = z

    def wgs(self):
        return trans_to_wgs(self.x, self.y, self.z)

    def __str__(self):
        return ','.join([str(c) for c in list(self.egsa())])


class Box(object):
    def __init__(self, ll, ur):
        self.ll = ll
        self.ul = Point(ll.x, ur.y, ll.z)
        self.ur = ur
        self.lr = Point(ur.x, ll.y, ll.z)
        self.w = self.lr.x - self.ll.x
        self.h = self.ul.y - self.ll.y

    def __str__(self):
        return ','.join(str(c) for c in (self.ll.x, self.ll.y, self.ur.x, self.ur.y))

    def wgs(self):
        llx, lly, llz = self.ll.wgs()
        urx, ury, urz = self.ur.wgs()
        return '%s,%s,%s,%s' % (llx, lly, urx, ury)

    def ul_egsa_through_wgs(self):
        llx, lly, llz = self.ll.wgs()
        urx, ury, urz = self.ur.wgs()
        ulx, uly, ulz = llx, ury, llz
        return Point(ulx, uly, ulz, 4326)

    def lr_egsa_through_wgs(self):
        llx, lly, llz = self.ll.wgs()
        urx, ury, urz = self.ur.wgs()
        lrx, lry, lrz = urx, lly, llz
        return Point(lrx, lry, lrz, 4326)
