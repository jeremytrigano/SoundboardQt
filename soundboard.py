#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Application de SoundBoard avec interface Qt
    ======================
 
    Exécuter pour commencer l'utilisation de la SoundBoard.
 
 
"""

import json
from PySide2.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGroupBox, QGridLayout, QPushButton)
import sys
import operator
from math import sqrt, ceil

# import des informations boutons contenues dans le json
with open('buttons.json') as json_file:
    data_buttons = json.load(json_file)

# stockage de la position la plus élevée pour le cadrage
positions = [p['position'] for p in data_buttons['buttons']]
max_pos = max(positions)


class SoundBoard(QDialog):
    def __init__(self):
        super(SoundBoard, self).__init__()
        self.title = '=== SoundBoard ==='
        self.left = 50
        self.top = 50
        # calcul du nombre de boutons par hauteur et largeur
        self.btnPWH = ceil(sqrt(max_pos))
        # peu importe la hauteur et largeur la fenêtre s'adaptera au contenu
        self.width = 1
        self.height = 1
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createGridLayout()

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        self.show()

    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox("")
        layout = QGridLayout()

        # positionnement des boutons en fonction des positions du json
        for ligne in range(self.btnPWH):
            for colonne in range(self.btnPWH):
                if (ligne*3)+(colonne+1) in positions:
                    for b in data_buttons['buttons']:
                        if b['position'] == (ligne*3)+(colonne+1):
                            layout.addWidget(QPushButton(
                                b['name']), ligne, colonne)
                else:
                    layout.addWidget(QPushButton('Nouveau'), ligne, colonne)
                colonne += 1
            ligne += 1

        self.horizontalGroupBox.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mwsb = SoundBoard()

    sys.exit(app.exec_())
