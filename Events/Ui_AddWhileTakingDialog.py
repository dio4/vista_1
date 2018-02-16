# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AddWhileTakingDialog.ui'
#
# Created: Thu Aug 07 20:42:20 2014
#      by: PyQt4 UI code generator 4.11
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

class Ui_AddWhileTakingDialog(object):
    def setupUi(self, AddWhileTakingDialog):
        AddWhileTakingDialog.setObjectName(_fromUtf8("AddWhileTakingDialog"))
        AddWhileTakingDialog.resize(251, 440)
        self.gridLayout = QtGui.QGridLayout(AddWhileTakingDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(AddWhileTakingDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tblTimeList = QtGui.QTableView(AddWhileTakingDialog)
        self.tblTimeList.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.tblTimeList.setObjectName(_fromUtf8("tblTimeList"))
        self.gridLayout.addWidget(self.tblTimeList, 0, 0, 1, 1)

        self.retranslateUi(AddWhileTakingDialog)
        QtCore.QMetaObject.connectSlotsByName(AddWhileTakingDialog)

    def retranslateUi(self, AddWhileTakingDialog):
        AddWhileTakingDialog.setWindowTitle(_translate("AddWhileTakingDialog", "Добавить время приёма", None))

