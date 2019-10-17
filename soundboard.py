#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Application de SoundBoard avec interface Qt
    ======================

    Exécuter pour commencer l'utilisation de la SoundBoard.


"""

import json
from PySide2.QtCore import (QRect, QSize)
from PySide2.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QGridLayout, QPushButton, QToolButton, QTableWidget,
    QSpacerItem, QSizePolicy)
from PySide2.QtGui import (QIcon, QPixmap)
import sys
import operator
from math import sqrt, ceil
import vlc

soundRep = "./sons/"
instance = vlc.Instance()
p = instance.media_player_new()


class SoundBoard(QDialog):
    def __init__(self):
        super(SoundBoard, self).__init__()
        self.title = '=== SoundBoard ==='
        self.left = 50
        self.top = 50
        # peu importe la hauteur et largeur la fenêtre s'adaptera au contenu
        self.width = 500
        self.height = 500
        self.currFileName = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.windowLayout = QHBoxLayout()
        self.tableWidget = QTableWidget()
        self.tableWidget.horizontalHeader().hide()
        self.tableWidget.verticalHeader().hide()
        self.initMenu()
        self.initButtons()
        self.windowLayout.setStretch(1, 0)
        self.setLayout(self.windowLayout)
        self.show()

    def initMenu(self):
        layout = QVBoxLayout()
        hlayout = QHBoxLayout()

        self.tbPlus = QToolButton()
        self.tbPlus.setGeometry(QRect(0, 0, 32, 32))
        iPlus = QIcon()
        iPlus.addPixmap(QPixmap(
            "./icons/plus.png"), QIcon.Normal, QIcon.Off)
        self.tbPlus.setIcon(iPlus)
        self.tbPlus.setObjectName("tbPlus")

        hlayout.addWidget(self.tbPlus)
        self.tbPlus.clicked.connect(self.refreshUI)

        self.tbMinus = QToolButton()
        self.tbMinus.setGeometry(QRect(0, 0, 32, 32))
        iMinus = QIcon()
        iMinus.addPixmap(QPixmap(
            "./icons/minus.png"), QIcon.Normal, QIcon.Off)
        self.tbMinus.setIcon(iMinus)
        self.tbMinus.setObjectName("tbMinus")

        hlayout.addWidget(self.tbMinus)
        self.tbMinus.clicked.connect(self.delete)

        self.tbEdit = QToolButton()
        self.tbEdit.setGeometry(QRect(0, 0, 32, 32))
        iEdit = QIcon()
        iEdit.addPixmap(QPixmap(
            "./icons/edit.png"), QIcon.Normal, QIcon.Off)
        self.tbEdit.setIcon(iEdit)
        self.tbEdit.setObjectName("tbEdit")

        hlayout.addWidget(self.tbEdit)
        self.tbEdit.clicked.connect(self.edit)

        layout.addLayout(hlayout)

        self.pbStop = QPushButton('GROS BOUTON STOP')
        self.pbStop.setMinimumSize(QSize(100, 100))
        self.pbStop.setGeometry(QRect(0, 0, 100, 100))
        layout.addWidget(self.pbStop)
        self.pbStop.clicked.connect(self.stop)

        spacerMenu = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacerMenu)

        self.windowLayout.addLayout(layout)

    def initButtons(self):
        self.tableWidget.clear()
        # import des informations boutons contenues dans le json
        with open('buttons.json', encoding='utf-8') as json_file:
            data_buttons = json.load(json_file)

        # stockage de la position la plus élevée pour le cadrage
        positions = [p['position'] for p in data_buttons['buttons']]
        max_pos = max(positions)

        # calcul du nombre de boutons par hauteur et largeur
        self.btnPWH = ceil(sqrt(max_pos))
        self.tableWidget.setColumnCount(self.btnPWH)
        self.tableWidget.setRowCount(self.btnPWH)
        self.tableWidget.setGeometry(QRect(0, 0, 400, 400))

        # positionnement des boutons en fonction des positions du json
        for ligne in range(self.btnPWH):
            for colonne in range(self.btnPWH):
                if (ligne*3)+(colonne+1) in positions:
                    for b in data_buttons['buttons']:
                        if b['position'] == (ligne*3)+(colonne+1):
                            pb = QPushButton(b['name'])
                            pb.setProperty('pbFile', b['file'])
                            self.tableWidget.setCellWidget(
                                ligne, colonne, pb)
                            pb.clicked.connect(self.play)
                else:
                    self.tableWidget.setCellWidget(
                        ligne, colonne, QPushButton('Nouveau'))
                colonne += 1
            ligne += 1

        buttonsLayout = QVBoxLayout()
        buttonsLayout.setStretch(0, 1)
        buttonsLayout.addWidget(self.tableWidget)

        self.windowLayout.addLayout(buttonsLayout)

        self.setGeometry(self.left, self.top, 140 +
                         self.btnPWH*100, 140+self.btnPWH*20)

    def play(self):
        pb = self.sender()
        pbFile = pb.property('pbFile')
        if (p.get_state() == vlc.State.Playing):
            p.stop()
            media = instance.media_new(soundRep + pbFile)
            if (self.currFileName != pbFile):
                p.set_media(media)
                p.play()
                self.currFileName = pbFile
        else:
            media = instance.media_new(soundRep + pbFile)
            p.set_media(media)
            p.play()
            self.currFileName = pbFile

    def stop(self):
        p.stop()

    def add(self):
        p.stop()

    def delete(self):
        p.stop()

    def edit(self):
        p.stop()

    def refreshUI(self):
        self.initButtons()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mwsb = SoundBoard()

    sys.exit(app.exec_())
