#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
from entities import MapPoint, Box
from grabber import grab_img

START_LL = MapPoint(40000.0, 3800000.0, 0.0)
START_UR = MapPoint(900000.0, 4620000.0, 0.0)

GRID_BOXES = (4, 3)


def limit_box(bllx, blly, burx, bury):
    """Return a box inside the WMS limits"""
    if bllx < START_LL.x: bllx = START_LL.x
    if blly < START_LL.y: blly = START_LL.y
    if burx > START_UR.x: burx = START_UR.x
    if bury > START_UR.y: bury = START_UR.y
    ll = MapPoint(bllx, blly, 0)
    ur = MapPoint(burx, bury, 0)
    return Box(ll, ur)

class Grid(object):
    def __init__(self, box):
        self.box = box
        self.divx, self.divy = GRID_BOXES
        self.worker_pool = []

        self.calc_boxes()

    def calc_boxes(self):
        sw = self.box.w / self.divx
        sh = self.box.h / self.divy
        inllx, inlly = self.box.ll.x, self.box.ll.y
        inurx, inury = inllx + sw, inlly + sh
        self.sboxes = [[dict() for i in range(self.divx)] for j in range(self.divy)]
        for i in range(self.divx):
            for j in range(self.divy):
                llx, lly = inllx + i * sw, inlly + j * sh
                urx, ury = inurx + i * sw, inury + j * sh
                # Making the image box 5% larger in every dir
                bllx, blly = llx - sw * 0.05, lly - sh * 0.05
                burx, bury = llx + sw * 1.05, lly + sh * 1.05
                self.sboxes[j][i]['box'] = limit_box(bllx, blly, burx, bury)


class MapCanvas(QtWidgets.QGraphicsScene):
    """Widget for displaying map
    Contains:
        llx, lly - Canvas lower left in meters
        vw, vg - Canvas width, height in pixels
        w, h - Canvas width, height in meters
        wfac, hfac - horizontal, vertical ratio of meters/pixels
    """
    img_loading = QtCore.pyqtSignal()
    img_loaded = QtCore.pyqtSignal()

    def __init__(self, *args):
        super(MapCanvas, self).__init__(*args)

        self.delay_timer = QtCore.QTimer(self)
        self.delay_timer.setSingleShot(True)
        self.delay_timer.timeout.connect(self.start_grabbing)

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
        if hasattr(self, 'pixmap'):
            self.update_scene_pixmap()
        self.delay_grabbing()

    def update_scene_pixmap(self):
        ulx, uly = self.trans_egsa_canvas(self.pixmap['ulx'], self.pixmap['uly'])
        a = self.addPixmap(self.pixmap['pixmap'])
        a.setScale(self.pixmap['wfac'] / self.wfac)
        a.setPos(ulx, uly)

    def delay_grabbing(self):
        if self.delay_timer.isActive():
            self.delay_timer.stop()
        self.delay_timer.start(100)

    def start_grabbing(self):
        if self.parent().frozen_map:
            return
        if hasattr(self, 'grid'):
            for worker in self.grid.worker_pool:
                worker.terminate()
        self.sboxes_displayed = 0
        self.img_loading.emit()

        # Making the image box 5% larger in every dir
        bllx, blly = self.llx - self.w * 0.05, self.lly - self.h * 0.05
        burx, bury = self.llx + self.w * 1.05, self.lly + self.h * 1.05
        box = limit_box(bllx, blly, burx, bury)

        self.grid = Grid(box)
        for row in self.grid.sboxes:
            for sb in row:
                sb['worker'] = ImgGrabberThread(
                    sb['box'],
                    int(round(sb['box'].w / self.wfac)),
                    int(round(sb['box'].h / self.hfac)))
                self.grid.worker_pool.append(sb['worker'])
                sb['worker'].img_fetched.connect(self.draw_image)
                sb['worker'].start()

    def draw_image(self, sbox):
        qi = QtGui.QImage.fromData(sbox['image'])
        pixmap = QtGui.QPixmap.fromImage(qi)

        img_poly = QtGui.QPolygonF()
        img_poly.append(QtCore.QPointF(0, 0))
        img_poly.append(QtCore.QPointF(qi.width(), 0))
        img_poly.append(QtCore.QPointF(qi.width(), qi.height()))
        img_poly.append(QtCore.QPointF(0, qi.height()))

        egsa_poly = QtGui.QPolygonF()
        llx, lly = sbox['box'].ll.x, sbox['box'].ll.y
        ulx, uly = sbox['box'].ul_egsa_through_wgs().x, sbox['box'].ul_egsa_through_wgs().y
        urx, ury = sbox['box'].ur.x, sbox['box'].ur.y
        lrx, lry = sbox['box'].lr_egsa_through_wgs().x, sbox['box'].lr_egsa_through_wgs().y
        iulx, iuly = 0, 0
        iurx, iury = (urx - ulx) / self.wfac, (uly - ury) / self.hfac
        ilrx, ilry = (lrx - ulx) / self.wfac, (uly - lry) / self.hfac
        illx, illy = (llx - ulx) / self.wfac, (uly - lly) / self.hfac
        egsa_poly.append(QtCore.QPointF(iulx, iuly))
        egsa_poly.append(QtCore.QPointF(iurx, iury))
        egsa_poly.append(QtCore.QPointF(ilrx, ilry))
        egsa_poly.append(QtCore.QPointF(illx, illy))

        trans = QtGui.QTransform()
        res = QtGui.QTransform.quadToQuad(img_poly, egsa_poly, trans)
        pixmap = pixmap.transformed(trans)
        sb = self.addPixmap(pixmap)
        ulx, uly = self.trans_egsa_canvas(llx, uly)
        sb.setPos(ulx, uly)

        # Saving a scene pixmap
        self.tmp_image = QtGui.QImage(self.vw, self.vh, QtGui.QImage.Format_RGB16)
        self.tmp_painter = QtGui.QPainter(self.tmp_image)
        self.tmp_painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.render(self.tmp_painter, QtCore.QRectF(0, 0, self.vw, self.vh), QtCore.QRectF(0, 0, self.vw, self.vh))
        self.pixmap = {
            'pixmap': QtGui.QPixmap.fromImage(self.tmp_image),
            'ulx': self.llx,
            'uly': self.lly + self.h,
            'wfac': self.wfac
        }
        del self.tmp_painter
        del self.tmp_image

        self.sboxes_displayed += 1
        if self.sboxes_displayed == GRID_BOXES[0] * GRID_BOXES[1]:
            self.sboxes_displayed = 0
            self.img_loaded.emit()


class ImgGrabberThread(QtCore.QThread):
    """Qt Thread for fetching the image"""
    img_fetched = QtCore.pyqtSignal(dict)

    def __init__(self, box, iw, ih):
        QtCore.QThread.__init__(self)
        self.box = box
        self.iw = iw
        self.ih = ih

    def __del__(self):
        self.wait()

    def run(self):
        img = grab_img(self.box, self.iw, self.ih)
        sbox = {
            'image': img,
            'box': self.box
        }
        self.img_fetched.emit(sbox)
        return
