# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Orgs/PaymentSchemeItemEditor.ui'
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

class Ui_PaymentSchemeItemEditor(object):
    def setupUi(self, PaymentSchemeItemEditor):
        PaymentSchemeItemEditor.setObjectName(_fromUtf8("PaymentSchemeItemEditor"))
        PaymentSchemeItemEditor.resize(400, 93)
        self.gridLayout = QtGui.QGridLayout(PaymentSchemeItemEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtName = QtGui.QLineEdit(PaymentSchemeItemEditor)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(PaymentSchemeItemEditor)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PaymentSchemeItemEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)
        self.lblType = QtGui.QLabel(PaymentSchemeItemEditor)
        self.lblType.setObjectName(_fromUtf8("lblType"))
        self.gridLayout.addWidget(self.lblType, 1, 0, 1, 1)
        self.cmbType = QtGui.QComboBox(PaymentSchemeItemEditor)
        self.cmbType.setObjectName(_fromUtf8("cmbType"))
        self.cmbType.addItem(_fromUtf8(""))
        self.cmbType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbType, 1, 1, 1, 1)

        self.retranslateUi(PaymentSchemeItemEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PaymentSchemeItemEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PaymentSchemeItemEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(PaymentSchemeItemEditor)

    def retranslateUi(self, PaymentSchemeItemEditor):
        PaymentSchemeItemEditor.setWindowTitle(_translate("PaymentSchemeItemEditor", "Этап протокола", None))
        self.lblName.setText(_translate("PaymentSchemeItemEditor", "Наименование этапа", None))
        self.lblType.setText(_translate("PaymentSchemeItemEditor", "Тип этапа", None))
        self.cmbType.setItemText(0, _translate("PaymentSchemeItemEditor", "обычный", None))
        self.cmbType.setItemText(1, _translate("PaymentSchemeItemEditor", "по показаниям", None))

