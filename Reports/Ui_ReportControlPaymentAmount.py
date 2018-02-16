# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportControlPaymentAmount.ui'
#
# Created: Wed Jun 03 19:13:18 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_ReportControlPaymentAmount(object):
    def setupUi(self, ReportControlPaymentAmount):
        ReportControlPaymentAmount.setObjectName(_fromUtf8("ReportControlPaymentAmount"))
        ReportControlPaymentAmount.resize(428, 318)
        self.verticalLayout = QtGui.QVBoxLayout(ReportControlPaymentAmount)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lblBegDate = QtGui.QLabel(ReportControlPaymentAmount)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lblBegDate)
        self.edtBegDate = CDateEdit(ReportControlPaymentAmount)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtBegDate)
        self.lblEndDate = QtGui.QLabel(ReportControlPaymentAmount)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.lblEndDate)
        self.edtEndDate = CDateEdit(ReportControlPaymentAmount)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.edtEndDate)
        self.label = QtGui.QLabel(ReportControlPaymentAmount)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label)
        self.cmbFinance = CRBComboBox(ReportControlPaymentAmount)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbFinance.sizePolicy().hasHeightForWidth())
        self.cmbFinance.setSizePolicy(sizePolicy)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.cmbFinance)
        self.label_2 = QtGui.QLabel(ReportControlPaymentAmount)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.SpanningRole, self.label_2)
        self.label_3 = QtGui.QLabel(ReportControlPaymentAmount)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_3)
        self.cmbContract = CContractComboBox(ReportControlPaymentAmount)
        self.cmbContract.setObjectName(_fromUtf8("cmbContract"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.cmbContract)
        self.verticalLayout.addLayout(self.formLayout)
        self.tblNumbers = CTableView(ReportControlPaymentAmount)
        self.tblNumbers.setObjectName(_fromUtf8("tblNumbers"))
        self.verticalLayout.addWidget(self.tblNumbers)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ReportControlPaymentAmount)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportControlPaymentAmount)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportControlPaymentAmount.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportControlPaymentAmount.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportControlPaymentAmount)

    def retranslateUi(self, ReportControlPaymentAmount):
        ReportControlPaymentAmount.setWindowTitle(_translate("ReportControlPaymentAmount", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportControlPaymentAmount", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportControlPaymentAmount", "Дата окончания периода", None))
        self.label.setText(_translate("ReportControlPaymentAmount", "Тип финансирования", None))
        self.label_2.setText(_translate("ReportControlPaymentAmount", "Реестры с расчетными датами", None))
        self.label_3.setText(_translate("ReportControlPaymentAmount", "Договор", None))

from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
from library.TableView import CTableView
from Accounting.ContractComboBox import CContractComboBox
