#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
from canvas_entities import PointItem
from entities import Point
from conversions.hatt import REGIONS

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
        self.redraw_canvas()

    def import_points(self, points):
    	for p in points:
    		self.objects.append({'type': 'point', 'data': p})
    	self.redraw_canvas()

    def add_point(self, x, y):
        p = Point(x, y, 0)
        self.objects.append({'type': 'point', 'data': p})
        self.redraw_canvas()

    def hatt_grid(self, pressed):
        if pressed:
            for region in REGIONS:
                rect = {
                    'name': region.name,
                    'llx': region.llx,
                    'lly': region.lly,
                    'ulx': region.ulx,
                    'uly': region.uly,
                    'urx': region.urx,
                    'ury': region.ury,
                    'lrx': region.lrx,
                    'lry': region.lry,
                }
                self.objects.append({'type': 'hatt_grid', 'data': rect})
        else:
            self.objects[:] = [obj for obj in self.objects if obj['type'] != 'hatt_grid']
        self.redraw_canvas()

    def redraw_canvas(self):
        self.clear()
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
            if obj['type'] == 'hatt_grid':
                rect = obj['data']
                llx, lly = self.trans_egsa_canvas(rect['llx'], rect['lly'])
                lrx, lry = self.trans_egsa_canvas(rect['lrx'], rect['lry'])
                urx, ury = self.trans_egsa_canvas(rect['urx'], rect['ury'])
                ulx, uly = self.trans_egsa_canvas(rect['ulx'], rect['uly'])
                # Don't draw invisibles, TODO, this hides some on the edges too
                # if all([i < 0 for i in [llx, lly, lrx, lry, ulx, uly, urx, ury]]):
                #     break
                ll = QtCore.QPointF(llx, lly)
                lr = QtCore.QPointF(lrx, lry)
                ur = QtCore.QPointF(urx, ury)
                ul = QtCore.QPointF(ulx, uly)
                qpoly = QtGui.QPolygonF()
                qpoly.append(ul)
                qpoly.append(ur)
                qpoly.append(lr)
                qpoly.append(ll)
                self.addPolygon(qpoly, PEN)
                txt = self.addSimpleText(rect['name'])
                txt.setBrush(BRUSH)
                txt.setFont(FONT)
                txtrect = txt.boundingRect()
                w = txtrect.size().width() / 2
                h = txtrect.size().height() / 2
                x = (lrx + llx) / 2 - w
                y = (uly + lly) / 2 - h
                txt.setPos(x, y)
                print(x,y)
