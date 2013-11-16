#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
from entities import Point

START_CLL = Point(0.0, 3800000.0, 0.0)
START_WIDTH = 920000.0
START_HEIGHT = 820000.0

# START_CLL = Point(0.0, 0.0, 0.0)
# START_WIDTH = 1000000.0
# START_HEIGHT = 5000000.0

ZOOM_FACTOR = 1.2

SELECTION_PEN = QtGui.QPen()
SELECTION_PEN.setWidth(2);
SELECTION_PEN.setStyle(QtCore.Qt.DashDotLine);
SELECTION_PEN.setBrush(QtCore.Qt.red);

GRID_PEN = QtGui.QPen()
GRID_PEN.setBrush(QtCore.Qt.darkGray);

class GridCanvas(QtWidgets.QGraphicsScene):
    """Widget for displaying map
    Contains:
        llx, lly - Canvas lower left in meters
        vw, vg - Canvas width, height in pixels
        w, h - Canvas width, height in meters
        wfac, hfac - horizontal, vertical ratio of meters/pixels
    """
    grid_done = QtCore.pyqtSignal(dict)
    mouse_move = QtCore.pyqtSignal(str)
    point = QtCore.pyqtSignal(float, float)
    def __init__(self, *args):
        super(GridCanvas, self).__init__(*args)
        self.llx, self.lly = START_CLL.x, START_CLL.y
        self.selecting = False
        self.panning = False

    def calc_initial(self, vw, vh):
        self.vw, self.vh = vw, vh
        view_aspect = float(vw) / vh
        start_aspect = START_WIDTH / START_HEIGHT
        if start_aspect <= view_aspect:
            self.h = START_HEIGHT
            self.w = self.h * view_aspect
        else:
            self.w = START_WIDTH
            self.h = self.w / view_aspect
        self.wfac = self.w / self.vw
        self.hfac = self.w / self.vw

    def trans_canvas_egsa(self, cx, cy):
        ex = self.llx + cx * self.wfac
        ey = self.lly + (self.vh - cy) * self.hfac
        return ex, ey

    def trans_egsa_canvas(self, ex, ey):
        cx = (ex - self.llx) / self.wfac
        cy = (self.h + self.lly - ey) / self.hfac
        return cx, cy

    def calculate_scene_egsa(self):
        view_aspect = float(self.vw) / self.vh
        self.w = self.h * view_aspect
        self.wfac = self.w / self.vw
        self.hfac = self.w / self.vw

    def redraw_canvas(self, vw, vh):
        self.clear()
        self.vw, self.vh = vw, vh
        self.calculate_scene_egsa()
        self.draw_grid()
        gcanvas = {
            'vw': self.vw,
            'vh': self.vh,
            'wfac': self.wfac,
            'hfac': self.hfac,
            'w': self.w,
            'h': self.h,
            'llx': self.llx,
            'lly': self.lly
        }
        self.grid_done.emit(gcanvas)

    def draw_hatt_grid(self):
        regions = read_coefficients()


    def draw_grid(self):
        txt_color = QtCore.Qt.magenta
        if self.w / self.h > 1:
            small = self.h
            large = self.w
        else:
            small = self.w
            large = self.h
        num_dig = len(str(int(small)))
        div = float(10 ** (num_dig - 1))
        while True:
            num_divisions = small / div
            if num_divisions < 4:
                div = div / 2
            elif num_divisions > 8:
                div = div * 2
            else:
                break
        llx = int(self.llx)
        vert = llx - (llx % div) + div
        lly = int(self.lly)
        horiz = lly - (lly % div) + div
        while vert <= self.llx + self.w:
            can_vert, y = self.trans_egsa_canvas(vert, 0)
            self.addLine(QtCore.QLineF(QtCore.QPointF(can_vert, 0), QtCore.QPointF(can_vert, self.vh)), GRID_PEN)
            if int(vert) == vert:
                coord_text = str(int(vert))
            else:
                coord_text = str(vert)
            txt = self.addSimpleText(str(coord_text))
            txt.setBrush(QtGui.QBrush(txt_color))
            txt.setPos(can_vert, self.vh - 2)
            txt.setRotation(270)
            vert += div
        while horiz <= self.lly + self.h:
            x, can_horiz = self.trans_egsa_canvas(0, horiz)
            self.addLine(QtCore.QLineF(QtCore.QPointF(0, can_horiz), QtCore.QPointF(self.vw, can_horiz)), GRID_PEN)
            if int(horiz) == horiz:
                coord_text = str(int(horiz))
            else:
                coord_text = str(horiz)
            txt = self.addSimpleText(str(coord_text))
            txt.setBrush(QtGui.QBrush(txt_color))
            txt.setPos(2, can_horiz)
            horiz += div

    def clear_selection(self):
        if self.selecting:
            self.selecting = False
            self.removeItem(self.serect)

    def zoom(self, pos, zf):
        mx = pos.x()
        my = pos.y()
        oldcx = self.vw / 2.0
        oldcy = self.vh / 2.0
        # dx, dy = (oldcx - mx) * (1 - zf), (oldcy - my) * (1 - zf)
        # A bit better at keeping the mouse coords steady
        dx, dy = (oldcx - mx) * (1 - zf) * abs(2 - zf), (oldcy - my) * (1 - zf) * abs(2 - zf)
        newcx = oldcx + dx
        newcy = oldcy + dy
        x, y = self.trans_canvas_egsa(newcx, newcy)
        self.w = self.w / zf
        aspect = float(self.vw) / self.vh
        self.h = self.w / aspect
        self.llx, self.lly = x - self.w / 2, y - self.h / 2
        self.redraw_canvas(self.vw, self.vh)

    def mouseMoveEvent(self, event):
        """Prints coords"""
        pos = event.scenePos()
        x, y = pos.x(), pos.y()
        ex, ey = self.trans_canvas_egsa(x, y)
        self.mouse_move.emit('%.3f, %.3f' % (ex, ey))
        if self.selecting:
            rect = self.area.update(x, y)
            self.serect.setRect(rect)
        if self.panning:
            dx, dy = x - self.pan.sx, y - self.pan.sy
            edx, edy = dx * self.wfac, dy * self.hfac
            self.llx, self.lly = self.llx - edx, self.lly + edy
            self.pan = PanStart(x, y)
            self.redraw_canvas(self.vw, self.vh)

    def mousePressEvent(self, event):
        pos = event.scenePos()
        x, y = pos.x(), pos.y()
        if event.button() == QtCore.Qt.MiddleButton:
            # Start panning
            self.panning = True
            self.pan = PanStart(x, y)
        if event.button() == QtCore.Qt.LeftButton:
            if self.parent().command == 'zoom':
                # Start selecting area
                self.selecting = True
                self.area = AreaSelect(x, y)
                self.serect = self.addRect(QtCore.QRectF(), SELECTION_PEN)
            if self.parent().command == 'point':
                ex, ey = self.trans_canvas_egsa(x, y)
                self.point.emit(ex, ey)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.selecting:
            # Stop selecting area
            rect = self.serect.rect()
            self.clear_selection()
            if rect.width() == 0 or rect.height() == 0:
                return
            cx = rect.x() + rect.width() / 2
            cy = rect.y() + rect.height() / 2
            x, y = self.trans_canvas_egsa(cx, cy)
            width = rect.width() * self.wfac
            height = rect.height() * self.hfac
            view_aspect = float(self.vw) / self.vh
            rect_aspect = width / height
            if rect_aspect <= view_aspect:
                self.h = height
                self.w = self.h * view_aspect
            else:
                self.w = width
                self.h = self.w / view_aspect
            self.llx, self.lly = x - self.w / 2, y - self.h / 2
            self.redraw_canvas(self.vw, self.vh)
        elif event.button() == QtCore.Qt.MiddleButton and self.panning:
            self.panning = False

    def wheelEvent(self, event):
        # Zoom
        self.clear_selection()
        direction = event.delta() / 120
        if direction > 0:
            # zoom in
            self.zoom(event.scenePos(), ZOOM_FACTOR)
        else:
            # zoom out
            self.zoom(event.scenePos(), 1.0 / ZOOM_FACTOR)


class PanStart(object):
    def __init__(self, x, y):
        self.sx = x
        self.sy = y


class AreaSelect(object):
    def __init__(self, x, y):
        self.sx = x
        self.sy = y

    def update(self, x, y):
        if x < self.sx:
            rx = self.sx
            lx = x
        else:
            lx = self.sx
            rx = x
        if y < self.sy:
            ly = self.sy
            uy = y
        else:
            uy = self.sy
            ly = y
        w = abs(rx - lx)
        h = abs(uy - ly)
        return QtCore.QRectF(lx, uy, w, h)

