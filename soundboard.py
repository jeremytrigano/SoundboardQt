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
    QSpacerItem, QSizePolicy, QHeaderView, QTableWidgetItem, QFileDialog,
    QWidget, QColorDialog)
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
        self.initColorPicker()
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
        self.tbPlus.clicked.connect(self.add)

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
        self.tableWidget.setColumnWidth(2, 100)
        self.cdColorPicker.setVisible(False)

        self.tableWidget.horizontalHeader().hide()
        # import des informations boutons contenues dans le json
        with open('buttons.json', encoding='utf-8') as json_file:
            self.data_buttons = json.load(json_file)

        # stockage de la position la plus élevée pour le cadrage
        self.positions = [p['position'] for p in self.data_buttons['buttons']]
        self.max_pos = max(self.positions)

        # calcul du nombre de boutons par hauteur et largeur
        self.BtnH = self.data_buttons['buttons_grid']['height']
        self.BtnW = self.data_buttons['buttons_grid']['width']
        self.tableWidget.setColumnCount(self.BtnW)
        self.tableWidget.setRowCount(self.BtnH)

        # positionnement des boutons en fonction des positions du json
        for ligne in range(self.BtnH):
            for colonne in range(self.BtnW):
                if (ligne*self.BtnW)+(colonne+1) in self.positions:
                    for b in self.data_buttons['buttons']:
                        if b['position'] == (ligne*self.BtnW)+(colonne+1):
                            pb = QPushButton(b['name'][:9])
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

    def initColorPicker(self):
        self.lColorPicker = QVBoxLayout()
        self.cdColorPicker = QColorDialog()
        self.cdColorPicker.setOption(self.cdColorPicker.NoButtons, True)
        self.colorSelected = self.cdColorPicker.currentColor()

        self.lColorPicker.addWidget(self.cdColorPicker)
        self.cdColorPicker.setVisible(False)
        self.cdColorPicker.currentColorChanged.connect(self.colorChanged)

        self.windowLayout.addLayout(self.lColorPicker)

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
        self.cdColorPicker.setVisible(True)
        self.tableWidget.clear()
        self.tableWidget.clearSpans()
        self.tableWidget.setColumnWidth(2, 100)

        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(len(self.data_buttons['buttons'])+1)

        self.tableWidget.horizontalHeader().show()

        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem())
        self.tableWidget.horizontalHeaderItem(0).setText('Nom')
        self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem())
        self.tableWidget.horizontalHeaderItem(1).setText('Fichier')
        self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem())
        self.tableWidget.horizontalHeaderItem(2).setText('')
        self.tableWidget.setColumnWidth(2, 22)
        self.tableWidget.setHorizontalHeaderItem(3, QTableWidgetItem())
        self.tableWidget.horizontalHeaderItem(3).setText('Position')
        self.tableWidget.setHorizontalHeaderItem(4, QTableWidgetItem())
        self.tableWidget.horizontalHeaderItem(4).setText('Couleur')
        self.tableWidget.setHorizontalHeaderItem(5, QTableWidgetItem())
        self.tableWidget.horizontalHeaderItem(5).setText('')

        # nom
        self.leName = QLineEdit()
        self.leName.setPlaceholderText('Nom (10 max.)')
        self.tableWidget.setCellWidget(0, 0, self.leName)
        # fichier
        self.leFile = QLineEdit()
        self.leFile.setPlaceholderText('Fichier')
        self.tableWidget.setCellWidget(0, 1, self.leFile)
        # browse
        pbBrowser = QPushButton('...')
        pbBrowser.setMinimumSize(QSize(21, 21))
        pbBrowser.clicked.connect(self.browseMedia)
        self.tableWidget.setCellWidget(0, 2, pbBrowser)
        # position
        self.lePos = QLineEdit()
        self.lePos.setPlaceholderText('Position')
        self.tableWidget.setCellWidget(0, 3, self.lePos)
        # couleur
        self.leColor = QLineEdit()
        self.leColor.setPlaceholderText('255,255,255')
        self.leColor.setText(str(self.colorSelected.red())+","
                             + str(self.colorSelected.green())+","
                             + str(self.colorSelected.blue()))
        self.tableWidget.setCellWidget(0, 4, self.leColor)
        # validation
        pbValid = QPushButton('Valider')
        pbValid.clicked.connect(self.addValid)
        self.tableWidget.setCellWidget(0, 5, pbValid)

        def sortByPos(val):
            return val['position']

        self.data_buttons['buttons'].sort(key=sortByPos)
        for ligne, b in enumerate(self.data_buttons['buttons'], start=1):
            self.tableWidget.setSpan(ligne, 1, 1, 2)
            self.tableWidget.setCellWidget(ligne, 0, QLabel(b['name']))
            self.tableWidget.setCellWidget(ligne, 1, QLabel(b['file']))
            self.tableWidget.setCellWidget(
                ligne, 3, QLabel(str(b['position'])))
            self.tableWidget.setCellWidget(ligne, 4, QLabel('Couleur'))

        # 530 color picked width
        self.setGeometry(self.left, self.top, 690+530, 300)

    def addValid(self):
        gName = self.leName.text()
        self.leName.setStyleSheet("color: rgb(0,0,0);")
        gFile = self.leFile.text()
        self.leFile.setStyleSheet("color: rgb(0,0,0);")
        gPos = self.lePos.text()
        self.lePos.setStyleSheet("color: rgb(0,0,0);")
        gColor = self.leColor.text()
        self.leColor.setStyleSheet("color: rgb(0,0,0);")
        # si champs vides
        if ((gName == '' or gName == 'Obligatoire !')
            or (gFile == '' or gFile == 'Obligatoire !')
            or (gPos == '' or gColor == 'Obligatoire !')
                or (gColor == '' or gColor == 'Obligatoire !')):
            if gName == '' or gName == 'Obligatoire !':
                self.leName.setText('Obligatoire !')
                self.leName.setStyleSheet(
                    "color: rgb(255,0,0); font-weight: bold;")
            if gFile == '' or gFile == 'Obligatoire !':
                self.leFile.setText('Obligatoire !')
                self.leFile.setStyleSheet(
                    "color: rgb(255,0,0); font-weight: bold;")
            if gPos == '' or gColor == 'Obligatoire !':
                self.lePos.setText('Obligatoire !')
                self.lePos.setStyleSheet(
                    "color: rgb(255,0,0); font-weight: bold;")
            if gColor == '' or gColor == 'Obligatoire !':
                self.leColor.setText('Obligatoire !')
                self.leColor.setStyleSheet(
                    "color: rgb(255,0,0); font-weight: bold;")
        else:
            # vérif si champ position est un nombre
            try:
                flag = 0
                flag = int(gPos)
            except ValueError:
                self.lePos.setText(
                    f"{str(gPos)} n'est pas un nombre")
                self.lePos.setStyleSheet(
                    "color: rgb(255,0,0); font-weight: bold;")
            # si position est un nombre
            if flag != 0:
                # si position hors grille
                if int(gPos) < 0 or int(gPos) > self.data_buttons['buttons_grid']['height']*self.data_buttons['buttons_grid']['width']:
                    self.lePos.setText(
                        f"{str(gPos)} hors grille")
                    self.lePos.setStyleSheet(
                        "color: rgb(255,0,0); font-weight: bold;")
                else:
                    # si position déjà prise
                    if int(gPos) in self.positions:
                        self.lePos.setText(
                            f"{str(gPos)} déjà prise")
                        self.lePos.setStyleSheet(
                            "color: rgb(255,0,0); font-weight: bold;")
                    else:
                        dictToAppend = {
                            "name": gName,
                            "file": gFile,
                            "position": int(gPos),
                            "r": self.colorSelected.red(),
                            "g": self.colorSelected.green(),
                            "b": self.colorSelected.blue()
                        }
                        self.data_buttons['buttons'].append(dictToAppend)
                        with open('buttons.json', 'w', encoding='utf-8') as outfile:
                            json.dump(self.data_buttons, outfile, indent=4)
                        self.initButtons()

    def delete(self):
        self.initButtons()

    def edit(self):
        self.initButtons()

    def settings(self):
        self.tableWidget.clear()
        self.tableWidget.clearSpans()
        self.tableWidget.setColumnWidth(2, 100)

        self.cdColorPicker.setVisible(False)

        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(4)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.tableWidget.horizontalHeader().hide()

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

    def browseMedia(self):
        self.openFile = QFileDialog.getOpenFileName(
            self, "Sélectionner un média...", "./sons", "Image Files (*.avi *.mp3 *.wav)")
        filenameSplitted = self.openFile[0].split('/')
        self.leFile.setText(filenameSplitted[-1])

    def colorChanged(self):
        self.colorSelected = self.cdColorPicker.currentColor()
        self.leColor.setText(str(self.colorSelected.red())+","
                             + str(self.colorSelected.green())+","
                             + str(self.colorSelected.blue()))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mwsb = SoundBoard()

    sys.exit(app.exec_())
