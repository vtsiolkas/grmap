#!/usr/bin/python
# -*- coding: utf-8 -*-

class HATTRegion(object):
    def __init__(self, name, f, l, a, b):
        self.name = name
        self.f = f.strip()
        self.l = l.strip()
        self.a = a
        self.b = b

    def __repr__(self):
        return self.name

def read_coefficients():
    with open('coeff_without_megisti.csv', 'r', encoding='utf-8') as f:
        coeffs = []
        lines = f.readlines()
    for line in lines:
        p = line.split(';')
        a = [float(p[x]) for x in range(1,7)]
        b = [float(p[x]) for x in range(7,13)]
        coeffs.append(HATTRegion(p[13], p[14], p[15], a, b))
    return coeffs

def trans_hatt_egsa(x, y, region):
    a = region.a
    b = region.b
    resx = a[0] + a[1]*x + a[2]*y + a[3]*(x**2) + a[4]*(y**2) + a[5]*x*y
    resy = b[0] + b[1]*x + b[2]*y + b[3]*(x**2) + b[4]*(y**2) + b[5]*x*y
    return resx, resy

def find_regions(f, l):
    regions = read_coefficients()
    wanted = []
    for region in regions:
        if region.f == f:
            if region.l == l:
                wanted.append(region)
    return wanted
