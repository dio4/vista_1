# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StoreItemDialog.ui'
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

class Ui_StoreItemDialog(object):
    def setupUi(self, StoreItemDialog):
        StoreItemDialog.setObjectName(_fromUtf8("StoreItemDialog"))
        StoreItemDialog.resize(640, 489)
        self.gridLayout_2 = QtGui.QGridLayout(StoreItemDialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblTradeName = QtGui.QLabel(StoreItemDialog)
        self.lblTradeName.setObjectName(_fromUtf8("lblTradeName"))
        self.gridLayout.addWidget(self.lblTradeName, 0, 0, 1, 1)
        self.edtTradeName = QtGui.QLineEdit(StoreItemDialog)
        self.edtTradeName.setObjectName(_fromUtf8("edtTradeName"))
        self.gridLayout.addWidget(self.edtTradeName, 0, 1, 1, 1)
        self.lblINN = QtGui.QLabel(StoreItemDialog)
        self.lblINN.setObjectName(_fromUtf8("lblINN"))
        self.gridLayout.addWidget(self.lblINN, 1, 0, 1, 1)
        self.edtINN = QtGui.QLineEdit(StoreItemDialog)
        self.edtINN.setObjectName(_fromUtf8("edtINN"))
        self.gridLayout.addWidget(self.edtINN, 1, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(StoreItemDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.tblShippingInfo = CItemListView(StoreItemDialog)
        self.tblShippingInfo.setObjectName(_fromUtf8("tblShippingInfo"))
        self.gridLayout_2.addWidget(self.tblShippingInfo, 1, 0, 1, 1)
        self.lblTradeName.setBuddy(self.edtTradeName)
        self.lblINN.setBuddy(self.edtINN)

        self.retranslateUi(StoreItemDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StoreItemDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StoreItemDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StoreItemDialog)
        StoreItemDialog.setTabOrder(self.edtTradeName, self.edtINN)
        StoreItemDialog.setTabOrder(self.edtINN, self.tblShippingInfo)
        StoreItemDialog.setTabOrder(self.tblShippingInfo, self.buttonBox)

    def retranslateUi(self, StoreItemDialog):
        StoreItemDialog.setWindowTitle(_translate("StoreItemDialog", "Dialog", None))
        self.lblTradeName.setText(_translate("StoreItemDialog", "Торговое наименование", None))
        self.lblINN.setText(_translate("StoreItemDialog", "МНН", None))

from library.ItemListView import CItemListView
