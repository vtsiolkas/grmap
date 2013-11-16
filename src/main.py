#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from grid_canvas import GridCanvas
from object_canvas import ObjectCanvas
from map_canvas import MapCanvas
from import_points import ImportPointsDialog

WMS_ENABLED = False
WMS_ENABLED = True


class Map(QWidget):
    def __init__(self):
        super(Map, self).__init__()
        self.initial = True
        self.frozen_map = False
        self.points = []
        self.command = 'zoom'
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
        zoom_btn.setChecked(True)
        zoom_btn.clicked.connect(lambda: self.set_command('zoom'))
        point_btn = QPushButton('Σημείο', self)
        point_btn.setCheckable(True)
        point_btn.clicked.connect(lambda: self.set_command('point'))

        btn_group.addButton(pan_btn)
        btn_group.addButton(zoom_btn)
        btn_group.addButton(point_btn)

        freeze_btn = QPushButton('Πάγωμα χάρτη', self)
        freeze_btn.setCheckable(True)
        freeze_btn.clicked.connect(self.freeze_map)

        correct_map_btn = QPushButton('Διόρθωση χάρτη', self)
        correct_map_btn.clicked.connect(self.correct_map)

        import_points_btn = QPushButton('Εισαγωγή σημείων', self)
        import_points_btn.clicked.connect(self.show_import_points_dialog)

        self.grid.addWidget(pan_btn, 0, 0, 1, 1)
        self.grid.addWidget(zoom_btn, 0, 1, 1, 1)
        self.grid.addWidget(point_btn, 0, 2, 1, 1)
        self.grid.addWidget(freeze_btn, 0, 3, 1, 1)
        self.grid.addWidget(correct_map_btn, 0, 4, 1, 1)
        self.grid.addWidget(import_points_btn, 0, 5, 1, 1)

        # Views ************************************
        self.mapview = QGraphicsView(self)
        self.mapview.setStyleSheet("border: 0px; background: black")
        self.grid.addWidget(self.mapview, 1, 0, 10, 10)

        self.ocanvas = ObjectCanvas(self)
        self.oview = QGraphicsView(self.ocanvas, self)
        self.oview.setStyleSheet("border: 0px; background: transparent")
        self.grid.addWidget(self.oview, 1, 0, 10, 10)

        self.gcanvas = GridCanvas(self)
        self.view = QGraphicsView(self.gcanvas, self)
        self.view.setStyleSheet("border: 0px; background: transparent")
        self.view.setMouseTracking(True)
        self.view.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.grid.addWidget(self.view, 1, 0, 10, 10)

        # gcanvas signal connecting here
        self.gcanvas.grid_done.connect(self.ocanvas.update_view)
        self.gcanvas.mouse_move.connect(self.refresh_coords)
        self.gcanvas.point.connect(self.ocanvas.add_point)

        if WMS_ENABLED:
            self.map_canvas = MapCanvas(self)
            self.mapview.setScene(self.map_canvas)
            self.map_canvas.img_loading.connect(self.busy)
            self.map_canvas.img_loaded.connect(self.ready)
            self.gcanvas.grid_done.connect(self.map_canvas.update_view)

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

        hatt_grid_btn = QPushButton('Διανομή Κ.Φ.Χ 1:50000', self)
        hatt_grid_btn.clicked.connect(self.ocanvas.hatt_grid)
        self.grid.addWidget(hatt_grid_btn, 0, 6, 1, 1)

        self.show()

    def freeze_map(self, pressed):
        # pressed is boolean
        self.frozen_map = pressed
        if not pressed:
            vw, vh = self.view.size().width(), self.view.size().height()
            self.gcanvas.redraw_canvas(vw, vh)

    def correct_map(self):
        pass

    def set_command(self, command):
        self.command = command

    def show_import_points_dialog(self):
        import_points_dialog = ImportPointsDialog(self)
        import_points_dialog.show()
        import_points_dialog.importing_points.connect(self.ocanvas.import_points)

    def resizeEvent(self, event):
        self.gcanvas.clear()
        vw, vh = self.view.size().width(), self.view.size().height()
        self.view.setSceneRect(QtCore.QRectF(0, 0, vw, vh))
        self.oview.setSceneRect(QtCore.QRectF(0, 0, vw, vh))
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
            clipboard = QApplication.clipboard()
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
        idxf = open('sample.dxf', 'r')
        odxf = open('ktima.dxf', 'w')
        for line in idxf:
            buf = line
            if buf == '**GRMAP_EASTING**\n':
                buf = str(self.map_canvas.llx) + '\n'
            elif buf == '**GRMAP_NORTHING**\n':
                buf = str(self.map_canvas.lly) + '\n'
            elif buf == '**GRMAP_FAC**\n':
                buf = str(self.map_canvas.wfac) + '\n'
            elif buf == '**GRMAP_IMG_WIDTH**\n':
                buf = str(float(self.view.size().width())) + '\n'
            elif buf == '**GRMAP_IMG_HEIGHT**\n':
                buf = str(float(self.view.size().height())) + '\n'
            elif buf == '**GRMAP_IMG_WIDTH_HALF**\n':
                buf = str(float(self.view.size().width()) - 0.5) + '\n'
            elif buf == '**GRMAP_IMG_HEIGHT_HALF**\n':
                buf = str(float(self.view.size().height()) - 0.5) + '\n'
            elif buf == '**GRMAP_XREF_NAME**\n':
                buf = 'ktima' + '\n'
            elif buf == '**GRMAP_IMG_PATH**\n':
                buf = 'ktima.tiff' + '\n'
            elif buf == '**GRMAP_IMG_FAC**\n':
                buf = '0.5' + '\n'
            else:
                buf = line
            odxf.write(buf)
        idxf.close()
        odxf.close()


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
