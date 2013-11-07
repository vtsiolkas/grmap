#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyproj import Proj, transform

wgs = Proj(init='epsg:4326')
egsa = Proj(init='epsg:2100')

def trans_to_egsa(x, y):
    x1, y1, z1 = transform(wgs, egsa, x, y, 0)
    # print "---------------------------\nTransformation from WGS84 to EGSA87:\n------------------------------"
    # print "WGS84: %f,%f" % (x,y)
    # print "EGSA87: %f,%f" % (x1,y1)
    return x1, y1

def trans_to_wgs(x, y):
    x1, y1, z1 = transform(egsa, wgs, x, y, 0)
    # print "---------------------------\nTransformation from EGSA87 to WGS84:\n------------------------------"
    # print "EGSA87: %f,%f" % (x,y)
    # print "WGS84: %f,%f" % (x1,y1)
    return x1, y1