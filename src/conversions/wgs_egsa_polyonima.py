#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyproj import Proj, transform

def to_sec(degrees):
	return degrees * 3600.0

def to_deg(secs):
	return secs / 3600

def dm_to_decimal(f):
	moires, lepta = str(f).split('.')
	lepta = int(int(lepta) * 100 / 60)
	res = moires + '.' + str(lepta)
	return float(res)


f0 = dm_to_decimal(39.35)
l0 = dm_to_decimal(22.26)
f1 = to_sec(f0)
l1 = to_sec(l0)

a0 = -9.34
a1 = 0.02
a2 = 0.05
b0 = -6.1
b1 = -0.08
b2 = -0.11


f2 = f1 + a0 + a1 * to_sec(f0 - 38) + a2 * to_sec(l0 - 24)
l2 = l1 + b0 + b1 * to_sec(f0 - 38) + b2 * to_sec(l0 - 24)

f2, l2 = to_deg(f2), to_deg(l2)
print(f2, l2)

a = Proj(proj='latlong',ellps='GRS80',pm='athens',lon_0='23.7163375')
egsa = Proj(init='epsg:2100')

# 365307.716		4382398.584

x, y, z = transform(a, egsa, l2, f2, 0)
print(x, y, z)

