# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CreateQueueDialog.ui'
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

class Ui_CreateQueueDialog(object):
    def setupUi(self, CreateQueueDialog):
        CreateQueueDialog.setObjectName(_fromUtf8("CreateQueueDialog"))
        CreateQueueDialog.resize(223, 266)
        self.gridLayout = QtGui.QGridLayout(CreateQueueDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblQueueType = QtGui.QLabel(CreateQueueDialog)
        self.lblQueueType.setObjectName(_fromUtf8("lblQueueType"))
        self.gridLayout.addWidget(self.lblQueueType, 0, 0, 1, 2)
        self.cmbMedicalProfile = CRBComboBox(CreateQueueDialog)
        self.cmbMedicalProfile.setObjectName(_fromUtf8("cmbMedicalProfile"))
        self.gridLayout.addWidget(self.cmbMedicalProfile, 1, 0, 1, 2)
        self.lblDateBegin = QtGui.QLabel(CreateQueueDialog)
        self.lblDateBegin.setObjectName(_fromUtf8("lblDateBegin"))
        self.gridLayout.addWidget(self.lblDateBegin, 2, 0, 1, 2)
        self.edtBeginDate = QtGui.QDateEdit(CreateQueueDialog)
        self.edtBeginDate.setObjectName(_fromUtf8("edtBeginDate"))
        self.gridLayout.addWidget(self.edtBeginDate, 3, 0, 1, 2)
        self.lblEndDate = QtGui.QLabel(CreateQueueDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 4, 0, 1, 2)
        self.edtEndDate = QtGui.QDateEdit(CreateQueueDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 5, 0, 1, 2)
        self.lblContacts = QtGui.QLabel(CreateQueueDialog)
        self.lblContacts.setObjectName(_fromUtf8("lblContacts"))
        self.gridLayout.addWidget(self.lblContacts, 6, 0, 1, 1)
        self.edtContacts = QtGui.QLineEdit(CreateQueueDialog)
        self.edtContacts.setObjectName(_fromUtf8("edtContacts"))
        self.gridLayout.addWidget(self.edtContacts, 7, 0, 1, 2)
        self.lblComment = QtGui.QLabel(CreateQueueDialog)
        self.lblComment.setObjectName(_fromUtf8("lblComment"))
        self.gridLayout.addWidget(self.lblComment, 8, 0, 1, 1)
        self.edtComment = QtGui.QLineEdit(CreateQueueDialog)
        self.edtComment.setObjectName(_fromUtf8("edtComment"))
        self.gridLayout.addWidget(self.edtComment, 9, 0, 1, 2)
        self.btnCreate = QtGui.QPushButton(CreateQueueDialog)
        self.btnCreate.setObjectName(_fromUtf8("btnCreate"))
        self.gridLayout.addWidget(self.btnCreate, 10, 0, 1, 1)
        self.btnCancel = QtGui.QPushButton(CreateQueueDialog)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridLayout.addWidget(self.btnCancel, 10, 1, 1, 1)

        self.retranslateUi(CreateQueueDialog)
        QtCore.QMetaObject.connectSlotsByName(CreateQueueDialog)

    def retranslateUi(self, CreateQueueDialog):
        CreateQueueDialog.setWindowTitle(_translate("CreateQueueDialog", "Добавление очереди", None))
        self.lblQueueType.setText(_translate("CreateQueueDialog", "Профиль помощи:", None))
        self.lblDateBegin.setText(_translate("CreateQueueDialog", "Дата начала оказания мед. помощи:", None))
        self.lblEndDate.setText(_translate("CreateQueueDialog", "Дата окончания оказания мед. помощи:", None))
        self.lblContacts.setText(_translate("CreateQueueDialog", "Контакты:", None))
        self.lblComment.setText(_translate("CreateQueueDialog", "Комментарий:", None))
        self.btnCreate.setText(_translate("CreateQueueDialog", "Добавить", None))
        self.btnCancel.setText(_translate("CreateQueueDialog", "Отмена", None))

from library.crbcombobox import CRBComboBox
