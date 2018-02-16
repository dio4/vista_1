# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RequestDocumentDialog.ui'
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

class Ui_RequestDocumentDialog(object):
    def setupUi(self, RequestDocumentDialog):
        RequestDocumentDialog.setObjectName(_fromUtf8("RequestDocumentDialog"))
        RequestDocumentDialog.resize(640, 501)
        self.gridLayout_2 = QtGui.QGridLayout(RequestDocumentDialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDocumentId = QtGui.QLabel(RequestDocumentDialog)
        self.lblDocumentId.setObjectName(_fromUtf8("lblDocumentId"))
        self.gridLayout.addWidget(self.lblDocumentId, 0, 0, 1, 1)
        self.edtDocumentId = QtGui.QLineEdit(RequestDocumentDialog)
        self.edtDocumentId.setReadOnly(True)
        self.edtDocumentId.setObjectName(_fromUtf8("edtDocumentId"))
        self.gridLayout.addWidget(self.edtDocumentId, 0, 1, 1, 1)
        self.cmbStoreTo = CStoreComboBox(RequestDocumentDialog)
        self.cmbStoreTo.setObjectName(_fromUtf8("cmbStoreTo"))
        self.gridLayout.addWidget(self.cmbStoreTo, 2, 3, 1, 1)
        self.lblStoreTo = QtGui.QLabel(RequestDocumentDialog)
        self.lblStoreTo.setObjectName(_fromUtf8("lblStoreTo"))
        self.gridLayout.addWidget(self.lblStoreTo, 2, 2, 1, 1)
        self.edtHistoryNumber = QtGui.QLineEdit(RequestDocumentDialog)
        self.edtHistoryNumber.setObjectName(_fromUtf8("edtHistoryNumber"))
        self.gridLayout.addWidget(self.edtHistoryNumber, 3, 3, 1, 1)
        self.lblHistoryNumber = QtGui.QLabel(RequestDocumentDialog)
        self.lblHistoryNumber.setObjectName(_fromUtf8("lblHistoryNumber"))
        self.gridLayout.addWidget(self.lblHistoryNumber, 3, 2, 1, 1)
        self.lblUser = QtGui.QLabel(RequestDocumentDialog)
        self.lblUser.setObjectName(_fromUtf8("lblUser"))
        self.gridLayout.addWidget(self.lblUser, 3, 0, 1, 1)
        self.cmbUser = CUserComboBox(RequestDocumentDialog)
        self.cmbUser.setObjectName(_fromUtf8("cmbUser"))
        self.gridLayout.addWidget(self.cmbUser, 3, 1, 1, 1)
        self.lblStoreFrom = QtGui.QLabel(RequestDocumentDialog)
        self.lblStoreFrom.setObjectName(_fromUtf8("lblStoreFrom"))
        self.gridLayout.addWidget(self.lblStoreFrom, 2, 0, 1, 1)
        self.cmbStoreFrom = CStoreComboBox(RequestDocumentDialog)
        self.cmbStoreFrom.setObjectName(_fromUtf8("cmbStoreFrom"))
        self.gridLayout.addWidget(self.cmbStoreFrom, 2, 1, 1, 1)
        self.edtDatetime = QtGui.QDateTimeEdit(RequestDocumentDialog)
        self.edtDatetime.setCalendarPopup(True)
        self.edtDatetime.setObjectName(_fromUtf8("edtDatetime"))
        self.gridLayout.addWidget(self.edtDatetime, 1, 3, 1, 1)
        self.lblDate = QtGui.QLabel(RequestDocumentDialog)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 1, 2, 1, 1)
        self.lblType = QtGui.QLabel(RequestDocumentDialog)
        self.lblType.setObjectName(_fromUtf8("lblType"))
        self.gridLayout.addWidget(self.lblType, 1, 0, 1, 1)
        self.cmbType = CEnumComboBox(RequestDocumentDialog)
        self.cmbType.setObjectName(_fromUtf8("cmbType"))
        self.gridLayout.addWidget(self.cmbType, 1, 1, 1, 1)
        self.lblNumber = QtGui.QLabel(RequestDocumentDialog)
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.gridLayout.addWidget(self.lblNumber, 0, 2, 1, 1)
        self.edtNumber = QtGui.QLineEdit(RequestDocumentDialog)
        self.edtNumber.setObjectName(_fromUtf8("edtNumber"))
        self.gridLayout.addWidget(self.edtNumber, 0, 3, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RequestDocumentDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 5, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnFinalize = QtGui.QPushButton(RequestDocumentDialog)
        self.btnFinalize.setEnabled(False)
        self.btnFinalize.setObjectName(_fromUtf8("btnFinalize"))
        self.horizontalLayout.addWidget(self.btnFinalize)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.horizontalLayout, 4, 0, 1, 1)
        self.tblItems = CItemListView(RequestDocumentDialog)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout_2.addWidget(self.tblItems, 1, 0, 1, 1)

        self.retranslateUi(RequestDocumentDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RequestDocumentDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RequestDocumentDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RequestDocumentDialog)
        RequestDocumentDialog.setTabOrder(self.edtDocumentId, self.edtNumber)
        RequestDocumentDialog.setTabOrder(self.edtNumber, self.cmbType)
        RequestDocumentDialog.setTabOrder(self.cmbType, self.edtDatetime)
        RequestDocumentDialog.setTabOrder(self.edtDatetime, self.cmbStoreFrom)
        RequestDocumentDialog.setTabOrder(self.cmbStoreFrom, self.cmbStoreTo)
        RequestDocumentDialog.setTabOrder(self.cmbStoreTo, self.cmbUser)
        RequestDocumentDialog.setTabOrder(self.cmbUser, self.edtHistoryNumber)
        RequestDocumentDialog.setTabOrder(self.edtHistoryNumber, self.tblItems)
        RequestDocumentDialog.setTabOrder(self.tblItems, self.btnFinalize)
        RequestDocumentDialog.setTabOrder(self.btnFinalize, self.buttonBox)

    def retranslateUi(self, RequestDocumentDialog):
        RequestDocumentDialog.setWindowTitle(_translate("RequestDocumentDialog", "Dialog", None))
        self.lblDocumentId.setText(_translate("RequestDocumentDialog", "Порядковый номер", None))
        self.lblStoreTo.setText(_translate("RequestDocumentDialog", "Получатель", None))
        self.lblHistoryNumber.setText(_translate("RequestDocumentDialog", "Номер истории болезни", None))
        self.lblUser.setText(_translate("RequestDocumentDialog", "Заявитель", None))
        self.lblStoreFrom.setText(_translate("RequestDocumentDialog", "Отправитель", None))
        self.edtDatetime.setDisplayFormat(_translate("RequestDocumentDialog", "dd.MM.yyyy HH:mm", None))
        self.lblDate.setText(_translate("RequestDocumentDialog", "Дата создания", None))
        self.lblType.setText(_translate("RequestDocumentDialog", "Тип", None))
        self.lblNumber.setText(_translate("RequestDocumentDialog", "Номер", None))
        self.btnFinalize.setText(_translate("RequestDocumentDialog", "Утвердить", None))

from Pharmacy.ItemListComboBox import CStoreComboBox, CUserComboBox
from library.Enum import CEnumComboBox
from library.ItemListView import CItemListView
