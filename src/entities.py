#!/usr/bin/python
# -*- coding: utf-8 -*-
from conversions.conversions import *
from pyproj import Proj, transform
import math

class Point(object):
    def __init__(self, x=None, y=None, z=0, name=None):
        self.x = x
        self.y = y
        self.z = z
        self.name = name

    def bhatt_egsa(self):
        a = self.region.a
        b = self.region.b
        x = self.x
        y = self.y
        self.x = a[0] + a[1]*x + a[2]*y + a[3]*(x**2) + a[4]*(y**2) + a[5]*x*y
        self.y = b[0] + b[1]*x + b[2]*y + b[3]*(x**2) + b[4]*(y**2) + b[5]*x*y

    def shatt_bhatt(self, f, l):
        sf = dm_to_decimal(f)
        sl = dm_to_decimal(l)
        bf = dm_to_decimal(self.region.f)
        bl = dm_to_decimal(self.region.l)
        shatt = Proj(proj='aeqd',ellps='bessel',pm='athens',lat_0=sf,lon_0=sl)
        bhatt = Proj(proj='aeqd',ellps='bessel',pm='athens',lat_0=bf,lon_0=bl)
        self.x, self.y, self.z = transform(shatt, bhatt, self.x, self.y, self.z)

    def wgs_egsa(self):
        self.x, self.y, self.z = trans_wgs_egsa(self.x, self.y, self.z)

    def tm3_bhatt(self, f):
        bf = dm_to_decimal(self.region.f)
        bl = dm_to_decimal(self.region.l)
        tm3 = Proj(proj='tmerc',ellps='bessel',pm='athens',lon_0=f,lat_0='34',k_0='0.9999',x_0='200000')
        bhatt = Proj(proj='aeqd',ellps='bessel',pm='athens',lat_0=bf,lon_0=bl)
        self.x, self.y, self.z = transform(tm3, bhatt, self.x, self.y, self.z)



class MapPoint(object):
    def __init__(self, x, y, z,source='ΕΓΣΑ87'):
        if source == 'WGS84':
            self.x, self.y, self.z = trans_wgs_egsa(x, y, z)
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
        self.ul = MapPoint(ll.x, ur.y, ll.z)
        self.ur = ur
        self.lr = MapPoint(ur.x, ll.y, ll.z)
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
        return MapPoint(ulx, uly, ulz, 'WGS84')

    def lr_egsa_through_wgs(self):
        llx, lly, llz = self.ll.to_wgs()
        urx, ury, urz = self.ur.to_wgs()
        lrx, lry, lrz = urx, lly, llz
        return MapPoint(lrx, lry, lrz, 'WGS84')
