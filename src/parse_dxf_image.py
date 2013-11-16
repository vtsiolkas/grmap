#!/usr/bin/python
# -*- coding: utf-8 -*-
from conversions.hatt import read_coefficients, find_regions

def read_hatt(self):
    dd = dict.fromkeys(['90','10','20','11','21', '12', '22', '13', '23', '340'], 0.0)
    new_lines = dict()
    with open('../new_names.txt', 'r') as f:
        lines = f.readlines()
    for li in lines:
        l = li.strip()
        ref, name = l.split(':')
        new_lines[ref] = name[:-4]
        print(ref, name)
    output = open('../hatt_bboxes.txt', 'w')
    with open('../akr.dxf', 'r') as f:
    # with open('ktima.dxf', 'r') as f:
        print('opened_file!')
        s = f.__next__()
        while s.strip() != 'ENTITIES':
            s = f.__next__()
        # print('entered entities!')
        for line in f:
            l = line.strip()
            if l == 'ENDSEC':
                break
            if l == 'AcDbRasterImage':
                # print('entered image!')
                while l != '0':
                    if l in dd:
                        dd[l] = f.__next__().strip()
                    l = f.__next__().strip()
                ropts = {
                    'e': float(dd['10']),
                    'n': float(dd['20']),
                    'uvx': float(dd['11']),
                    'uvy': float(dd['21']),
                    'vvx': float(dd['12']),
                    'vvy': float(dd['22']),
                    'w': float(dd['13']),
                    'h': float(dd['23']),
                    'ref': dd['340']
                }
                llx, lly = ropts['e'], ropts['n']
                ulx, uly = llx + ropts['vvx'] * ropts['h'], lly + ropts['vvy'] * ropts['h']
                lrx, lry = llx + ropts['uvx'] * ropts['w'], lly + ropts['uvy'] * ropts['w']
                urx, ury = ulx + ropts['uvx'] * ropts['w'], uly + ropts['uvy'] * ropts['w']
                # ref = ropts['ref']
                # print(ref)
                name = new_lines[ropts['ref']]
                a = '%s:%.3f:%.3f:%.3f:%.3f:%.3f:%.3f:%.3f:%.3f' % (name, ulx, uly, urx, ury, lrx, lry, llx, lly)
                # a = ':'.join(map(str, [ulx, uly, urx, ury, lrx, lry, llx, lly, name]))
                output.write(a + '\n')
        output.close()
                # rect = {
                #     'llx': llx,
                #     'lly': lly,
                #     'lrx': lrx,
                #     'lry': lry,
                #     'ulx': ulx,
                #     'uly': uly,
                #     'urx': urx,
                #     'ury': ury,
                # }
                # self.objects.append({
                #     'type': 'grid_rect',
                #     'rect': rect
                # })
                # print('appended rect!', llx, lly, urx, ury, ulx, uly, lrx, lry)
