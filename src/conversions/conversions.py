#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyproj import Proj, transform
from hatt import REGIONS

wgs = Proj(init='epsg:4326')
egsa = Proj(init='epsg:2100')

def trans_wgs_egsa(x, y, z):
    ex, ey, ez = transform(wgs, egsa, x, y, z)
    return ex, ey, ez

def trans_egsa_wgs(x, y, z):
    wx, wy, wz = transform(egsa, wgs, x, y, z)
    return wx, wy, wz

def dm_to_decimal(d):
	# Transforms 39.45(which means 39°45') to true decimal deg 39.75 Used for HATT now
	moires, lepta = str(d).split('.')
	lepta = int(int(lepta) * 100 / 60)
	res = moires + '.' + str(lepta)
	return float(res)

def small_hatt_container(f, l):
	f, l = dm_to_decimal(f), dm_to_decimal(l)
	a = Proj(proj='aeqd',ellps='bessel',pm='athens',lon_0=l,lat_0=f)
	pos_points = [
    	[transform(a, egsa, 1000, 1000, 0)],
    	[transform(a, egsa, 1000, -1000, 0)],
    	[transform(a, egsa, -1000, 1000, 0)],
    	[transform(a, egsa, -1000, -1000, 0)]
    ]
    result = []
    for ps in pos_points:
    	for region in REGIONS:
    		if region.contains_egsa_point(ps[0], ps[1]):
    			if region not in result:
    				result.append(region)
    return result
