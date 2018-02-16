# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'InventoryDocumentDialog.ui'
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

class Ui_InventoryDocumentDialog(object):
    def setupUi(self, InventoryDocumentDialog):
        InventoryDocumentDialog.setObjectName(_fromUtf8("InventoryDocumentDialog"))
        InventoryDocumentDialog.resize(800, 600)
        self.gridLayout_2 = QtGui.QGridLayout(InventoryDocumentDialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCatalog = QtGui.QLabel(InventoryDocumentDialog)
        self.lblCatalog.setObjectName(_fromUtf8("lblCatalog"))
        self.gridLayout.addWidget(self.lblCatalog, 2, 2, 1, 1)
        self.cmbUser = CUserComboBox(InventoryDocumentDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(60)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbUser.sizePolicy().hasHeightForWidth())
        self.cmbUser.setSizePolicy(sizePolicy)
        self.cmbUser.setObjectName(_fromUtf8("cmbUser"))
        self.gridLayout.addWidget(self.cmbUser, 0, 3, 1, 1)
        self.lblDate = QtGui.QLabel(InventoryDocumentDialog)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 1, 0, 1, 1)
        self.lblNumber = QtGui.QLabel(InventoryDocumentDialog)
        self.lblNumber.setWordWrap(True)
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.gridLayout.addWidget(self.lblNumber, 0, 0, 1, 1)
        self.cmbStore = CStoreComboBox(InventoryDocumentDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(60)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbStore.sizePolicy().hasHeightForWidth())
        self.cmbStore.setSizePolicy(sizePolicy)
        self.cmbStore.setObjectName(_fromUtf8("cmbStore"))
        self.gridLayout.addWidget(self.cmbStore, 1, 3, 1, 1)
        self.lblStore = QtGui.QLabel(InventoryDocumentDialog)
        self.lblStore.setObjectName(_fromUtf8("lblStore"))
        self.gridLayout.addWidget(self.lblStore, 1, 2, 1, 1)
        self.edtNumber = QtGui.QLineEdit(InventoryDocumentDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(40)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtNumber.sizePolicy().hasHeightForWidth())
        self.edtNumber.setSizePolicy(sizePolicy)
        self.edtNumber.setObjectName(_fromUtf8("edtNumber"))
        self.gridLayout.addWidget(self.edtNumber, 0, 1, 1, 1)
        self.cmbCatalog = CCatalogComboBox(InventoryDocumentDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(60)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbCatalog.sizePolicy().hasHeightForWidth())
        self.cmbCatalog.setSizePolicy(sizePolicy)
        self.cmbCatalog.setObjectName(_fromUtf8("cmbCatalog"))
        self.gridLayout.addWidget(self.cmbCatalog, 2, 3, 1, 1)
        self.lblUser = QtGui.QLabel(InventoryDocumentDialog)
        self.lblUser.setObjectName(_fromUtf8("lblUser"))
        self.gridLayout.addWidget(self.lblUser, 0, 2, 1, 1)
        self.edtDatetime = QtGui.QDateTimeEdit(InventoryDocumentDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDatetime.sizePolicy().hasHeightForWidth())
        self.edtDatetime.setSizePolicy(sizePolicy)
        self.edtDatetime.setCalendarPopup(True)
        self.edtDatetime.setObjectName(_fromUtf8("edtDatetime"))
        self.gridLayout.addWidget(self.edtDatetime, 1, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblSearch = QtGui.QLabel(InventoryDocumentDialog)
        self.lblSearch.setObjectName(_fromUtf8("lblSearch"))
        self.horizontalLayout.addWidget(self.lblSearch)
        self.edtSearch = CLineEdit(InventoryDocumentDialog)
        self.edtSearch.setObjectName(_fromUtf8("edtSearch"))
        self.horizontalLayout.addWidget(self.edtSearch)
        self.btnResetSearch = QtGui.QToolButton(InventoryDocumentDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnResetSearch.sizePolicy().hasHeightForWidth())
        self.btnResetSearch.setSizePolicy(sizePolicy)
        self.btnResetSearch.setObjectName(_fromUtf8("btnResetSearch"))
        self.horizontalLayout.addWidget(self.btnResetSearch)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.tblItems = CItemListView(InventoryDocumentDialog)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout_2.addWidget(self.tblItems, 2, 0, 1, 2)
        self.btnSaveInventory = QtGui.QPushButton(InventoryDocumentDialog)
        self.btnSaveInventory.setEnabled(False)
        self.btnSaveInventory.setObjectName(_fromUtf8("btnSaveInventory"))
        self.gridLayout_2.addWidget(self.btnSaveInventory, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(InventoryDocumentDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 3, 1, 1, 1)

        self.retranslateUi(InventoryDocumentDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), InventoryDocumentDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), InventoryDocumentDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(InventoryDocumentDialog)
        InventoryDocumentDialog.setTabOrder(self.edtNumber, self.edtDatetime)
        InventoryDocumentDialog.setTabOrder(self.edtDatetime, self.cmbUser)
        InventoryDocumentDialog.setTabOrder(self.cmbUser, self.cmbStore)
        InventoryDocumentDialog.setTabOrder(self.cmbStore, self.cmbCatalog)
        InventoryDocumentDialog.setTabOrder(self.cmbCatalog, self.edtSearch)
        InventoryDocumentDialog.setTabOrder(self.edtSearch, self.btnResetSearch)
        InventoryDocumentDialog.setTabOrder(self.btnResetSearch, self.tblItems)
        InventoryDocumentDialog.setTabOrder(self.tblItems, self.btnSaveInventory)
        InventoryDocumentDialog.setTabOrder(self.btnSaveInventory, self.buttonBox)

    def retranslateUi(self, InventoryDocumentDialog):
        InventoryDocumentDialog.setWindowTitle(_translate("InventoryDocumentDialog", "Dialog", None))
        self.lblCatalog.setText(_translate("InventoryDocumentDialog", "Каталог", None))
        self.lblDate.setText(_translate("InventoryDocumentDialog", "Дата", None))
        self.lblNumber.setText(_translate("InventoryDocumentDialog", "Номер инвентаризационной ведомости", None))
        self.lblStore.setText(_translate("InventoryDocumentDialog", "Склад", None))
        self.lblUser.setText(_translate("InventoryDocumentDialog", "Ревизор", None))
        self.edtDatetime.setDisplayFormat(_translate("InventoryDocumentDialog", "dd.MM.yyyy HH:mm", None))
        self.lblSearch.setText(_translate("InventoryDocumentDialog", "Поиск", None))
        self.btnResetSearch.setText(_translate("InventoryDocumentDialog", "X", None))
        self.btnSaveInventory.setText(_translate("InventoryDocumentDialog", "Провести", None))

from Pharmacy.ItemListComboBox import CCatalogComboBox, CStoreComboBox, CUserComboBox
from library.ItemListView import CItemListView
from library.LineEdit import CLineEdit
