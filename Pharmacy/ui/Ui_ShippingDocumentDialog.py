# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ShippingDocumentDialog.ui'
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

class Ui_ShippingDocumentDialog(object):
    def setupUi(self, ShippingDocumentDialog):
        ShippingDocumentDialog.setObjectName(_fromUtf8("ShippingDocumentDialog"))
        ShippingDocumentDialog.resize(645, 486)
        self.gridLayout_2 = QtGui.QGridLayout(ShippingDocumentDialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtNumber = QtGui.QLineEdit(ShippingDocumentDialog)
        self.edtNumber.setObjectName(_fromUtf8("edtNumber"))
        self.gridLayout.addWidget(self.edtNumber, 0, 1, 1, 1)
        self.lblInternalNumber = QtGui.QLabel(ShippingDocumentDialog)
        self.lblInternalNumber.setObjectName(_fromUtf8("lblInternalNumber"))
        self.gridLayout.addWidget(self.lblInternalNumber, 1, 0, 1, 1)
        self.edtInternalNumber = QtGui.QLineEdit(ShippingDocumentDialog)
        self.edtInternalNumber.setObjectName(_fromUtf8("edtInternalNumber"))
        self.gridLayout.addWidget(self.edtInternalNumber, 1, 1, 1, 1)
        self.lblExternalNumber = QtGui.QLabel(ShippingDocumentDialog)
        self.lblExternalNumber.setObjectName(_fromUtf8("lblExternalNumber"))
        self.gridLayout.addWidget(self.lblExternalNumber, 2, 0, 1, 1)
        self.edtInvoiceNumber = QtGui.QLineEdit(ShippingDocumentDialog)
        self.edtInvoiceNumber.setObjectName(_fromUtf8("edtInvoiceNumber"))
        self.gridLayout.addWidget(self.edtInvoiceNumber, 3, 1, 1, 1)
        self.lblDateTime = QtGui.QLabel(ShippingDocumentDialog)
        self.lblDateTime.setObjectName(_fromUtf8("lblDateTime"))
        self.gridLayout.addWidget(self.lblDateTime, 4, 0, 1, 1)
        self.edtExternalNumber = QtGui.QLineEdit(ShippingDocumentDialog)
        self.edtExternalNumber.setObjectName(_fromUtf8("edtExternalNumber"))
        self.gridLayout.addWidget(self.edtExternalNumber, 2, 1, 1, 1)
        self.lblInvoiceNumber = QtGui.QLabel(ShippingDocumentDialog)
        self.lblInvoiceNumber.setObjectName(_fromUtf8("lblInvoiceNumber"))
        self.gridLayout.addWidget(self.lblInvoiceNumber, 3, 0, 1, 1)
        self.lblNumber = QtGui.QLabel(ShippingDocumentDialog)
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.gridLayout.addWidget(self.lblNumber, 0, 0, 1, 1)
        self.edtDateTime = QtGui.QDateTimeEdit(ShippingDocumentDialog)
        self.edtDateTime.setCalendarPopup(True)
        self.edtDateTime.setObjectName(_fromUtf8("edtDateTime"))
        self.gridLayout.addWidget(self.edtDateTime, 4, 1, 1, 1)
        self.lblSupplier = QtGui.QLabel(ShippingDocumentDialog)
        self.lblSupplier.setObjectName(_fromUtf8("lblSupplier"))
        self.gridLayout.addWidget(self.lblSupplier, 0, 2, 1, 1)
        self.cmbUser = CUserComboBox(ShippingDocumentDialog)
        self.cmbUser.setObjectName(_fromUtf8("cmbUser"))
        self.gridLayout.addWidget(self.cmbUser, 5, 1, 1, 1)
        self.lblShipper = QtGui.QLabel(ShippingDocumentDialog)
        self.lblShipper.setObjectName(_fromUtf8("lblShipper"))
        self.gridLayout.addWidget(self.lblShipper, 1, 2, 1, 1)
        self.lblReason = QtGui.QLabel(ShippingDocumentDialog)
        self.lblReason.setObjectName(_fromUtf8("lblReason"))
        self.gridLayout.addWidget(self.lblReason, 2, 2, 1, 1)
        self.lblFinalizeUser = QtGui.QLabel(ShippingDocumentDialog)
        self.lblFinalizeUser.setObjectName(_fromUtf8("lblFinalizeUser"))
        self.gridLayout.addWidget(self.lblFinalizeUser, 5, 0, 1, 1)
        self.lblFundSource = QtGui.QLabel(ShippingDocumentDialog)
        self.lblFundSource.setObjectName(_fromUtf8("lblFundSource"))
        self.gridLayout.addWidget(self.lblFundSource, 3, 2, 1, 1)
        self.lblOrganisation = QtGui.QLabel(ShippingDocumentDialog)
        self.lblOrganisation.setObjectName(_fromUtf8("lblOrganisation"))
        self.gridLayout.addWidget(self.lblOrganisation, 4, 2, 1, 1)
        self.cmbSupplier = COrganisationComboBox(ShippingDocumentDialog)
        self.cmbSupplier.setObjectName(_fromUtf8("cmbSupplier"))
        self.gridLayout.addWidget(self.cmbSupplier, 0, 3, 1, 1)
        self.lblStore = QtGui.QLabel(ShippingDocumentDialog)
        self.lblStore.setObjectName(_fromUtf8("lblStore"))
        self.gridLayout.addWidget(self.lblStore, 5, 2, 1, 1)
        self.cmbShipper = COrganisationComboBox(ShippingDocumentDialog)
        self.cmbShipper.setObjectName(_fromUtf8("cmbShipper"))
        self.gridLayout.addWidget(self.cmbShipper, 1, 3, 1, 1)
        self.cmbFundSource = CRbItemComboBox(ShippingDocumentDialog)
        self.cmbFundSource.setObjectName(_fromUtf8("cmbFundSource"))
        self.gridLayout.addWidget(self.cmbFundSource, 3, 3, 1, 1)
        self.cmbOrganisation = COrganisationComboBox(ShippingDocumentDialog)
        self.cmbOrganisation.setObjectName(_fromUtf8("cmbOrganisation"))
        self.gridLayout.addWidget(self.cmbOrganisation, 4, 3, 1, 1)
        self.cmbStore = CStoreComboBox(ShippingDocumentDialog)
        self.cmbStore.setObjectName(_fromUtf8("cmbStore"))
        self.gridLayout.addWidget(self.cmbStore, 5, 3, 1, 1)
        self.edtReason = QtGui.QLineEdit(ShippingDocumentDialog)
        self.edtReason.setObjectName(_fromUtf8("edtReason"))
        self.gridLayout.addWidget(self.edtReason, 2, 3, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.tblItems = CItemListView(ShippingDocumentDialog)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout_2.addWidget(self.tblItems, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ShippingDocumentDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(ShippingDocumentDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ShippingDocumentDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ShippingDocumentDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ShippingDocumentDialog)
        ShippingDocumentDialog.setTabOrder(self.edtNumber, self.edtInternalNumber)
        ShippingDocumentDialog.setTabOrder(self.edtInternalNumber, self.edtExternalNumber)
        ShippingDocumentDialog.setTabOrder(self.edtExternalNumber, self.edtInvoiceNumber)
        ShippingDocumentDialog.setTabOrder(self.edtInvoiceNumber, self.edtDateTime)
        ShippingDocumentDialog.setTabOrder(self.edtDateTime, self.cmbUser)
        ShippingDocumentDialog.setTabOrder(self.cmbUser, self.cmbSupplier)
        ShippingDocumentDialog.setTabOrder(self.cmbSupplier, self.cmbShipper)
        ShippingDocumentDialog.setTabOrder(self.cmbShipper, self.edtReason)
        ShippingDocumentDialog.setTabOrder(self.edtReason, self.cmbFundSource)
        ShippingDocumentDialog.setTabOrder(self.cmbFundSource, self.cmbOrganisation)
        ShippingDocumentDialog.setTabOrder(self.cmbOrganisation, self.cmbStore)
        ShippingDocumentDialog.setTabOrder(self.cmbStore, self.tblItems)
        ShippingDocumentDialog.setTabOrder(self.tblItems, self.buttonBox)

    def retranslateUi(self, ShippingDocumentDialog):
        ShippingDocumentDialog.setWindowTitle(_translate("ShippingDocumentDialog", "Dialog", None))
        self.lblInternalNumber.setText(_translate("ShippingDocumentDialog", "Номер внутренней накладной", None))
        self.lblExternalNumber.setText(_translate("ShippingDocumentDialog", "Номер внешней накладной", None))
        self.lblDateTime.setText(_translate("ShippingDocumentDialog", "Дата-время приема на склад", None))
        self.lblInvoiceNumber.setText(_translate("ShippingDocumentDialog", "Номер счет-фактуры", None))
        self.lblNumber.setText(_translate("ShippingDocumentDialog", "Порядковый номер", None))
        self.edtDateTime.setDisplayFormat(_translate("ShippingDocumentDialog", "dd.MM.yyyy HH:mm", None))
        self.lblSupplier.setText(_translate("ShippingDocumentDialog", "Поставщик", None))
        self.lblShipper.setText(_translate("ShippingDocumentDialog", "Грузоотправитель", None))
        self.lblReason.setText(_translate("ShippingDocumentDialog", "Основание", None))
        self.lblFinalizeUser.setText(_translate("ShippingDocumentDialog", "Принявший сотрудник", None))
        self.lblFundSource.setText(_translate("ShippingDocumentDialog", "Источник финансирования", None))
        self.lblOrganisation.setText(_translate("ShippingDocumentDialog", "Организация", None))
        self.lblStore.setText(_translate("ShippingDocumentDialog", "Склад", None))

from Pharmacy.ItemListComboBox import COrganisationComboBox, CRbItemComboBox, CStoreComboBox, CUserComboBox
from library.ItemListView import CItemListView
