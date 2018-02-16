# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportTariffR23_Page1.ui'
#
# Created: Thu Feb 12 18:39:11 2015
#      by: PyQt4 UI code generator 4.11.2
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

class Ui_ExportTariffR23_Page1(object):
    def setupUi(self, ExportTariffR23_Page1):
        ExportTariffR23_Page1.setObjectName(_fromUtf8("ExportTariffR23_Page1"))
        ExportTariffR23_Page1.setWindowModality(QtCore.Qt.NonModal)
        ExportTariffR23_Page1.resize(522, 323)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ExportTariffR23_Page1.sizePolicy().hasHeightForWidth())
        ExportTariffR23_Page1.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(ExportTariffR23_Page1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(ExportTariffR23_Page1)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tblDates = CInDocTableView(self.splitter)
        self.tblDates.setTabKeyNavigation(False)
        self.tblDates.setAlternatingRowColors(True)
        self.tblDates.setObjectName(_fromUtf8("tblDates"))
        self.tblItems = CInDocTableView(self.splitter)
        self.tblItems.setTabKeyNavigation(False)
        self.tblItems.setAlternatingRowColors(True)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(229, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.btnSelectAll = QtGui.QPushButton(ExportTariffR23_Page1)
        self.btnSelectAll.setObjectName(_fromUtf8("btnSelectAll"))
        self.gridLayout.addWidget(self.btnSelectAll, 1, 1, 1, 1)
        self.btnClearSelection = QtGui.QPushButton(ExportTariffR23_Page1)
        self.btnClearSelection.setObjectName(_fromUtf8("btnClearSelection"))
        self.gridLayout.addWidget(self.btnClearSelection, 1, 2, 1, 1)

        self.retranslateUi(ExportTariffR23_Page1)
        QtCore.QMetaObject.connectSlotsByName(ExportTariffR23_Page1)
        ExportTariffR23_Page1.setTabOrder(self.btnSelectAll, self.btnClearSelection)

    def retranslateUi(self, ExportTariffR23_Page1):
        ExportTariffR23_Page1.setWindowTitle(_translate("ExportTariffR23_Page1", "Выбор экспортируемых тарифов", None))
        self.tblDates.setWhatsThis(_translate("ExportTariffR23_Page1", "список записей", "ура!"))
        self.tblItems.setWhatsThis(_translate("ExportTariffR23_Page1", "список записей", "ура!"))
        self.btnSelectAll.setText(_translate("ExportTariffR23_Page1", "Выбрать все", None))
        self.btnClearSelection.setText(_translate("ExportTariffR23_Page1", "Очистить", None))

from library.InDocTable import CInDocTableView
