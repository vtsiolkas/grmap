#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
from canvas_entities import PointItem
from entities import Point

from conversions.hatt import read_coefficients, find_regions
from math import *

PEN = QtGui.QPen()
BRUSH = QtCore.Qt.red
PEN.setBrush(BRUSH);
FONT = QtGui.QFont("SansSerif", 12)

class ObjectCanvas(QtWidgets.QGraphicsScene):
    """Widget for displaying map
    Contains:
        llx, lly - Canvas lower left in meters
        vw, vg - Canvas width, height in pixels
        w, h - Canvas width, height in meters
        wfac, hfac - horizontal, vertical ratio of meters/pixels
    """
    def __init__(self, *args):
        super(ObjectCanvas, self).__init__(*args)
        self.objects = []

    def trans_canvas_egsa(self, cx, cy):
        ex = self.llx + cx * self.wfac
        ey = self.lly + (self.vh - cy) * self.hfac
        return ex, ey

    def trans_egsa_canvas(self, ex, ey):
        cx = (ex - self.llx) / self.wfac
        cy = (self.h + self.lly - ey) / self.hfac
        return cx, cy

    def update_view(self, gcanvas):
        self.vw, self.vh = gcanvas['vw'], gcanvas['vh']
        self.llx, self.lly = gcanvas['llx'], gcanvas['lly']
        self.w, self.h = gcanvas['w'], gcanvas['h']
        self.wfac, self.hfac = gcanvas['wfac'], gcanvas['hfac']
        self.clear()
        self.redraw_canvas()

    def import_points(self, points):
    	for p in points:
    		self.objects.append({'type': 'point', 'data': p})
    	self.redraw_canvas()

    def add_point(self, x, y):
        p = Point(x, y, 0)
        self.objects.append({'type': 'point', 'data': {'point': p}})
        self.redraw_canvas()

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

        # regions = read_coefficients()
        # for reg in regions:
        #     p = Point(reg.a[0], reg.b[0], 0)
        #     self.objects.append({'type': 'point', 'data': {'point': p}})

    # def name_rect(self, ex, ey):
    #     for obj in self.objects:
    #         llx, lly = obj['rect']['llx'], obj['rect']['lly']
    #         lrx, lry = obj['rect']['lrx'], obj['rect']['lry']
    #         urx, ury = obj['rect']['urx'], obj['rect']['ury']
    #         ulx, uly = obj['rect']['ulx'], obj['rect']['uly']
    #         if llx < ex < urx and lly < ey < ury:
    #             rect = obj['rect']

    def redraw_canvas(self):
        for obj in self.objects:
            if obj['type'] == 'point':
                point = obj['data']['point']

                x, y = self.trans_egsa_canvas(point.x, point.y)
                p = PointItem(x, y)
                self.addItem(p)

                if 'name' in obj['data']:
                    name = obj['data']['name']
                    txt = self.addSimpleText(str(name))
                    txt.setBrush(BRUSH)
                    txt.setFont(FONT)
                    txt.setPos(x + 10, y - 10)
            if obj['type'] == 'grid_rect':
                llx, lly = self.trans_egsa_canvas(obj['rect']['llx'], obj['rect']['lly'])
                lrx, lry = self.trans_egsa_canvas(obj['rect']['lrx'], obj['rect']['lry'])
                urx, ury = self.trans_egsa_canvas(obj['rect']['urx'], obj['rect']['ury'])
                ulx, uly = self.trans_egsa_canvas(obj['rect']['ulx'], obj['rect']['uly'])
                # Don't draw invisibles, TODO, this hides some on the edges too
                # if all([i < 0 for i in [llx, lly, lrx, lry, ulx, uly, urx, ury]]):
                #     break
                ll = QtCore.QPointF(llx, lly)
                lr = QtCore.QPointF(lrx, lry)
                ur = QtCore.QPointF(urx, ury)
                ul = QtCore.QPointF(ulx, uly)
                rect = QtGui.QPolygonF()
                rect.append(ul)
                rect.append(ur)
                rect.append(lr)
                rect.append(ll)
                qpoly = self.addPolygon(rect, PEN)


