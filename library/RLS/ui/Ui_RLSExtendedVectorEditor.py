# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RLSExtendedVectorEditor.ui'
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

class Ui_RLSExtendedVectorEditor(object):
    def setupUi(self, RLSExtendedVectorEditor):
        RLSExtendedVectorEditor.setObjectName(_fromUtf8("RLSExtendedVectorEditor"))
        RLSExtendedVectorEditor.setWindowModality(QtCore.Qt.ApplicationModal)
        RLSExtendedVectorEditor.resize(400, 240)
        RLSExtendedVectorEditor.setMinimumSize(QtCore.QSize(400, 240))
        self.gridLayout = QtGui.QGridLayout(RLSExtendedVectorEditor)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblItems = CItemListView(RLSExtendedVectorEditor)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RLSExtendedVectorEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(RLSExtendedVectorEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RLSExtendedVectorEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RLSExtendedVectorEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(RLSExtendedVectorEditor)

    def retranslateUi(self, RLSExtendedVectorEditor):
        RLSExtendedVectorEditor.setWindowTitle(_translate("RLSExtendedVectorEditor", "Dialog", None))

from library.ItemListView import CItemListView
