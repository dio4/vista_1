# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EventRecipesDrugstore.ui'
#
# Created: Wed Feb  3 15:32:12 2016
#      by: PyQt4 UI code generator 4.11.1
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

class Ui_EventRecipesDrugstore(object):
    def setupUi(self, EventRecipesDrugstore):
        EventRecipesDrugstore.setObjectName(_fromUtf8("EventRecipesDrugstore"))
        EventRecipesDrugstore.resize(594, 378)
        self.gridLayout = QtGui.QGridLayout(EventRecipesDrugstore)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblItems = CInDocTableView(EventRecipesDrugstore)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 1, 0, 1, 2)
        self.btnSync = QtGui.QPushButton(EventRecipesDrugstore)
        self.btnSync.setObjectName(_fromUtf8("btnSync"))
        self.gridLayout.addWidget(self.btnSync, 3, 0, 1, 1)
        self.btnClose = QtGui.QPushButton(EventRecipesDrugstore)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 3, 1, 1, 1)
        self.edtName = QtGui.QLineEdit(EventRecipesDrugstore)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 0, 0, 1, 1)
        self.btnSearch = QtGui.QPushButton(EventRecipesDrugstore)
        self.btnSearch.setObjectName(_fromUtf8("btnSearch"))
        self.gridLayout.addWidget(self.btnSearch, 0, 1, 1, 1)
        self.lblLastSync = QtGui.QLabel(EventRecipesDrugstore)
        self.lblLastSync.setObjectName(_fromUtf8("lblLastSync"))
        self.gridLayout.addWidget(self.lblLastSync, 2, 0, 1, 1)

        self.retranslateUi(EventRecipesDrugstore)
        QtCore.QMetaObject.connectSlotsByName(EventRecipesDrugstore)

    def retranslateUi(self, EventRecipesDrugstore):
        EventRecipesDrugstore.setWindowTitle(_translate("EventRecipesDrugstore", "Dialog", None))
        self.btnSync.setText(_translate("EventRecipesDrugstore", "Обновить информацию из аптек", None))
        self.btnClose.setText(_translate("EventRecipesDrugstore", "Закрыть", None))
        self.btnSearch.setText(_translate("EventRecipesDrugstore", "Поиск", None))
        self.lblLastSync.setText(_translate("EventRecipesDrugstore", "Дата и время последней синхронизации:", None))

from library.InDocTable import CInDocTableView
