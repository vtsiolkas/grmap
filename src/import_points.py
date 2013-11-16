#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from entities import Point
from conversions.hatt import REGIONS


LINETYPE = {0: {'display': 'Όνομα,Χ(φ),Υ(λ),Ζ',
                'form': 'name,x,y,z'},
            1: {'display': 'Όνομα,Χ(φ),Υ(λ)',
                'form': 'name,x,y'},
            2: {'display': 'Χ(φ),Υ(λ),Ζ',
                'form': 'x,y,z'},
            3: {'display': 'Χ(φ),Υ(λ)',
                'form': 'x,y'}}


class ImportPointsDialog(QDialog):
    importing_points = QtCore.pyqtSignal(list)
    def __init__(self, *args):
        super(ImportPointsDialog, self).__init__(*args)
        self.region = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Εισαγωγή σημείων')
        self.setGeometry(10, 30, 400, 700)
        grid = QGridLayout(self)

        # Toolbar ************************************
        from_file_btn = QPushButton('Φόρτωση από αρχείο...', self)
        from_file_btn.clicked.connect(self.load_file)
        grid.addWidget(from_file_btn, 0, 0, 1, 2)

        from_combo_label = QLabel('Σύστημα αναφοράς σημείων:')
        self.from_combo = QComboBox(self)
        self.from_combo.addItems(["ΕΓΣΑ87", "WGS84", "HATT"])
        self.from_combo.currentIndexChanged[str].connect(self.from_changed)
        from_linetype_label = QLabel('Μορφή:')
        self.from_linetype_combo = QComboBox(self)
        self.from_linetype_combo.addItems([
            'Όνομα,Χ(φ),Υ(λ),Ζ',
            'Όνομα,Χ(φ),Υ(λ)',
            'Χ(φ),Υ(λ),Ζ',
            'Χ(φ),Υ(λ)',
            'Άλλη(γράψτε εδώ)'])
        self.from_linetype_combo.setEditable(True)
        self.from_linetype_combo.editTextChanged.connect(self.keep_from_linetype_combo)

        self.from_hatt_label = QLabel('')

        grid.addWidget(from_combo_label, 1, 0, 1, 2)
        grid.addWidget(self.from_combo, 1, 2, 1, 2)

        grid.addWidget(self.from_hatt_label, 1, 4, 1, 2)

        grid.addWidget(from_linetype_label, 2, 0, 1, 2)
        grid.addWidget(self.from_linetype_combo, 2, 2, 1, 4)

        self.text_input = QTextEdit(self)
        self.text_input.setLineWrapMode(QTextEdit.NoWrap)
        grid.addWidget(self.text_input, 3, 0, 4, 6)

        convert_btn = QPushButton('Μετατροπή', self)
        convert_btn.clicked.connect(self.convert)
        grid.addWidget(convert_btn, 7, 1, 1, 2)

        import_btn = QPushButton("Εισαγωγή στο σχέδιο ως ΕΓΣΑ87", self)
        import_btn.clicked.connect(self.import_to_canvas)
        grid.addWidget(import_btn, 7, 3, 1, 2)

        to_combo_label = QLabel('Σύστημα αναφοράς σημείων:')
        self.to_combo = QComboBox(self)
        self.to_combo.addItems(["ΕΓΣΑ87", "WGS84"])

        grid.addWidget(to_combo_label, 8, 0, 1, 2)
        grid.addWidget(self.to_combo, 8, 2, 1, 2)

        self.text_output = QTextEdit(self)
        self.text_output.setLineWrapMode(QTextEdit.NoWrap)
        grid.addWidget(self.text_output, 9, 0, 4, 6)

    def load_file(self):
        file_chooser = QFileDialog.getOpenFileName(self, 'Επιλογή αρχείου', '', "Όλα τα αρχεία (*.*)")
        filename = file_chooser[0]
        try:
            with open(filename,'r') as f:
                point_lines = f.readlines()
        except FileNotFoundError:
            self.error('Πρόβλημα', 'Το αρχείο δεν βρέθηκε...')
        self.text_input.setText('')
        self.text_output.setText('')
        for line in point_lines:
            self.text_input.append(line.rstrip())

    def from_changed(self, system):
        if system == 'HATT':
            hatt_dialog = HattDialog(self)
            hatt_dialog.hatt_dialog_closed.connect(self.get_hatt_region)
            hatt_dialog.exec_()
        else:
            self.from_hatt_label.setText('')

    def get_hatt_region(self, region):
        self.region = region
        if not self.region:
            self.from_combo.setCurrentIndex(0)
        else:
            self.from_hatt_label.setText('%s - (%s, %s)' % (region.name, region.f, region.l))

    def keep_from_linetype_combo(self, text):
        idx = self.from_linetype_combo.currentIndex()
        if idx in LINETYPE:
            self.from_linetype_combo.setEditText(LINETYPE[idx]['display'])

    def error(self, title, text):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.open()

    def read_points(self):
        possible_divs = [':', ';', ',', ' ']
        text = self.text_input.toPlainText()
        if text.strip() == '': return
        lines = [line.strip() for line in text.splitlines()]
        for char in possible_divs:
            if char in lines[0]:
                self.div = char
                break
        if not hasattr(self, 'div'):
            self.error('Πρόβλημα', 'Δεν βρέθηκε κάποιο κατάλληλο διαχωριστικό σε κάθε γραμμή...')
            return False
        linetype = LINETYPE[self.from_linetype_combo.currentIndex()]['form'].split(',')
        points = []
        for line in lines:
            items = [item.strip() for item in line.split(self.div)]
            if len(items) != len(linetype):
                self.error('Πρόβλημα', 'Λάθος μορφή, επιλέξτε την σωστή και προσπαθήστε ξανά...')
                return False
            point = dict()
            for idx, t in enumerate(linetype):
                item = items[idx]
                if t in ['x', 'y', 'z']:
                    try:
                        point[t] = float(item.replace(',', '.'))
                    except:
                        self.error('Πρόβλημα', 'Κάποιο από τα x, y, z δεν είναι αριθμός')
                else:
                    point[t] = item
            points.append(point)
        source_system = self.from_combo.currentText()
        for p in points:
            if 'z' not in p:
                z = 0
            else:
                z = p['z']
            p['point'] = Point(p['x'], p['y'], z, source_system, self.region)
        return points

    def convert(self):
        points = self.read_points()
        if not points:
            return
        self.text_output.setText('')
        source_system = self.from_combo.currentText()
        target_system = self.to_combo.currentText()
        if source_system == target_system:
            self.text_output.setText(self.text_input.toPlainText())
            return
        if target_system == 'ΕΓΣΑ87':
            for p in points:
                line = ''
                if 'name' in p:
                    line += p['name'] + self.div
                line += str(p['point'].x) + self.div
                line += str(p['point'].y)
                if 'z' in p:
                    line += self.div + str(p['point'].z)
                self.text_output.append(line)
        elif target_system == 'WGS84':
            for p in points:
                line = ''
                if 'name' in p:
                    line += p['name'] + self.div
                wgs_x, wgs_y, wgs_z = p['point'].to_wgs()
                line += str(wgs_x) + self.div
                line += str(wgs_y)
                if 'z' in p:
                    line += self.div + str(wgs_z)
                self.text_output.append(line)

    def import_to_canvas(self):
        points = self.read_points()
        if points:
            self.importing_points.emit(points)
            self.close()


