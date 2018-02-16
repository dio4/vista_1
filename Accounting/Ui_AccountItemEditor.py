# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AccountItemEditor.ui'
#
# Created: Thu Apr 16 00:54:49 2015
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(489, 159)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblService = QtGui.QLabel(Dialog)
        self.lblService.setObjectName(_fromUtf8("lblService"))
        self.gridLayout.addWidget(self.lblService, 1, 0, 1, 1)
        self.lblAmount = QtGui.QLabel(Dialog)
        self.lblAmount.setObjectName(_fromUtf8("lblAmount"))
        self.gridLayout.addWidget(self.lblAmount, 5, 1, 1, 1)
        self.lblSum = QtGui.QLabel(Dialog)
        self.lblSum.setObjectName(_fromUtf8("lblSum"))
        self.gridLayout.addWidget(self.lblSum, 5, 2, 1, 1)
        self.edtSum = QtGui.QDoubleSpinBox(Dialog)
        self.edtSum.setDecimals(3)
        self.edtSum.setMaximum(9999999.99)
        self.edtSum.setObjectName(_fromUtf8("edtSum"))
        self.gridLayout.addWidget(self.edtSum, 6, 2, 1, 1)
        self.edtAmount = QtGui.QDoubleSpinBox(Dialog)
        self.edtAmount.setMaximum(9999.99)
        self.edtAmount.setObjectName(_fromUtf8("edtAmount"))
        self.gridLayout.addWidget(self.edtAmount, 6, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 1, 1, 4)
        self.cmbService = CRBServiceComboBox(Dialog)
        self.cmbService.setObjectName(_fromUtf8("cmbService"))
        self.gridLayout.addWidget(self.cmbService, 1, 1, 1, 4)
        self.edtUET = QtGui.QDoubleSpinBox(Dialog)
        self.edtUET.setDecimals(3)
        self.edtUET.setMaximum(9999.99)
        self.edtUET.setObjectName(_fromUtf8("edtUET"))
        self.gridLayout.addWidget(self.edtUET, 6, 4, 1, 1)
        self.lblUET = QtGui.QLabel(Dialog)
        self.lblUET.setObjectName(_fromUtf8("lblUET"))
        self.gridLayout.addWidget(self.lblUET, 5, 4, 1, 1)
        self.cmbUnit = CRBComboBox(Dialog)
        self.cmbUnit.setObjectName(_fromUtf8("cmbUnit"))
        self.gridLayout.addWidget(self.cmbUnit, 6, 3, 1, 1)
        self.lblUnit = QtGui.QLabel(Dialog)
        self.lblUnit.setObjectName(_fromUtf8("lblUnit"))
        self.gridLayout.addWidget(self.lblUnit, 5, 3, 1, 1)
        self.lblPrice = QtGui.QLabel(Dialog)
        self.lblPrice.setObjectName(_fromUtf8("lblPrice"))
        self.gridLayout.addWidget(self.lblPrice, 5, 0, 1, 1)
        self.edtPrice = QtGui.QDoubleSpinBox(Dialog)
        self.edtPrice.setEnabled(True)
        self.edtPrice.setDecimals(3)
        self.edtPrice.setMaximum(9999999.99)
        self.edtPrice.setObjectName(_fromUtf8("edtPrice"))
        self.gridLayout.addWidget(self.edtPrice, 6, 0, 1, 1)
        self.lblServiceNameSource = QtGui.QLabel(Dialog)
        self.lblServiceNameSource.setText(_fromUtf8(""))
        self.lblServiceNameSource.setObjectName(_fromUtf8("lblServiceNameSource"))
        self.gridLayout.addWidget(self.lblServiceNameSource, 2, 0, 1, 1)
        self.lblServiceName = QtGui.QLabel(Dialog)
        self.lblServiceName.setText(_fromUtf8(""))
        self.lblServiceName.setObjectName(_fromUtf8("lblServiceName"))
        self.gridLayout.addWidget(self.lblServiceName, 2, 1, 1, 4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblAccount = QtGui.QLabel(Dialog)
        self.lblAccount.setObjectName(_fromUtf8("lblAccount"))
        self.horizontalLayout.addWidget(self.lblAccount)
        self.cmbAccount = QtGui.QComboBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbAccount.sizePolicy().hasHeightForWidth())
        self.cmbAccount.setSizePolicy(sizePolicy)
        self.cmbAccount.setObjectName(_fromUtf8("cmbAccount"))
        self.horizontalLayout.addWidget(self.cmbAccount)
        self.gridLayout.addLayout(self.horizontalLayout, 7, 0, 1, 5)
        self.lblService.setBuddy(self.cmbService)
        self.lblAmount.setBuddy(self.edtAmount)
        self.lblSum.setBuddy(self.edtSum)
        self.lblUET.setBuddy(self.edtUET)
        self.lblPrice.setBuddy(self.edtPrice)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.lblService.setText(_translate("Dialog", "Код услуги", None))
        self.lblAmount.setText(_translate("Dialog", "Количество", None))
        self.lblSum.setText(_translate("Dialog", "Сумма", None))
        self.lblUET.setText(_translate("Dialog", "УЕТ", None))
        self.lblUnit.setText(_translate("Dialog", "Единицы учета", None))
        self.lblPrice.setText(_translate("Dialog", "Цена по тарифу", None))
        self.lblAccount.setText(_translate("Dialog", "Переместить в счет", None))

from library.crbcombobox import CRBComboBox
from library.crbservicecombobox import CRBServiceComboBox
