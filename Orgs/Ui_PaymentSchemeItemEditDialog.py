# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PaymentSchemeItemEditDialog.ui'
#
# Created: Thu Mar 05 15:32:15 2015
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_PaymentSchemeItemEditDialog(object):
    def setupUi(self, PaymentSchemeItemEditDialog):
        PaymentSchemeItemEditDialog.setObjectName(_fromUtf8("PaymentSchemeItemEditDialog"))
        PaymentSchemeItemEditDialog.resize(398, 244)
        self.gridLayout = QtGui.QGridLayout(PaymentSchemeItemEditDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblPaymentSchemeItems = CInDocTableView(PaymentSchemeItemEditDialog)
        self.tblPaymentSchemeItems.setObjectName(_fromUtf8("tblPaymentSchemeItems"))
        self.gridLayout.addWidget(self.tblPaymentSchemeItems, 0, 0, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.btnUp = QtGui.QPushButton(PaymentSchemeItemEditDialog)
        self.btnUp.setObjectName(_fromUtf8("btnUp"))
        self.verticalLayout.addWidget(self.btnUp)
        self.btnDown = QtGui.QPushButton(PaymentSchemeItemEditDialog)
        self.btnDown.setObjectName(_fromUtf8("btnDown"))
        self.verticalLayout.addWidget(self.btnDown)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PaymentSchemeItemEditDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)

        self.retranslateUi(PaymentSchemeItemEditDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PaymentSchemeItemEditDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PaymentSchemeItemEditDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PaymentSchemeItemEditDialog)

    def retranslateUi(self, PaymentSchemeItemEditDialog):
        PaymentSchemeItemEditDialog.setWindowTitle(_translate("PaymentSchemeItemEditDialog", "Dialog", None))
        self.btnUp.setText(_translate("PaymentSchemeItemEditDialog", "˄", None))
        self.btnDown.setText(_translate("PaymentSchemeItemEditDialog", "˅", None))

from library.InDocTable import CInDocTableView
