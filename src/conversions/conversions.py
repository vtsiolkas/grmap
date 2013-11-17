#!/usr/bin/python
# -*- coding: utf-8 -*-
from pyproj import Proj, transform
from conversions.hatt import REGIONS

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

def hatt_egsa_fast(x, y, f, l):
    f = dm_to_decimal(f)
    l = dm_to_decimal(l)
    hatt = Proj(proj='aeqd',ellps='bessel',pm='athens',lat_0=f,lon_0=l,towgs84='456.39,372.62,496.82,-12.664e-6,-5.620e-6,-10.854e-6,15.9e-6')
    ex, ey, z = transform(hatt, egsa, x, y, 0)
    result = []
    for region in REGIONS:
        if region.contains_egsa_point(ex, ey):
            result.append(region)
    if result:
        if len(result) > 1:
            print('Parapanw apo mia hatt regions:', result)
        return result[0]
    return result

def tm3_egsa_fast(x, y, f):
    tm3 = Proj(proj='tmerc',ellps='bessel',pm='athens',lon_0=f,lat_0='34',k_0='0.9999',x_0='200000',towgs84='456.39,372.62,496.82,-12.664e-6,-5.620e-6,-10.854e-6,15.9e-6')
    ex, ey, z = transform(tm3, egsa, x, y, 0)
    result = []
    for region in REGIONS:
        if region.contains_egsa_point(ex, ey):
            result.append(region)
    if result:
        if len(result) > 1:
            print('Parapanw apo mia hatt regions:', result)
        return result[0]
    return result
