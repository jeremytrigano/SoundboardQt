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
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QGridLayout, QPushButton, QToolButton, QTableWidget, QLineEdit,
    QSpacerItem, QSizePolicy, QHeaderView)
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
        # positionnement de la fenêtre à l'ouverture
        self.left = 50
        self.top = 50
        # initialisation de la largeur et hauteur par défaut
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

        # bouton ajout
        self.tbPlus = QToolButton()
        self.tbPlus.setGeometry(QRect(0, 0, 32, 32))
        iPlus = QIcon()
        iPlus.addPixmap(QPixmap(
            "./icons/plus.png"), QIcon.Normal, QIcon.Off)
        self.tbPlus.setIcon(iPlus)
        self.tbPlus.setObjectName("tbPlus")

        hlayout.addWidget(self.tbPlus)
        self.tbPlus.clicked.connect(self.refreshUI)

        # bouton suppression
        self.tbMinus = QToolButton()
        self.tbMinus.setGeometry(QRect(0, 0, 32, 32))
        iMinus = QIcon()
        iMinus.addPixmap(QPixmap(
            "./icons/minus.png"), QIcon.Normal, QIcon.Off)
        self.tbMinus.setIcon(iMinus)
        self.tbMinus.setObjectName("tbMinus")

        hlayout.addWidget(self.tbMinus)
        self.tbMinus.clicked.connect(self.delete)

        # bouton édition
        self.tbEdit = QToolButton()
        self.tbEdit.setGeometry(QRect(0, 0, 32, 32))
        iEdit = QIcon()
        iEdit.addPixmap(QPixmap(
            "./icons/edit.png"), QIcon.Normal, QIcon.Off)
        self.tbEdit.setIcon(iEdit)
        self.tbEdit.setObjectName("tbEdit")

        hlayout.addWidget(self.tbEdit)
        self.tbEdit.clicked.connect(self.edit)

        # bouton paramètres
        self.tbParam = QToolButton()
        self.tbParam.setGeometry(QRect(0, 0, 32, 32))
        iParam = QIcon()
        iParam.addPixmap(QPixmap(
            "./icons/cog.png"), QIcon.Normal, QIcon.Off)
        self.tbParam.setIcon(iParam)
        self.tbParam.setObjectName("tbParam")

        hlayout.addWidget(self.tbParam)
        self.tbParam.clicked.connect(self.settings)

        layout.addLayout(hlayout)

        self.pbStop = QPushButton("Don't STOP\n\nthe\n\nSoundBoard")
        self.pbStop.setStyleSheet("font-weight: bold;")
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

        self.tableWidget.clearSpans()
        # import des informations boutons contenues dans le json
        with open('buttons.json', encoding='utf-8') as json_file:
            self.data_buttons = json.load(json_file)

        # stockage de la position la plus élevée pour le cadrage
        positions = [p['position'] for p in self.data_buttons['buttons']]
        self.max_pos = max(positions)

        # calcul du nombre de boutons par hauteur et largeur
        self.BtnH = self.data_buttons['buttons_grid']['height']
        self.BtnW = self.data_buttons['buttons_grid']['width']
        self.tableWidget.setColumnCount(self.BtnW)
        self.tableWidget.setRowCount(self.BtnH)

        # positionnement des boutons en fonction des positions du json
        for ligne in range(self.BtnH):
            for colonne in range(self.BtnW):
                if (ligne*self.BtnW)+(colonne+1) in positions:
                    for b in self.data_buttons['buttons']:
                        if b['position'] == (ligne*self.BtnW)+(colonne+1):
                            pb = QPushButton(b['name'])
                            pb.setProperty('pbFile', b['file'])
                            # si fond clair, font noire, si sombre, font blanche
                            if (b['r']*0.299 + b['g']*0.587 + b['b']*0.114) > 186:
                                pb.setStyleSheet(
                                    f"background-color: rgb({b['r']},{b['g']},{b['b']}); color: #000000;")
                            else:
                                pb.setStyleSheet(
                                    f"background-color: rgb({b['r']},{b['g']},{b['b']}); color: #ffffff;")
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

        self.setGeometry(self.left, self.top,
                         140 + self.BtnW*100,
                         175 if self.BtnH*31 < 175 else 25 + self.BtnH*30)

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

    def settings(self):
        self.tableWidget.clear()

        col = 2
        row = 3

        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(4)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        # bouton validation
        pb = QPushButton('Valider')
        self.tableWidget.setCellWidget(3, 0, pb)
        pb.clicked.connect(self.saveSettings)

        # bouton annulation
        pb = QPushButton('Annuler')
        self.tableWidget.setCellWidget(3, 1, pb)
        pb.clicked.connect(self.refreshUI)

        # parameters
        self.tableWidget.setSpan(0, 0, 1, 2)
        self.lAlert = QLabel("La modification de ces valeurs entrainera la "
                             "modification de position des boutons")
        self.lAlert.setStyleSheet("font-weight: bold;")
        self.tableWidget.setCellWidget(
            0, 0, self.lAlert)
        self.tableWidget.setCellWidget(
            1, 0, QLabel('Nombre de boutons en Hauteur'))
        self.leH = QLineEdit(str(self.data_buttons['buttons_grid']['height']))
        self.tableWidget.setCellWidget(
            1, 1, self.leH)
        self.tableWidget.setCellWidget(
            2, 0, QLabel('Nombre de boutons en Largeur'))
        self.leW = QLineEdit(str(self.data_buttons['buttons_grid']['width']))
        self.tableWidget.setCellWidget(
            2, 1, self.leW)

        settingsLayout = QVBoxLayout()
        settingsLayout.setStretch(0, 1)
        settingsLayout.addWidget(self.tableWidget)

        self.windowLayout.addLayout(settingsLayout)

        self.setGeometry(self.left, self.top, 600, 300)

    def saveSettings(self):
        h = int(self.leH.text())
        w = int(self.leW.text())
        if h*w < self.max_pos:
            self.lAlert.setText(
                f"Le bouton à la position {str(self.max_pos)} "
                f"est en dehors de la grille {h} x {w}")
            self.lAlert.setStyleSheet(
                "color: rgb(255,0,0); font-weight: bold;")
        else:
            self.data_buttons['buttons_grid']['height'] = int(self.leH.text())
            self.data_buttons['buttons_grid']['width'] = int(self.leW.text())
            with open('buttons.json', 'w', encoding='utf-8') as outfile:
                json.dump(self.data_buttons, outfile, indent=4)
            self.initButtons()

    def refreshUI(self):
        self.initButtons()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mwsb = SoundBoard()

    sys.exit(app.exec_())
