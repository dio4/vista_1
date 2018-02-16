# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SelectPaymentSchemeDialog.ui'
#
# Created: Tue Mar 03 13:45:17 2015
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

class Ui_SelectPaymentSchemeDialog(object):
    def setupUi(self, SelectPaymentSchemeDialog):
        SelectPaymentSchemeDialog.setObjectName(_fromUtf8("SelectPaymentSchemeDialog"))
        SelectPaymentSchemeDialog.resize(676, 71)
        self.formLayout = QtGui.QFormLayout(SelectPaymentSchemeDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lblPaymentScheme_2 = QtGui.QLabel(SelectPaymentSchemeDialog)
        self.lblPaymentScheme_2.setObjectName(_fromUtf8("lblPaymentScheme_2"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lblPaymentScheme_2)
        self.cmbPaymentScheme = CPaymentSchemeComboBox(SelectPaymentSchemeDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbPaymentScheme.sizePolicy().hasHeightForWidth())
        self.cmbPaymentScheme.setSizePolicy(sizePolicy)
        self.cmbPaymentScheme.setObjectName(_fromUtf8("cmbPaymentScheme"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.cmbPaymentScheme)
        self.buttonBox = QtGui.QDialogButtonBox(SelectPaymentSchemeDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(SelectPaymentSchemeDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SelectPaymentSchemeDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SelectPaymentSchemeDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SelectPaymentSchemeDialog)

    def retranslateUi(self, SelectPaymentSchemeDialog):
        SelectPaymentSchemeDialog.setWindowTitle(_translate("SelectPaymentSchemeDialog", "Выбор схемы оплаты", None))
        self.lblPaymentScheme_2.setText(_translate("SelectPaymentSchemeDialog", "Схема оплаты", None))

from library.PaymentSchemeComboBox import CPaymentSchemeComboBox
