# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportEISOMSPage2.ui'
#
# Created: Thu Dec 26 18:03:24 2013
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_ExportEISOMSPage2(object):
    def setupUi(self, ExportEISOMSPage2):
        ExportEISOMSPage2.setObjectName(_fromUtf8("ExportEISOMSPage2"))
        ExportEISOMSPage2.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportEISOMSPage2)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblDir = QtGui.QLabel(ExportEISOMSPage2)
        self.lblDir.setObjectName(_fromUtf8("lblDir"))
        self.gridlayout.addWidget(self.lblDir, 0, 0, 1, 1)
        self.edtDir = QtGui.QLineEdit(ExportEISOMSPage2)
        self.edtDir.setObjectName(_fromUtf8("edtDir"))
        self.gridlayout.addWidget(self.edtDir, 0, 1, 1, 1)
        self.btnSelectDir = QtGui.QToolButton(ExportEISOMSPage2)
        self.btnSelectDir.setObjectName(_fromUtf8("btnSelectDir"))
        self.gridlayout.addWidget(self.btnSelectDir, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(128, 241, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(ExportEISOMSPage2)
        QtCore.QMetaObject.connectSlotsByName(ExportEISOMSPage2)

    def retranslateUi(self, ExportEISOMSPage2):
        ExportEISOMSPage2.setWindowTitle(_translate("ExportEISOMSPage2", "Form", None))
        self.lblDir.setText(_translate("ExportEISOMSPage2", "Сохранить в директорию", None))
        self.btnSelectDir.setText(_translate("ExportEISOMSPage2", "...", None))