class HattDialog(QDialog):
    hatt_dialog_closed = QtCore.pyqtSignal(object)
    def __init__(self, *args):
        super(HattDialog, self).__init__(*args)
        self.region = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Επιλογή φύλλου χάρτη 1:50000')
        self.setGeometry(10, 30, 400, 200)
        grid = QGridLayout(self)

        explain_label = QLabel(
            'Εισάγετε το φ και λ του κέντρου φύλλου χάρτη και πιέστε Αναζήτηση για να \n' +
            'περιοριστούν οι περιοχές στη λίστα, και επιλέξτε την περιοχή που θέλετε. \n' +
            'Εναλλακτικά επιλέξτε κατευθείαν την περιοχή που θέλετε από τη λίστα.'
            )

        f_label = QLabel('φ:')
        l_label = QLabel('λ:')
        self.f_edit = QLineEdit()
        self.l_edit = QLineEdit()

        search_btn = QPushButton('Αναζήτηση')
        search_btn.clicked.connect(self.limit_regions)
        search_btn.setAutoDefault(False)

        line1 = QFrame(self)
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

        self.regions = REGIONS
        from_combo_label = QLabel('Φύλλο χάρτη 1:50000:')
        self.region_combo = QComboBox(self)
        self.region_combo.setMinimumContentsLength(30)
        self.region_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        region_names = ['%s - (%s, %s)' % (r.name, r.f, r.l) for r in self.regions]
        self.region_combo.addItems(region_names)

        grid.addWidget(explain_label, 0, 0, 1, 20)
        grid.addWidget(f_label, 1, 0, 2, 1)
        grid.addWidget(self.f_edit, 1, 1, 2, 4)
        grid.addWidget(l_label, 1, 5, 2, 1)
        grid.addWidget(self.l_edit, 1, 6, 2, 4)
        grid.addWidget(search_btn, 1, 12, 2, 8)
        grid.addWidget(line1, 3, 0, 1, 20)
        grid.addWidget(from_combo_label, 4, 0, 4, 5)
        grid.addWidget(self.region_combo, 4, 5, 4, 15)

        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.close_window)
        self.ok_btn.setAutoDefault(True)
        self.cancel_btn = QPushButton('Ακύρωση')
        self.cancel_btn.clicked.connect(self.close_window)

        grid.addWidget(self.ok_btn, 8, 0, 1, 10)
        grid.addWidget(self.cancel_btn, 8, 10, 1, 10)

    def closeEvent(self, event):
        self.hatt_dialog_closed.emit(self.region)

    def close_window(self):
        if self.sender() == self.ok_btn:
            self.region = self.regions[self.region_combo.currentIndex()]
            self.close()
        else:
            self.region = None
            self.close()

    def limit_regions(self):
        f = self.f_edit.text().replace(',', '.')
        l = self.l_edit.text().replace(',', '.')
        result = []
        # Sanitizing input (heh)
        f_clean = f.strip().replace(',', '.')
        l_clean = l.strip().replace(',', '.')
        f_split = f_clean.split('.')
        l_split = l_clean.split('.')
        if len(f_split) != 2 or len(l_split) != 2:
            self.error('Πρόβλημα', "Δεν αναγνωρίζονται οι παράμετροι φ και λ. Εισάγετέ τους στη μορφή (φ = 39.45 και λ = -1.45) π.χ για το Φ.Χ 30' Τρικάλων που έχει 39°45', -1°45')" +
                                   " ή (φ = 39.09 και λ = 0.27) για (μικρό) Φ.Χ. 6' που έχει 39°09', 0°27'" )
            return
        # First we look if f & l are .15 or .45 (big hatt)
        if f_split[2] in ['15', '45'] and l_split[2] in ['15', '45']:
            for region in self.regions:
                if region.f == f and region.l == l:
                    result.append(region)
        # If none found, we suppose it is a small(6') map f & l
        elif f_split[2] in ['3', '9', '03', '09', '15', '21', '27', '33', '39', '45', '51', '57'] and l_split[2] in ['3', '9', '03', '09', '15', '21', '27', '33', '39', '45', '51', '57']:
            result = small_hatt_container(f_clean, l_clean)
        if result:
            self.region_combo.clear()
            self.regions = regions
            region_names = ['%s - (%s, %s)' % (r.name, r.f, r.l) for r in self.regions]
            self.region_combo.addItems(region_names)
        else:
            self.error('Πρόβλημα', 'Δεν βρέθηκε φύλλο χάρτη με αυτά τα φ, λ... Προσπαθήστε ξανά ή επιλέξτε κατευθείαν κάποιο από τη λίστα')

    def error(self, title, text):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.open()
