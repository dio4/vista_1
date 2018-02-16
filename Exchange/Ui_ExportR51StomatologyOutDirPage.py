# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportR51StomatologyOutDirPage.ui'
#
# Created: Thu Dec 26 18:11:47 2013
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

class Ui_ExportR51StomatologyOutDirPage(object):
    def setupUi(self, ExportR51StomatologyOutDirPage):
        ExportR51StomatologyOutDirPage.setObjectName(_fromUtf8("ExportR51StomatologyOutDirPage"))
        ExportR51StomatologyOutDirPage.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportR51StomatologyOutDirPage)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblDir = QtGui.QLabel(ExportR51StomatologyOutDirPage)
        self.lblDir.setObjectName(_fromUtf8("lblDir"))
        self.gridlayout.addWidget(self.lblDir, 0, 0, 1, 1)
        self.edtDir = QtGui.QLineEdit(ExportR51StomatologyOutDirPage)
        self.edtDir.setObjectName(_fromUtf8("edtDir"))
        self.gridlayout.addWidget(self.edtDir, 0, 1, 1, 1)
        self.btnSelectDir = QtGui.QToolButton(ExportR51StomatologyOutDirPage)
        self.btnSelectDir.setObjectName(_fromUtf8("btnSelectDir"))
        self.gridlayout.addWidget(self.btnSelectDir, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(128, 241, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(ExportR51StomatologyOutDirPage)
        QtCore.QMetaObject.connectSlotsByName(ExportR51StomatologyOutDirPage)

    def retranslateUi(self, ExportR51StomatologyOutDirPage):
        ExportR51StomatologyOutDirPage.setWindowTitle(_translate("ExportR51StomatologyOutDirPage", "Form", None))
        self.lblDir.setText(_translate("ExportR51StomatologyOutDirPage", "Сохранить в директорию", None))
        self.btnSelectDir.setText(_translate("ExportR51StomatologyOutDirPage", "...", None))

