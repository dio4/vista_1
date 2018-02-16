# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UpdatesChecker.ui'
#
# Created by: PyQt4 UI code generator 4.12
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_UpdatesCheckerDialog(object):
    def setupUi(self, UpdatesCheckerDialog):
        UpdatesCheckerDialog.setObjectName(_fromUtf8("UpdatesCheckerDialog"))
        UpdatesCheckerDialog.resize(539, 321)
        self.verticalLayout = QtGui.QVBoxLayout(UpdatesCheckerDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.table = QtGui.QTableWidget(UpdatesCheckerDialog)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.table.setColumnCount(2)
        self.table.setObjectName(_fromUtf8("table"))
        self.table.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        self.table.horizontalHeader().setDefaultSectionSize(200)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.table)
        self.buttonBox = QtGui.QDialogButtonBox(UpdatesCheckerDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(UpdatesCheckerDialog)
        QtCore.QMetaObject.connectSlotsByName(UpdatesCheckerDialog)

    def retranslateUi(self, UpdatesCheckerDialog):
        UpdatesCheckerDialog.setWindowTitle(_translate("UpdatesCheckerDialog", "Список апдейтов", None))
        self.table.setSortingEnabled(True)
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("UpdatesCheckerDialog", "Номер апдейта", None))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("UpdatesCheckerDialog", "Состояние", None))

