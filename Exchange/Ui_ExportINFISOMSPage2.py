# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportINFISOMSPage2.ui'
#
# Created: Thu Dec 26 18:04:05 2013
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

class Ui_ExportINFISOMSPage2(object):
    def setupUi(self, ExportINFISOMSPage2):
        ExportINFISOMSPage2.setObjectName(_fromUtf8("ExportINFISOMSPage2"))
        ExportINFISOMSPage2.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportINFISOMSPage2)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblDir = QtGui.QLabel(ExportINFISOMSPage2)
        self.lblDir.setObjectName(_fromUtf8("lblDir"))
        self.gridlayout.addWidget(self.lblDir, 0, 0, 1, 1)
        self.edtDir = QtGui.QLineEdit(ExportINFISOMSPage2)
        self.edtDir.setObjectName(_fromUtf8("edtDir"))
        self.gridlayout.addWidget(self.edtDir, 0, 1, 1, 1)
        self.btnSelectDir = QtGui.QToolButton(ExportINFISOMSPage2)
        self.btnSelectDir.setObjectName(_fromUtf8("btnSelectDir"))
        self.gridlayout.addWidget(self.btnSelectDir, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(128, 241, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(ExportINFISOMSPage2)
        QtCore.QMetaObject.connectSlotsByName(ExportINFISOMSPage2)

    def retranslateUi(self, ExportINFISOMSPage2):
        ExportINFISOMSPage2.setWindowTitle(_translate("ExportINFISOMSPage2", "Form", None))
        self.lblDir.setText(_translate("ExportINFISOMSPage2", "Сохранить в директорию", None))
        self.btnSelectDir.setText(_translate("ExportINFISOMSPage2", "...", None))

