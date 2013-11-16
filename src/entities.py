#!/usr/bin/python
# -*- coding: utf-8 -*-
from conversions.conversions import trans_wgs_egsa, trans_egsa_wgs
import math


class Point(object):
    def __init__(self, x, y, z,source='ΕΓΣΑ87', region=None):
        if source == 'WGS84':
            self.x, self.y, self.z = trans_wgs_egsa(x, y, z)
        elif source == 'HATT':
            if not region:
                raise Exception('Δεν έδωσες κέντρο φύλλου χάρτη HATT')
            self.x, self.y = region.to_egsa(x, y)
            self.z = z
        else:
            self.x = x
            self.y = y
            self.z = z

    def to_wgs(self):
        return trans_egsa_wgs(self.x, self.y, self.z)

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

    def to_wgs(self):
        llx, lly, llz = self.ll.to_wgs()
        urx, ury, urz = self.ur.to_wgs()
        return '%s,%s,%s,%s' % (llx, lly, urx, ury)

    def ul_egsa_through_wgs(self):
        llx, lly, llz = self.ll.to_wgs()
        urx, ury, urz = self.ur.to_wgs()
        ulx, uly, ulz = llx, ury, llz
        return Point(ulx, uly, ulz, 'WGS84')

    def lr_egsa_through_wgs(self):
        llx, lly, llz = self.ll.to_wgs()
        urx, ury, urz = self.ur.to_wgs()
        lrx, lry, lrz = urx, lly, llz
        return Point(lrx, lry, lrz, 'WGS84')
