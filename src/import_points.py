#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import *
from entities import Point

LINETYPE = {0: {'display': 'Όνομα,Χ(φ),Υ(λ),Ζ',
                'form': 'name,x,y,z'},
            1: {'display': 'Όνομα,Χ(φ),Υ(λ)',
                'form': 'name,x,y'},
            2: {'display': 'Χ(φ),Υ(λ),Ζ',
                'form': 'x,y,z'},
            3: {'display': 'Χ(φ),Υ(λ)',
                'form': 'x,y'}}

class ImportPointsDialog(QDialog):    
    def __init__(self, *args):
        super(ImportPointsDialog, self).__init__(*args)     
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
        self.from_combo.addItems(["ΕΓΣΑ'87", "WGS84"])
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

        grid.addWidget(from_combo_label, 1, 0, 1, 2)
        grid.addWidget(self.from_combo, 1, 2, 1, 2)
        grid.addWidget(from_linetype_label, 2, 0, 1, 2)
        grid.addWidget(self.from_linetype_combo, 2, 2, 1, 4)

        self.text_input = QTextEdit(self)
        self.text_input.setLineWrapMode(QTextEdit.NoWrap)
        grid.addWidget(self.text_input, 3, 0, 5, 6)

        convert_btn = QPushButton('Μετατροπή', self)
        convert_btn.clicked.connect(self.convert)
        grid.addWidget(convert_btn, 7, 1, 1, 2)

        import_btn = QPushButton('Εισαγωγή στο σχέδιο', self)
        import_btn.clicked.connect(self.import_to_canvas)
        grid.addWidget(import_btn, 7, 3, 1, 2)

        to_combo_label = QLabel('Σύστημα αναφοράς σημείων:')
        self.to_combo = QComboBox(self)
        self.to_combo.addItems(["ΕΓΣΑ'87", "WGS84"])

        grid.addWidget(to_combo_label, 8, 0, 1, 2)
        grid.addWidget(self.to_combo, 8, 2, 1, 2)

        self.text_output = QTextEdit(self)
        self.text_output.setLineWrapMode(QTextEdit.NoWrap)
        grid.addWidget(self.text_output, 9, 0, 5, 6)

    def load_file(self):
        file_chooser = QFileDialog.getOpenFileName(self, 'Επιλογή αρχείου', '', "Όλα τα αρχεία (*.*)")
        filename = file_chooser[0]
        with open(filename,'r') as f:
            point_lines = f.readlines()
        for line in point_lines:
            self.text_input.append(line.rstrip())

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
        possible_divs = [':', ';', '-', ',', ' ']
        text = self.text_input.toPlainText()
        if text.strip() == '': return
        lines = [line.strip() for line in text.splitlines()]
        for char in possible_divs:
            if char in lines[0]:
                self.div = char
                break
        if not hasattr(self, 'div'):
            self.error('Πρόβλημα', 'Δεν βρέθηκε κάποιο κατάλληλο διαχωριστικό σε κάθε γραμμή...')
        linetype = LINETYPE[self.from_linetype_combo.currentIndex()]['form'].split(',')
        print(linetype)
        points = []
        for line in lines:
            items = line.split(self.div)
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
        print points
        # if self.from_combo.currentIndex() == 0:
        #     for p in points:
        #         if 'z' not in p:
        #             z = 0
        #         else:
        #             z = p['z']
        #         p['point'] = Point(p['x'], p['y'], z, 2100)


    def convert(self):
        self.read_points()

    def import_to_canvas(self):
        pass