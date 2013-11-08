#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
from canvas_entities import PointItem
# from entities import Point, Box


PEN = QtGui.QPen()
PEN.setBrush(QtCore.Qt.red);


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

    def redraw_canvas(self):
        for obj in self.objects:
            if obj['type'] == 'point':
                point = obj['data']['point']
                x, y = self.trans_egsa_canvas(point.x, point.y)
                p = PointItem(x, y)
                self.addItem(p)
