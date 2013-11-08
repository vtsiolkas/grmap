#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets

RADIUS = 5.0
PEN = QtGui.QPen()
PEN.setBrush(QtCore.Qt.red);

class PointItem(QtWidgets.QGraphicsItem):
    """Widget for displaying point
    Contains:
        x, y - Canvas center
        size - Circle size in pixels
        # TODO color - Point color
    """
    def __init__(self, x, y):
        super(PointItem, self).__init__()
        self.setPos(x, y)

    def boundingRect(self):
        return QtCore.QRectF(-RADIUS, -RADIUS, 2 * RADIUS, 2 * RADIUS)

    def paint(self, painter, option, widget):
        painter.setPen(PEN)
        painter.drawEllipse(-RADIUS, -RADIUS, 2 * RADIUS, 2 * RADIUS)
        painter.drawLine(-RADIUS, -RADIUS, RADIUS, RADIUS)
        painter.drawLine(-RADIUS, RADIUS, RADIUS, -RADIUS)
