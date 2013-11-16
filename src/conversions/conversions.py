#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyproj import Proj, transform

wgs = Proj(init='epsg:4326')
egsa = Proj(init='epsg:2100')

def trans_wgs_egsa(x, y, z):
    ex, ey, ez = transform(wgs, egsa, x, y, z)
    return ex, ey, ez

def trans_egsa_wgs(x, y, z):
    wx, wy, wz = transform(egsa, wgs, x, y, z)
    return wx, wy, wz
