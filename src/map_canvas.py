#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
from entities import Point, Box
from grabber import grab_img

START_LL = Point(40000, 3800000, 2100)
START_UR = Point(900000, 4620000, 2100)

GRID_BOXES = (4, 3)


class Grid(object):
    def __init__(self, box):
        self.box = box
        self.llx, self.lly = box.ll.egsa()
        self.urx, self.ury = box.ur.egsa()
        self.w = box.width
        self.h = box.height
        self.divx, self.divy = GRID_BOXES
        self.worker_pool = []

        self.calc_boxes()

    def calc_boxes(self):
        sw = self.w / self.divx
        sh = self.h / self.divy
        inllx, inlly = self.box.ll.egsa()
        inurx, inury = inllx + sw, inlly + sh
        self.sboxes = [[dict() for i in range(self.divx)] for j in range(self.divy)]
        for i in range(self.divx):
            for j in range(self.divy):
                llx, lly = inllx + i * sw, inlly + j * sh
                urx, ury = inurx + i * sw, inury + j * sh
                # Making the image box 5% larger in every dir
                bllx, blly = llx - sw * 0.05, lly - sh * 0.05
                burx, bury = llx + sw * 1.05, lly + sh * 1.05
                # But staying inside the WMS limits
                if bllx < START_LL.egsa()[0]: bllx = START_LL.egsa()[0]
                if blly < START_LL.egsa()[1]: blly = START_LL.egsa()[1]
                if burx > START_UR.egsa()[0]: burx = START_UR.egsa()[0]
                if bury > START_UR.egsa()[1]: bury = START_UR.egsa()[1]
                ll = Point(bllx, blly, 2100)
                ur = Point(burx, bury, 2100)
                self.sboxes[j][i]['box'] = Box(ll, ur)


class MapCanvas(QtWidgets.QGraphicsScene):
    """Widget for displaying map
    Contains:
        box - WMS bounding box in WGS(call x, y = box.ll.egsa() for points)
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
        x = self.llx + cx * self.wfac
        y = self.lly + (self.vh - cy) * self.hfac
        return x, y

    def trans_egsa_canvas(self, ex, ey):
        x = (ex - self.llx) / self.wfac
        y = (self.h + self.lly - ey) / self.hfac
        return x, y

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
        # But staying inside the WMS limits
        if bllx < START_LL.egsa()[0]: bllx = START_LL.egsa()[0]
        if blly < START_LL.egsa()[1]: blly = START_LL.egsa()[1]
        if burx > START_UR.egsa()[0]: burx = START_UR.egsa()[0]
        if bury > START_UR.egsa()[1]: bury = START_UR.egsa()[1]
        bll = Point(bllx, blly, 2100)
        bur = Point(burx, bury, 2100)
        box = Box(bll, bur)

        self.grid = Grid(box)
        for row in self.grid.sboxes:
            for sb in row:                
                sb['worker'] = ImgGrabberThread(
                    sb['box'],
                    int(round(sb['box'].width / self.wfac)),
                    int(round(sb['box'].height / self.hfac)))
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
        llx, lly = sbox['box'].ll.egsa()
        ulx, uly = sbox['box'].ul.egsa()
        urx, ury = sbox['box'].ur.egsa()
        lrx, lry = sbox['box'].lr.egsa()
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
        # Calculating absolute(from not rotated egsa box) ulx, uly
        llx, lly = sbox['box'].ll.egsa()
        ulx, uly = sbox['box'].ul.egsa()
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
            'wfac': self.wfac,
        }
        del self.tmp_painter
        del self.tmp_image        

        self.sboxes_displayed += 1
        if self.sboxes_displayed == GRID_BOXES[0] * GRID_BOXES[1]:
            self.sboxes_displayed = 0
            self.img_loaded.emit()
            # self.clear()
            # self.update_scene_pixmap()


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
