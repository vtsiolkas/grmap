#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from map_canvas import MapCanvas
from grid_canvas import GridCanvas
from import_points import ImportPointsDialog

WMS_ENABLED = False
# WMS_ENABLED = True


class Map(QWidget):    
    def __init__(self):
        super(Map, self).__init__()     
        self.initial = True
        self.frozen_map = False
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('GrMap')
        self.setGeometry(10, 30, 800, 700)
        self.grid = QGridLayout(self)

        # Toolbar ************************************
        btn_group = QButtonGroup(self)
        pan_btn = QPushButton('Pan', self)
        pan_btn.setCheckable(True)
        zoom_btn = QPushButton('Zoom', self)
        zoom_btn.setCheckable(True)
        btn_group.addButton(pan_btn)
        btn_group.addButton(zoom_btn)

        freeze_btn = QPushButton('Πάγωμα χάρτη', self)
        freeze_btn.setCheckable(True)
        freeze_btn.clicked.connect(self.freeze_map)

        correct_map_btn = QPushButton('Διόρθωση χάρτη', self)
        correct_map_btn.clicked.connect(self.correct_map)

        import_points_btn = QPushButton('Εισαγωγή σημείων', self)
        import_points_btn.clicked.connect(self.import_points)

        self.grid.addWidget(pan_btn, 0, 0, 1, 1)
        self.grid.addWidget(zoom_btn, 0, 1, 1, 1)
        self.grid.addWidget(freeze_btn, 0, 3, 1, 1)
        self.grid.addWidget(correct_map_btn, 0, 4, 1, 1)
        self.grid.addWidget(import_points_btn, 0, 5, 1, 1)

        # Views ************************************
        self.mapview = QGraphicsView(self)
        self.mapview.setStyleSheet("border: 0px; background: black")
        self.grid.addWidget(self.mapview, 1, 0, 10, 10)

        self.gcanvas = GridCanvas(self)
        self.view = QGraphicsView(self.gcanvas, self)
        self.view.setStyleSheet("border: 0px; background: transparent")
        self.view.setMouseTracking(True)
        self.view.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))        
        self.grid.addWidget(self.view, 1, 0, 10, 10)

        # Footer ************************************
        self.spinner = QtGui.QMovie('spinner.gif', QtCore.QByteArray(), self)
        self.spinner.setCacheMode(QtGui.QMovie.CacheAll)
        self.spinner.setSpeed(100)
        self.spinlbl = QLabel(self)
        self.spinlbl.setMovie(self.spinner)
        self.spinlbl.hide()
        
        self.lbl = QLabel(self)
        self.lbl.setText('0.000, 0.000')

        tiffbutton = QPushButton('Export tiff+tfw', self)
        tiffbutton.clicked.connect(self.export_tiff)

        self.grid.addWidget(self.spinlbl, 11, 0, 1, 2)
        self.grid.addWidget(self.lbl, 11, 2, 1, 4)
        self.grid.addWidget(tiffbutton, 11, 6, 1, 4)

        self.gcanvas.mouse_move.connect(self.refresh_coords)
        if WMS_ENABLED:
            self.map_canvas = MapCanvas(self)
            self.mapview.setScene(self.map_canvas)
            self.map_canvas.img_loading.connect(self.busy)
            self.map_canvas.img_loaded.connect(self.ready)
            self.gcanvas.grid_done.connect(self.map_canvas.update_view)        
        self.show()

    def freeze_map(self, pressed):
        # pressed is boolean
        self.frozen_map = pressed
        if not pressed:
            vw, vh = self.view.size().width(), self.view.size().height()
            self.gcanvas.redraw_canvas(vw, vh)

    def correct_map(self):
        pass

    def import_points(self):
        self.import_points_dialog = ImportPointsDialog(self)
        self.import_points_dialog.show()


    def resizeEvent(self, event):
        self.gcanvas.clear()
        vw, vh = self.view.size().width(), self.view.size().height()
        self.view.setSceneRect(QtCore.QRectF(0, 0, vw, vh))
        self.mapview.setSceneRect(QtCore.QRectF(0, 0, vw, vh))
        if self.initial:
            self.gcanvas.calc_initial(vw, vh)
            self.initial = False
        self.gcanvas.redraw_canvas(vw, vh)

    def refresh_coords(self, coords):
        self.lbl.setText(coords)

    def busy(self):
        self.spinlbl.show()
        self.spinner.start()

    def ready(self):
        self.spinner.stop()
        self.spinlbl.hide()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_C:
            # Copy point coords to clipboard
            coords = self.lbl.text()
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(coords)
            print('Coordinates copied to clipboard: ', coords)

    def export_tiff(self):
        self.map_canvas.pixmap['pixmap'].save('ktima.tiff')
        with open('ktima.tfw','w') as f:
            f.write('%s\n%s\n%s\n%s\n%s\n%s' % (
                str(self.map_canvas.wfac),
                '0',
                '0',
                str(-self.map_canvas.hfac),
                str(self.map_canvas.llx),
                str(self.map_canvas.lly + self.map_canvas.h)
            ))


class TiffExporterThread(QtCore.QThread):
    """Qt Thread for fetching the image"""
    def __init__(self, box, vw, vh):
        QtCore.QThread.__init__(self)
        self.box = box
        self.vw = vw
        self.vh = vh
        print('Worker inited', self.box, self.vw, self.vh)

    def __del__(self):
        self.wait()

    def run(self):
        ok = export_tiff(self.box, self.vw, self.vh)
        self.emit(QtCore.SIGNAL('tiff_saved'), ok)
        return

app = QApplication(sys.argv)
mapapp = Map()
sys.exit(app.exec_())