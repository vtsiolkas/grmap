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

    def egsa(self):
        return self.x, self.y, self.z

    def __str__(self):
        return ','.join([str(c) for c in list(self.egsa())])


class Box(object):
    def __init__(self, ll, ur):
        self.ll = ll
        self.lr = Point(ur.x, ll.y, ll.z)
        self.ul = Point(ll.x, ur.y, ll.z)
        self.ur = ur
        self.width = self.square_width()
        self.height = self.square_height()

    def egsa(self):
        return ','.join(str(c) for c in (self.ll.x, self.ll.y, self.ur.x, self.ur.y))

    def wgs(self):
        return (trans_to_wgs(self.ll.x, self.ll.y, self.ll.z),
                trans_to_wgs(self.ul.x, self.ul.y, self.ul.z),
                trans_to_wgs(self.ur.x, self.ur.y, self.ur.z),
                trans_to_wgs(self.lr.x, self.lr.y, self.lr.z))

    def square_width(self):
        llx, lly = self.ll.x, self.ll.y
        urx, ury = self.ur.x, self.ur.y
        return urx - llx

    def square_height(self):
        llx, lly = self.ll.x, self.ll.y
        urx, ury = self.ur.x, self.ur.y
        return ury - lly

    def egsa_width(self):
        llx, lly = trans_to_egsa(self.ll.x, self.ll.y)
        lrx, lry = trans_to_egsa(self.lr.x, self.lr.y)
        return lrx - llx

    def egsa_height(self):
        llx, lly = trans_to_egsa(self.ll.x, self.ll.y)
        ulx, uly = trans_to_egsa(self.ul.x, self.ul.y)
        return uly - lly
