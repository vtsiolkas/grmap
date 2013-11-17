#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
# from PIL import Image
# from StringIO import StringIO
from entities import MapPoint, Box
import math

# ll = MapPoint(308000, 4380000, 'ΕΓΣΑ87')
# ur = MapPoint(309000, 4381000, 'ΕΓΣΑ87')

# llt = MapPoint(40000, 3800000, 'ΕΓΣΑ87')
# urt = MapPoint(900000, 4620000, 'ΕΓΣΑ87')

def grab_img(box, w, h):
    payload = {
        'VERSION': '1.1.0',
        'REQUEST': 'GetMap',
        'LAYERS': 'KTBASEMAP',
        'SRS': 'EPSG:4326',
        'BBOX': box.to_wgs(),
        'WIDTH': w,
        'HEIGHT': h,
        'FORMAT': 'image/jpg'
    }
    r = requests.get('http://gis.ktimanet.gr/wms/wmsopen/wmsserver.aspx', params=payload)
    # return raw image data
    return r.content


# UNUSED BUT CAN SAVE HIGHER QUALITY
# def export_tiff(box, w, h):
#     height = int(w * box.height / box.width)
#     if height <= h:
#         width = w
#     else:
#         height = h
#         width = int(h * box.width / box.height)
#     print 'Before request reached'
#     payload = {
#         'VERSION': '1.1.0',
#         'REQUEST': 'GetMap',
#         'LAYERS': 'KTBASEMAP',
#         'SRS': 'EPSG:4326',
#         'BBOX': box.to_wgs(),
#         'WIDTH': width,
#         'HEIGHT': height,
#         'FORMAT': 'image/png'
#     }
#     r = requests.get('http://gis.ktimanet.gr/wms/wmsopen/wmsserver.aspx', params=payload)

#     i = Image.open(StringIO(r.content))

#     print 'after request reached'
#     i.save('egsa.tiff')
#     angle = math.radians(box.egsa_rotation())
#     wfac = box.width / width
#     hfac = box.height / height
#     print wfac, hfac
#     fac = wfac
#     n1 = str(fac * math.cos(angle))
#     n2 = str(-(fac * math.sin(angle)))
#     n3 = str(-(fac * math.sin(angle)))
#     n4 = str(-(fac * math.cos(angle)))
#     print n1, n2, n3, n4
#     with open('egsa.tfw','w') as f:
#         f.write('%s\n' % n1)
#         f.write('%s\n' % n2)
#         f.write('%s\n' % n3)
#         f.write('%s\n' % n4)
#         f.write('%s\n' % str(box.ul.egsa()[0]))
#         f.write('%s' % str(box.ul.egsa()[1]))

#     return True
