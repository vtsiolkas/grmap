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

def dm_to_decimal(f):
	moires, lepta = str(f).split('.')
	lepta = int(int(lepta) * 100 / 60)
	res = moires + '.' + str(lepta)
	return float(res)

# a = Proj('+proj=latlong +ellps=GRS80 +towgs84=-199.87,74.79,246.62')
astlon = 23.7163375

alat = dm_to_decimal(39.39)
alon = dm_to_decimal(-1.57)
blat = dm_to_decimal(39.45)
blon = dm_to_decimal(-1.45)

# Bessel params.... check + and - (probably inverted)
# towgs84='456.39,372.62,496.82,-12.664e-6,-5.620e-6,-10.854e-6,15.9e-6'

a = Proj(proj='aeqd',ellps='bessel',pm='athens',lon_0=alon,lat_0=alat)
b = Proj(proj='aeqd',ellps='bessel',pm='athens',lon_0=blon,lat_0=blat)

x, y, z = transform(a, b, -1500, -5000, 0)
print(x, y)
