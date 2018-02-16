# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportR51OMSOutDirPage.ui'
#
# Created: Thu Dec 26 18:09:16 2013
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

class Ui_ExportR51OMSOutDirPage(object):
    def setupUi(self, ExportR51OMSOutDirPage):
        ExportR51OMSOutDirPage.setObjectName(_fromUtf8("ExportR51OMSOutDirPage"))
        ExportR51OMSOutDirPage.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportR51OMSOutDirPage)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblDir = QtGui.QLabel(ExportR51OMSOutDirPage)
        self.lblDir.setObjectName(_fromUtf8("lblDir"))
        self.gridlayout.addWidget(self.lblDir, 0, 0, 1, 1)
        self.edtDir = QtGui.QLineEdit(ExportR51OMSOutDirPage)
        self.edtDir.setObjectName(_fromUtf8("edtDir"))
        self.gridlayout.addWidget(self.edtDir, 0, 1, 1, 1)
        self.btnSelectDir = QtGui.QToolButton(ExportR51OMSOutDirPage)
        self.btnSelectDir.setObjectName(_fromUtf8("btnSelectDir"))
        self.gridlayout.addWidget(self.btnSelectDir, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(128, 241, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(ExportR51OMSOutDirPage)
        QtCore.QMetaObject.connectSlotsByName(ExportR51OMSOutDirPage)

    def retranslateUi(self, ExportR51OMSOutDirPage):
        ExportR51OMSOutDirPage.setWindowTitle(_translate("ExportR51OMSOutDirPage", "Form", None))
        self.lblDir.setText(_translate("ExportR51OMSOutDirPage", "Сохранить в директорию", None))
        self.btnSelectDir.setText(_translate("ExportR51OMSOutDirPage", "...", None))