# class HattDialog(QDialog):
#     hatt_dialog_closed = QtCore.pyqtSignal(object)
#     def __init__(self, *args):
#         super(HattDialog, self).__init__(*args)
#         self.region = None
#         self.initUI()

#     def initUI(self):
#         self.setWindowTitle('Επιλογή φύλλου χάρτη 1:50000')
#         self.setGeometry(10, 30, 400, 200)
#         grid = QGridLayout(self)

#         explain_label = QLabel(
#             'Εισάγετε το φ και λ του κέντρου φύλλου χάρτη 1:50000 και πιέστε Φιλτράρισμα για να \n' +
#             'περιοριστούν οι περιοχές στη λίστα, και επιλέξτε την περιοχή που θέλετε. \n' +
#             'Εναλλακτικά επιλέξτε κατευθείαν την περιοχή που θέλετε από τη λίστα.'
#             )

#         f_label = QLabel('φ:')
#         l_label = QLabel('λ:')
#         self.f_edit = QLineEdit()
#         self.l_edit = QLineEdit()

#         search_btn = QPushButton('Φιλτράρισμα')
#         search_btn.clicked.connect(self.limit_regions)
#         search_btn.setAutoDefault(False)

#         line1 = QFrame(self)
#         line1.setFrameShape(QFrame.HLine)
#         line1.setFrameShadow(QFrame.Sunken)

#         self.regions = read_coefficients()
#         from_combo_label = QLabel('Φύλλο χάρτη 1:50000:')
#         self.region_combo = QComboBox(self)
#         self.region_combo.setMinimumContentsLength(30)
#         self.region_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
#         region_names = ['%s - (%s, %s)' % (r.name, r.f, r.l) for r in self.regions]
#         self.region_combo.addItems(region_names)

#         grid.addWidget(explain_label, 0, 0, 1, 20)
#         grid.addWidget(f_label, 1, 0, 2, 1)
#         grid.addWidget(self.f_edit, 1, 1, 2, 4)
#         grid.addWidget(l_label, 1, 5, 2, 1)
#         grid.addWidget(self.l_edit, 1, 6, 2, 4)
#         grid.addWidget(search_btn, 1, 12, 2, 8)
#         grid.addWidget(line1, 3, 0, 1, 20)
#         grid.addWidget(from_combo_label, 4, 0, 4, 5)
#         grid.addWidget(self.region_combo, 4, 5, 4, 15)

#         self.ok_btn = QPushButton('OK')
#         self.ok_btn.clicked.connect(self.close_window)
#         self.ok_btn.setAutoDefault(True)
#         self.cancel_btn = QPushButton('Ακύρωση')
#         self.cancel_btn.clicked.connect(self.close_window)

#         grid.addWidget(self.ok_btn, 8, 0, 1, 10)
#         grid.addWidget(self.cancel_btn, 8, 10, 1, 10)

#     def closeEvent(self, event):
#         self.hatt_dialog_closed.emit(self.region)

#     def close_window(self):
#         if self.sender() == self.ok_btn:
#             self.region = self.regions[self.region_combo.currentIndex()]
#             self.close()
#         else:
#             self.region = None
#             self.close()

#     def limit_regions(self):
#         f = self.f_edit.text().replace(',', '.')
#         l = self.l_edit.text().replace(',', '.')
#         regions = find_regions(f, l)
#         if regions:
#             self.region_combo.clear()
#             self.regions = regions
#             region_names = ['%s - (%s, %s)' % (r.name, r.f, r.l) for r in self.regions]
#             self.region_combo.addItems(region_names)
#         else:
#             self.error('Πρόβλημα', 'Δεν βρέθηκε φύλλο χάρτη με αυτά τα φ, λ... Προσπαθήστε ξανά ή επιλέξτε κατευθείαν κάποιο από τη λίστα')

#     def error(self, title, text):
#         msg = QMessageBox(self)
#         msg.setWindowTitle(title)
#         msg.setText(text)
#         msg.open()
