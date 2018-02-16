# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RLSComboBoxTest.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_TestDialog(object):
    def setupUi(self, TestDialog):
        TestDialog.setObjectName(_fromUtf8("TestDialog"))
        TestDialog.resize(400, 82)
        self.gridlayout = QtGui.QGridLayout(TestDialog)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.comboBox = CRLSComboBox(TestDialog)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.gridlayout.addWidget(self.comboBox, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 131, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(TestDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(TestDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TestDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TestDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TestDialog)

    def retranslateUi(self, TestDialog):
        TestDialog.setWindowTitle(_translate("TestDialog", "Испытание РЛС", None))

from library.RLS.RLSComboBox import CRLSComboBox
