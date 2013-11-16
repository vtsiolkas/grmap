from math import *

def egsa2wgs(X, Y, z):
    # GRS80 ellipsoid
    a = 6378137.0
    b = 6356752.314140347
    e2 = (a**2 - b**2) / (a**2)
    es2 = (a**2 - b**2) / b**2
    m0 = 0.9996
    n = (a - b) / (a + b)

    B = (1 + n) / a / (1 + n**2 / 4 + n**4 / 64) * Y / m0
    b1 = 3 / 2 * n * (1 - 9 / 16 * n**2) * sin(2 * B)
    b2 = n**2 / 16 * (21 - 55 / 2 * n**2) * sin(4 * B)
    b3 = 151 / 96 * n**3 * sin(6 * B)
    b4 = 1097 / 512 * n**4 * sin(8 * B)
    Bf = B + b1 + b2 + b3 + b4
    ID = floor(X / 1000000)
    Vf = sqrt(1 + es2 * cos(Bf)**2)
    etaf = sqrt(es2 * cos(Bf)**2)
    y = X - 500000 - ID * 1000000
    ys = y * b / m0 / a**2
    l = atan(Vf / cos(Bf) * ( (exp(ys) - exp(-ys)) / 2 ) * (1 - etaf**2 * ys**2 / 6 - es2 * ys**4 / 10))
    lng = 24 * pi / 180 + l
    lat = atan(tan(Bf) * cos(Vf * l) * (1 - etaf**2 / 6 * l**4))

    N = a / sqrt(1 - e2 * (sin(lat)**2))
    X = (N + z) * cos(lat) * cos(lng)
    Y = (N + z) * cos(lat) * sin(lng)
    Z = (N * (1 - e2) + z) * sin(lat)

    # Old parameters(like coord_gr)
    # px = -199.723
    # py = 74.03
    # pz = 246.018
    # New parameters(like proj.4)
    px = -199.87
    py = 74.79
    pz = 246.62
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

    # WGS84 ellipsoid
    a = 6378137.0
    b = 6356752.31424518
    e2 = (a**2 - b**2) / (a**2)

    lng = atan2(Y1, X1)
    lat0 = atan2(Z1, sqrt(X1**2 + Y1**2))
    while abs(lat - lat0) > 0.0000000001:
        N = a / sqrt(1 - e2 * sin(lat0)**2)
        h = sqrt(X1**2 + Y1**2) / cos(lat0) - N
        lat = lat0
        lat0 = atan(Z1 / sqrt(X1**2 + Y1**2) * (1 / (1 - e2 * N / (N + h))))

    h = h - 0.001
    lat = lat * 180 / pi
    lng = lng * 180 / pi
    print(lat, lng)

egsa2wgs(360000,4600000, 0)