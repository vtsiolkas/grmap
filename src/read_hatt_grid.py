#!/usr/bin/python
# -*- coding: utf-8 -*-
from conversions.hatt import read_coefficients, find_regions

# regions = read_coefficients()

e   = 775089.0360000001
n   = 4071164.047999999
uvx = 8.929970003749568
uvy = 0.3002740907390962
vvx = -0.3587167999999132
vvy = 11.09792120000049
w   = 2667.0
h   = 2500.0


ulx = e + vvx * h
uly = n + vvy * h
lrx = e + uvx * w
lry = n + uvy * w
urx = ulx + uvx * w
ury = uly + uvy * w


print(ulx, uly)
print(lrx, lry)
print(urx, ury)
