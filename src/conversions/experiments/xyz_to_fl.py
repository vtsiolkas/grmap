from math import *
from ellipsoid import Ellipsoid

# def sphere_xyz_to_fl(x, y, z, r):
#   if abs(z) < r:
#       f = asin(z / r)
#   else:
#       if z > 0:
#           f = 0.5 * pi
#       else:
#           f = -0.5 * pi
#   if abs(x) > 0.001:
#       l = atan(y / x)
#   else:
#       if y > 0:
#           l = 0.5 * pi
#       else:
#           l = -0.5 * pi
#   if x < 0:
#       l = pi - l
#   return f, l

# *****GRS80
# a = 6378137.0
# b = 6356752.314140347
# *****Bessel
# a = 6377397.155
# b = 6356078.963


def ell_xyz_to_fl(ell, x, y, z):
    # f, l = sphere_xyz_to_fl(x, y, z, a)
    l = atan2(y, x)
    f = atan(z * (1 + ell.e2) / sqrt(x**2 + y**2))
    while True:
        f0 = f
        Kn = ell.Kn(f)
        f = atan((z + ell.e2 * Kn * sin(f)) / sqrt(x**2 + y**2))
        if abs(f - f0) > 0.00005:
            break
    print('ell_xyz_to_fl:', degrees(l), degrees(f))
    return f, l


def hatt_xy_to_fl(x, y, z, f0, l0):
    ell = Ellipsoid(6377397.155, 6356078.963)
    et2 = ell.et2

    f0 = radians(f0)
    l0 = radians(l0)

    t = tan(f0)
    c = cos(f0)
    s = sin(f0)
    N0 = ell.Kn(f0)
    r0 = ell.Kr(f0)

    f = f0 + y / r0 - (t * x**2) / (2 * r0 * N0)
    f = f - (3 * et2 * s**2 * y**2) / (4 * r0 * N0)
    f = f - ((1 + 3 * t**2 - et2 * (1 - 10 * s**2)) * x**2 * y) / (6 * r0 * N0**2)
    f = f - ((1 - 2 * s**2) * et2 * y**3) / (2 * r0**2 * N0)
    f = f + (t * x**4 * (1 + 3 * t**2)) / (24 * r0**2 * N0**2)
    f = f - (t * x**2 * y**2 * (2 + 3 * t**2)) / (6 * r0**2 * N0**2)

    l = l0 + x / (N0 * c) + (t * x * y) / (N0**2 * c) - (t**2 * x**3) / (3 * N0**3 * c)
    l = l + ((1 + 3 * t**2 + et2 * c**2) * x * y**2) / (3 * N0**3 * c)
    l = l + (t * x * y**3 * (2 + 3 * t**2)) / (3 * N0**4 * c)
    l = l - (t * x**3 * y * (1 + 3 * t**2)) / (3 * N0**4 * c)

    # f = f0 + y / r0 - 0.5 * t * (x / r0) * (x / N0)
    # f = f - 1.5 * et2 * t * c**2 * (y / r0) * (y / N0)
    # f = f - (1 / 6.0) * (1 + 3 * t**2 + et2 * c**2 - 9 * et2 * s**2) * (y / r0) * (x / N0)**2

    # l = l0 + x / (N0 * c) + (t / c) * (x / N0) * (y / N0)
    # l = l + ((1 + 3 * t**2 + et2 * c**2) / (3 * c)) * (x / N0) * (y / N0)**2
    # l = l - (t**2 / (3 * c)) * (x / N0)**3

    print(degrees(f), degrees(l))

ast = 23.7163375
l = ast - 0.45
f = 40.45
print('start f,l:', f, l)
x, y, z = 1000, 1000, 0
hatt_xy_to_fl(x, y, z, f, l)


# 40.45900586576507 23.27812868144629

# all degrees
# 40.45900586576507 23.27812868144629