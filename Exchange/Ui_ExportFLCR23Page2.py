# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportFLCR23Page2.ui'
#
# Created: Wed Nov 26 22:16:06 2014
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

class Ui_ExportFLCR23Page2(object):
    def setupUi(self, ExportFLCR23Page2):
        ExportFLCR23Page2.setObjectName(_fromUtf8("ExportFLCR23Page2"))
        ExportFLCR23Page2.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportFLCR23Page2)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblDir = QtGui.QLabel(ExportFLCR23Page2)
        self.lblDir.setObjectName(_fromUtf8("lblDir"))
        self.gridlayout.addWidget(self.lblDir, 0, 0, 1, 1)
        self.edtDir = QtGui.QLineEdit(ExportFLCR23Page2)
        self.edtDir.setObjectName(_fromUtf8("edtDir"))
        self.gridlayout.addWidget(self.edtDir, 0, 1, 1, 1)
        self.btnSelectDir = QtGui.QToolButton(ExportFLCR23Page2)
        self.btnSelectDir.setObjectName(_fromUtf8("btnSelectDir"))
        self.gridlayout.addWidget(self.btnSelectDir, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(128, 241, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(ExportFLCR23Page2)
        QtCore.QMetaObject.connectSlotsByName(ExportFLCR23Page2)

    def retranslateUi(self, ExportFLCR23Page2):
        ExportFLCR23Page2.setWindowTitle(_translate("ExportFLCR23Page2", "Form", None))
        self.lblDir.setText(_translate("ExportFLCR23Page2", "Сохранить в директорию", None))
        self.btnSelectDir.setText(_translate("ExportFLCR23Page2", "...", None))

