from math import *

def wgs2egsa(lat, lng, z):
    lat, lng = radians(lat), radians(lng)

    # WGS84 ellipsoid
    a = 6378137.0
    b = 6356752.31424518
    e2 = (a**2 - b**2) / a**2
    N = a / sqrt(1 - e2 * sin(lat)**2)

    X = (N + z) * cos(lat) * cos(lng)
    Y = (N + z) * cos(lat) * sin(lng)
    Z = (N * (1 - e2) + z) * sin(lat)

    # Old parameters(like coord_gr)
    # px = 199.723
    # py = -74.03
    # pz = -246.018
    # New parameters(like proj.4)
    px = 199.87
    py = -74.79
    pz = -246.62
    rw = 0
    rf = 0
    rk = 0
    ks = 1

    c1 = cos(rw)
    c2 = cos(rf)
    c3 = cos(rk)
    s1 = sin(rw)
    s2 = sin(rf)
    s3 = sin(rk)
    D11 = c2 * c3
    D21 = -c2 * s3
    D31 = sin(rf)
    D12 = s1 * s2 * c3 + c1 * s3
    D22 = -s1 * s2 * s3 + c1 * c3
    D32 = -s1 * c2
    D13 = -c1 * s2 * c3 + s1 * s3
    D23 = c1 * s2 * s3 + s1 * c3
    D33 = c1 * c2
    X1 = px + ks * (D11 * X + D12 * Y + D13 * Z)
    Y1 = py + ks * (D21 * X + D22 * Y + D23 * Z)
    Z1 = pz + ks * (D31 * X + D32 * Y + D33 * Z)

    # GRS80 ellipsoid
    a = 6378137.0
    b = 6356752.314140347
    e2 = (a**2 - b**2) / (a**2)
    es2 = (a**2 - b**2) / b**2
    m0 = 0.9996
    n = (a - b) / (a + b)

    lng = atan2(Y1, X1)
    lat0 = atan2(Z1, sqrt(X1**2 + Y1**2))
    while abs(lat - lat0) > 0.0000000001:
        N = a / sqrt(1 - e2 * sin(lat0)**2)
        h = sqrt(X1**2 + Y1**2) / cos(lat0) - N
        lat = lat0
        lat0 = atan(Z1 / sqrt(X1**2 + Y1**2) * (1 / (1 - e2 * N / (N + h))))
    lng = lng - 24 * pi / 180
    V = sqrt(1 + es2 * cos(lat)**2)
    eta = sqrt(es2 * cos(lat)**2)
    Bf = atan(tan(lat) / cos(V * lng) * (1 + eta**2 / 6 * (1 - 3 * sin(lat)**2) * lng**4))
    Vf = sqrt(1 + es2 * cos(Bf)**2)
    etaf = sqrt(es2 * cos(Bf)**2)
    r1 = (1 + n**2 / 4 + n**4 / 64) * Bf
    r2 = 3 / 2 * n * (1 - n**2 / 8) * sin(2 * Bf)
    r3 = 15 / 16 * n**2 * (1 - n**2 / 4) * sin(4 * Bf)
    r4 = 35 / 48 * n**3 * sin(6 * Bf)
    r5 = 315 / 512 * n**4 * sin(8 * Bf)
    Northing = a / (1 + n) * (r1 - r2 + r3 - r4 + r5) * m0 - 0.001
    ys = tan(lng) * cos(Bf) / Vf * (1 + etaf**2 * lng**2 * cos(Bf)**2 * (etaf**2 / 6 + lng**2 / 10))
    ys = log(ys + sqrt(ys**2 + 1))
    Easting = m0 * a**2 / b * ys + 500000
    print(Easting, Northing)

wgs2egsa(43.34239470588118, 22.27463998909822, 0)