#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from entities import Point, Point
from conversions.hatt import REGIONS
from conversions.conversions import *


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
        self.from_combo.addItems([
            "ΕΓΣΑ87",
            "WGS84",
            "HATT",
            "TM3 Δυτική Ζώνη",
            "TM3 Κεντρική Ζώνη",
            "TM3 Ανατολική Ζώνη"
        ])
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
        self.to_combo.addItems(["ΕΓΣΑ87"])

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
            hatt_dialog.hatt_dialog_closed.connect(self.get_hatt)
            hatt_dialog.exec_()
        else:
            self.from_hatt_label.setText('')

    def get_hatt(self, params):
        self.hatt = params['hatt']
        if not self.hatt:
            self.from_combo.setCurrentIndex(0)
        else:
            self.f = params['f']
            self.l = params['l']
            self.from_hatt_label.setText('(%s, %s)' % (self.f, self.l))

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
        txtpoints = []
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
            txtpoints.append(point)
        self.points = []
        for p in txtpoints:
            tmp = Point(p['x'], p['y'])
            if 'z' in p: tmp.z = p['z']
            if 'name' in p: tmp.name = p['name']
            self.points.append(tmp)
        source_system = self.from_combo.currentText()

    def convert(self):
        self.read_points()
        if not self.points:
            return
        self.text_output.setText('')
        source_system = self.from_combo.currentText()
        target_system = self.to_combo.currentText()
        if source_system == 'HATT':
            for p in self.points:
                p.region = hatt_egsa_fast(p.x, p.y, self.f, self.l)
                if p.region:
                    if self.hatt == 'BIG':
                        p.bhatt_egsa()
                    if self.hatt == 'SMALL':
                        p.shatt_bhatt(self.f, self.l)
                        p.bhatt_egsa()
                else:
                    self.error('Πρόβλημα', 'Το σημείο δεν αντιστοιχεί σε κάποιο φύλλο χάρτη 1:50000')
        elif source_system == 'WGS84':
            for p in self.points:
                p.wgs_egsa()
        elif source_system == "TM3 Δυτική Ζώνη":
            for p in self.points:
                p.region = tm3_egsa_fast(p.x, p.y, '-3')
                if p.region:
                    p.tm3_bhatt('-3')
                    p.bhatt_egsa()
                else:
                    self.error('Πρόβλημα', 'Το σημείο δεν αντιστοιχεί σε κάποιο φύλλο χάρτη 1:50000')
        elif source_system == "TM3 Κεντρική Ζώνη":
            for p in self.points:
                p.region = tm3_egsa_fast(p.x, p.y, '0')
                if p.region:
                    p.tm3_bhatt('0')
                    p.bhatt_egsa()
                else:
                    self.error('Πρόβλημα', 'Το σημείο δεν αντιστοιχεί σε κάποιο φύλλο χάρτη 1:50000')
        elif source_system == "TM3 Ανατολική Ζώνη":
            for p in self.points:
                p.region = tm3_egsa_fast(p.x, p.y, '3')
                if p.region:
                    p.tm3_bhatt('3')
                    p.bhatt_egsa()
                else:
                    self.error('Πρόβλημα', 'Το σημείο δεν αντιστοιχεί σε κάποιο φύλλο χάρτη 1:50000')
        if source_system == 'ΕΓΣΑ87':
            self.text_output.setText(self.text_input.toPlainText())
        else:
            line = ''
            if p.name:
                line += p.name + self.div
            line += str(p.x) + self.div
            line += str(p.y)
            if p.z:
                line += self.div + str(p.z)
            self.text_output.append(line)

    def import_to_canvas(self):
        self.convert()
        if self.points:
            self.importing_points.emit(self.points)
            self.close()


