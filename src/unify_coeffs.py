#!/usr/bin/python
# -*- coding: utf-8 -*-
from conversions.hatt import read_coefficients

regions1 = read_coefficients()

class LLRegion(object):
    def __init__(self, name, ulx, uly, urx, ury, lrx, lry, llx, lly):
        self.name = name
        self.ulx = ulx
        self.uly = uly
        self.urx = urx
        self.ury = ury
        self.lrx = lrx
        self.lry = lry
        self.llx = llx
        self.lly = lly

    def __repr__(self):
        return self.name

regions2 = []
with open('greek_hatt_bboxes.txt', 'r', encoding='utf-8') as f:
	lines = f.readlines()
lines = [l.strip() for l in lines]
for line in lines:
	l = line.split(':')
	regions2.append(LLRegion(l[0],float(l[1]),float(l[2]),float(l[3]),float(l[4]),float(l[5]),float(l[6]),float(l[7]),float(l[8])))

with open('regionale.txt', 'w', encoding='utf-8') as f:
	for r1 in regions1:
		for r2 in regions2:
			if r2.name == r1.name:
				f.write("HattRegion('%s', '%s', '%s', %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, " % (r1.name, r1.f, r1.l, r2.ulx, r2.uly, r2.urx, r2.ury, r2.lrx, r2.lry, r2.llx, r2.lly))
				f.write(', '.join(map(str, r1.a)) + ', ' + ', '.join(map(str, r1.b)) + '),\n')