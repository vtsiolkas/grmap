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

astlon = 23.7163375

blat = dm_to_decimal(39.45)
blon = dm_to_decimal(-1.45)

a = Proj(proj='tmerc',ellps='bessel',pm='athens',lon_0='-3',lat_0='34',k_0='0.9999',x_0='200000',towgs84='456.39,372.62,496.82,-12.664e-6,-5.620e-6,-10.854e-6,15.9e-6')
b = Proj(proj='aeqd',ellps='bessel',pm='athens',lon_0=blon,lat_0=blat)
x, y, z = transform(a, b, 291173.529, 615474.824, 0)
print(x, y)


# bessel from  towgs84='456.39,372.62,496.82,-12.664e-6,-5.620e-6,-10.854e-6,15.9e-6'