class HattDialog(QDialog):
    hatt_dialog_closed = QtCore.pyqtSignal(dict)
    def __init__(self, *args):
        super(HattDialog, self).__init__(*args)
        self.region = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Επιλογή φύλλου χάρτη')
        self.setGeometry(10, 30, 400, 200)
        grid = QGridLayout(self)

        explain_label = QLabel(
            'Εισάγετε το φ και λ του κέντρου φύλλου χάρτη. Η εφαρμογή ανιχνεύει αυτόματα \n' +
            'τα πάντα \n')

        f_label = QLabel('φ:')
        l_label = QLabel('λ:')
        self.f_edit = QLineEdit()
        self.l_edit = QLineEdit()

        grid.addWidget(explain_label, 0, 0, 1, 20)
        grid.addWidget(f_label, 1, 0, 2, 1)
        grid.addWidget(self.f_edit, 1, 1, 2, 4)
        grid.addWidget(l_label, 1, 5, 2, 1)
        grid.addWidget(self.l_edit, 1, 6, 2, 4)

        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.close_window)
        # self.ok_btn.setAutoDefault(True)
        self.cancel_btn = QPushButton('Ακύρωση')
        self.cancel_btn.clicked.connect(self.close_window)

        grid.addWidget(self.ok_btn, 8, 0, 1, 10)
        grid.addWidget(self.cancel_btn, 8, 10, 1, 10)

    def closeEvent(self, event):
        self.hatt_dialog_closed.emit(self.params)

    def close_window(self):
        self.hatt = None
        if self.sender() == self.ok_btn:
            self.check_params()
            if self.hatt:
                self.params = {
                    'hatt': self.hatt,
                    'f': self.f,
                    'l': self.l
                }
                self.close()
        else:
            self.params = {'hatt': self.hatt}
            self.close()

    def check_params(self):
        f = self.f_edit.text().strip().replace(',', '.')
        l = self.l_edit.text().strip().replace(',', '.')
        try:
            # Are they numbers?
            tmp = float(f)
            tmp = float(l)
        except:
            self.error('Πρόβλημα', "Δεν αναγνωρίζονται οι παράμετροι φ και λ. Εισάγετέ τους στη μορφή (φ = 39.45 και λ = -1.45) π.χ για το Φ.Χ 30' Τρικάλων που έχει 39°45', -1°45'\n" +
                                   "ή (φ = 39.09 και λ = 0.27) για (μικρό) Φ.Χ. 6' που έχει 39°09', 0°27'" )
            return
        f_split = f.split('.')
        l_split = l.split('.')
        if len(f_split) != 2 or len(l_split) != 2:
            self.error('Πρόβλημα', "Δεν αναγνωρίζονται οι παράμετροι φ και λ. Εισάγετέ τους στη μορφή (φ = 39.45 και λ = -1.45) π.χ για το Φ.Χ 30' Τρικάλων που έχει 39°45', -1°45'\n" +
                                   "ή (φ = 39.09 και λ = 0.27) για (μικρό) Φ.Χ. 6' που έχει 39°09', 0°27'" )
            return
        # First we look if f & l are .15 or .45 (big hatt)
        if f_split[1] in ['15', '45'] and l_split[1] in ['15', '45']:
            for region in REGIONS:
                if region.f == f and region.l == l:
                    self.hatt = 'BIG'
                    break
        # If not, we suppose it is a small(6') map f & l
        elif f_split[1] in ['3', '9', '03', '09', '15', '21', '27', '33', '39', '45', '51', '57'] and l_split[1] in ['3', '9', '03', '09', '15', '21', '27', '33', '39', '45', '51', '57']:
            if 34 <= int(f_split[0]) <= 41 and -4 <= int(l_split[0]) <= 4:
                self.hatt = 'SMALL'
        if self.hatt:
            self.f = f
            self.l = l
        else:
            self.error('Πρόβλημα', 'Δεν βρέθηκε φύλλο χάρτη με αυτά τα φ, λ... Προσπαθήστε ξανά...')

    def error(self, title, text):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.open()
