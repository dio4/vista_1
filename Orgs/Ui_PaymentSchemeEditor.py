# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Orgs/PaymentSchemeEditor.ui'
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

class Ui_PaymentSchemeEditor(object):
    def setupUi(self, PaymentSchemeEditor):
        PaymentSchemeEditor.setObjectName(_fromUtf8("PaymentSchemeEditor"))
        PaymentSchemeEditor.resize(400, 383)
        self.gridLayout = QtGui.QGridLayout(PaymentSchemeEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(PaymentSchemeEditor)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 8, 0, 1, 2)
        self.edtPostAddress = QtGui.QLineEdit(PaymentSchemeEditor)
        self.edtPostAddress.setObjectName(_fromUtf8("edtPostAddress"))
        self.gridLayout.addWidget(self.edtPostAddress, 10, 2, 1, 1)
        self.edtContractName = QtGui.QLineEdit(PaymentSchemeEditor)
        self.edtContractName.setObjectName(_fromUtf8("edtContractName"))
        self.gridLayout.addWidget(self.edtContractName, 6, 2, 1, 1)
        self.lblContractName = QtGui.QLabel(PaymentSchemeEditor)
        self.lblContractName.setObjectName(_fromUtf8("lblContractName"))
        self.gridLayout.addWidget(self.lblContractName, 6, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PaymentSchemeEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 13, 0, 1, 3)
        self.edtSubjectContract = QtGui.QLineEdit(PaymentSchemeEditor)
        self.edtSubjectContract.setObjectName(_fromUtf8("edtSubjectContract"))
        self.gridLayout.addWidget(self.edtSubjectContract, 9, 2, 1, 1)
        self.lblSubjectContract = QtGui.QLabel(PaymentSchemeEditor)
        self.lblSubjectContract.setObjectName(_fromUtf8("lblSubjectContract"))
        self.gridLayout.addWidget(self.lblSubjectContract, 9, 0, 1, 1)
        self.lblStatus = QtGui.QLabel(PaymentSchemeEditor)
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.gridLayout.addWidget(self.lblStatus, 1, 0, 1, 2)
        self.edtDate = CDateEdit(PaymentSchemeEditor)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 7, 2, 1, 1)
        self.lblContractNumber = QtGui.QLabel(PaymentSchemeEditor)
        self.lblContractNumber.setObjectName(_fromUtf8("lblContractNumber"))
        self.gridLayout.addWidget(self.lblContractNumber, 5, 0, 1, 2)
        self.cmbPerson = CPersonComboBoxEx(PaymentSchemeEditor)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 4, 2, 1, 1)
        self.lblContractSum = QtGui.QLabel(PaymentSchemeEditor)
        self.lblContractSum.setObjectName(_fromUtf8("lblContractSum"))
        self.gridLayout.addWidget(self.lblContractSum, 11, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.cmbOrgId = COrgComboBox(PaymentSchemeEditor)
        self.cmbOrgId.setEnabled(True)
        self.cmbOrgId.setMinimumSize(QtCore.QSize(200, 25))
        self.cmbOrgId.setObjectName(_fromUtf8("cmbOrgId"))
        self.horizontalLayout.addWidget(self.cmbOrgId)
        self.btnSelectOrgName = QtGui.QToolButton(PaymentSchemeEditor)
        self.btnSelectOrgName.setEnabled(True)
        self.btnSelectOrgName.setObjectName(_fromUtf8("btnSelectOrgName"))
        self.horizontalLayout.addWidget(self.btnSelectOrgName)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 2, 1, 1)
        self.edtEndDate = CDateEdit(PaymentSchemeEditor)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 8, 2, 1, 1)
        self.cmbStatus = QtGui.QComboBox(PaymentSchemeEditor)
        self.cmbStatus.setMinimumSize(QtCore.QSize(234, 0))
        self.cmbStatus.setObjectName(_fromUtf8("cmbStatus"))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbStatus, 1, 2, 1, 1)
        self.lblDate = QtGui.QLabel(PaymentSchemeEditor)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 7, 0, 1, 2)
        self.edtContractNumber = QtGui.QLineEdit(PaymentSchemeEditor)
        self.edtContractNumber.setMinimumSize(QtCore.QSize(234, 0))
        self.edtContractNumber.setObjectName(_fromUtf8("edtContractNumber"))
        self.gridLayout.addWidget(self.edtContractNumber, 5, 2, 1, 1)
        self.edtContractSum = QtGui.QLineEdit(PaymentSchemeEditor)
        self.edtContractSum.setMinimumSize(QtCore.QSize(234, 0))
        self.edtContractSum.setObjectName(_fromUtf8("edtContractSum"))
        self.gridLayout.addWidget(self.edtContractSum, 11, 2, 1, 1)
        self.lblOrgName = QtGui.QLabel(PaymentSchemeEditor)
        self.lblOrgName.setObjectName(_fromUtf8("lblOrgName"))
        self.gridLayout.addWidget(self.lblOrgName, 3, 0, 1, 2)
        self.lblPerson = QtGui.QLabel(PaymentSchemeEditor)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 4, 0, 1, 2)
        self.lblPostAddress = QtGui.QLabel(PaymentSchemeEditor)
        self.lblPostAddress.setObjectName(_fromUtf8("lblPostAddress"))
        self.gridLayout.addWidget(self.lblPostAddress, 10, 0, 1, 1)
        self.chkEnrollment = QtGui.QCheckBox(PaymentSchemeEditor)
        self.chkEnrollment.setObjectName(_fromUtf8("chkEnrollment"))
        self.gridLayout.addWidget(self.chkEnrollment, 12, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(PaymentSchemeEditor)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(PaymentSchemeEditor)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 2, 1, 1)
        self.edtNumber = QtGui.QLineEdit(PaymentSchemeEditor)
        self.edtNumber.setObjectName(_fromUtf8("edtNumber"))
        self.gridLayout.addWidget(self.edtNumber, 0, 2, 1, 1)
        self.lblNumber = QtGui.QLabel(PaymentSchemeEditor)
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.gridLayout.addWidget(self.lblNumber, 0, 0, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblDate.setBuddy(self.edtDate)

        self.retranslateUi(PaymentSchemeEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PaymentSchemeEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PaymentSchemeEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(PaymentSchemeEditor)

    def retranslateUi(self, PaymentSchemeEditor):
        PaymentSchemeEditor.setWindowTitle(_translate("PaymentSchemeEditor", "Протокол", None))
        self.lblEndDate.setText(_translate("PaymentSchemeEditor", "Дата окончания договора", None))
        self.lblContractName.setText(_translate("PaymentSchemeEditor", "Наименование протокола", None))
        self.lblSubjectContract.setText(_translate("PaymentSchemeEditor", "Предмет договора", None))
        self.lblStatus.setText(_translate("PaymentSchemeEditor", "Статус учреждения", None))
        self.lblContractNumber.setText(_translate("PaymentSchemeEditor", "Номер протокола", None))
        self.lblContractSum.setText(_translate("PaymentSchemeEditor", "Сумма договора", None))
        self.btnSelectOrgName.setText(_translate("PaymentSchemeEditor", "...", None))
        self.cmbStatus.setItemText(0, _translate("PaymentSchemeEditor", "Страховая компания", None))
        self.cmbStatus.setItemText(1, _translate("PaymentSchemeEditor", "Медицинский центр", None))
        self.cmbStatus.setItemText(2, _translate("PaymentSchemeEditor", "Благотворительное общество", None))
        self.cmbStatus.setItemText(3, _translate("PaymentSchemeEditor", "Другая организация", None))
        self.lblDate.setText(_translate("PaymentSchemeEditor", "Дата заключения договора", None))
        self.lblOrgName.setText(_translate("PaymentSchemeEditor", "Наименование организации", None))
        self.lblPerson.setText(_translate("PaymentSchemeEditor", "Главный исследователь", None))
        self.lblPostAddress.setText(_translate("PaymentSchemeEditor", "Почтовый адрес", None))
        self.chkEnrollment.setText(_translate("PaymentSchemeEditor", "Набор закрыт", None))
        self.lblOrgStructure.setText(_translate("PaymentSchemeEditor", "Подразделение", None))
        self.lblNumber.setText(_translate("PaymentSchemeEditor", "Номер договора", None))

from OrgComboBox import COrgComboBox
from OrgStructComboBoxes import COrgStructureComboBox
from PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
