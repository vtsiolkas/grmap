#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
from canvas_entities import PointItem
from entities import Point

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
        self.objects.append({'type': 'point', 'data': p})
        self.redraw_canvas()

    def hatt_grid(self):
        pass

    def redraw_canvas(self):
        for obj in self.objects:
            if obj['type'] == 'point':
                point = obj['data']
                x, y = self.trans_egsa_canvas(point.x, point.y)
                p = PointItem(x, y)
                self.addItem(p)
                if point.name:
                    txt = self.addSimpleText(str(point.name))
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
