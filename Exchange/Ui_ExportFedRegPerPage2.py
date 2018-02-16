# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportFedRegPerPage2.ui'
#
# Created: Fri Apr 11 13:11:07 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_ExportFedRegPerPage2SetupDialog(object):
    def setupUi(self, ExportFedRegPerPage2SetupDialog):
        ExportFedRegPerPage2SetupDialog.setObjectName(_fromUtf8("ExportFedRegPerPage2SetupDialog"))
        ExportFedRegPerPage2SetupDialog.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportFedRegPerPage2SetupDialog)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblDir = QtGui.QLabel(ExportFedRegPerPage2SetupDialog)
        self.lblDir.setObjectName(_fromUtf8("lblDir"))
        self.gridlayout.addWidget(self.lblDir, 0, 0, 1, 1)
        self.edtDir = QtGui.QLineEdit(ExportFedRegPerPage2SetupDialog)
        self.edtDir.setObjectName(_fromUtf8("edtDir"))
        self.gridlayout.addWidget(self.edtDir, 0, 1, 1, 1)
        self.btnSelectDir = QtGui.QToolButton(ExportFedRegPerPage2SetupDialog)
        self.btnSelectDir.setObjectName(_fromUtf8("btnSelectDir"))
        self.gridlayout.addWidget(self.btnSelectDir, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(128, 241, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(ExportFedRegPerPage2SetupDialog)
        QtCore.QMetaObject.connectSlotsByName(ExportFedRegPerPage2SetupDialog)

    def retranslateUi(self, ExportFedRegPerPage2SetupDialog):
        ExportFedRegPerPage2SetupDialog.setWindowTitle(_translate("ExportFedRegPerPage2SetupDialog", "Form", None))
        self.lblDir.setText(_translate("ExportFedRegPerPage2SetupDialog", "Сохранить в директорию", None))
        self.btnSelectDir.setText(_translate("ExportFedRegPerPage2SetupDialog", "...", None))

