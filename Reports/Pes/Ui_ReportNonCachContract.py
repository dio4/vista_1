# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportNonCashContract.ui'
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

class Ui_ReportNonCashDialog(object):
    def setupUi(self, ReportNonCashDialog):
        ReportNonCashDialog.setObjectName(_fromUtf8("ReportNonCashDialog"))
        ReportNonCashDialog.resize(306, 161)
        self.gridLayout = QtGui.QGridLayout(ReportNonCashDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBeginDate = QtGui.QLabel(ReportNonCashDialog)
        self.lblBeginDate.setObjectName(_fromUtf8("lblBeginDate"))
        self.gridLayout.addWidget(self.lblBeginDate, 0, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportNonCashDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportNonCashDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 0, 3, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(ReportNonCashDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 0, 4, 1, 1)
        self.lblorgStatus = QtGui.QLabel(ReportNonCashDialog)
        self.lblorgStatus.setObjectName(_fromUtf8("lblorgStatus"))
        self.gridLayout.addWidget(self.lblorgStatus, 1, 0, 1, 2)
        self.cmbOrgStatus = QtGui.QComboBox(ReportNonCashDialog)
        self.cmbOrgStatus.setObjectName(_fromUtf8("cmbOrgStatus"))
        self.cmbOrgStatus.addItem(_fromUtf8(""))
        self.cmbOrgStatus.addItem(_fromUtf8(""))
        self.cmbOrgStatus.addItem(_fromUtf8(""))
        self.cmbOrgStatus.addItem(_fromUtf8(""))
        self.cmbOrgStatus.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbOrgStatus, 1, 2, 1, 3)
        self.lblPartner = QtGui.QLabel(ReportNonCashDialog)
        self.lblPartner.setObjectName(_fromUtf8("lblPartner"))
        self.gridLayout.addWidget(self.lblPartner, 2, 0, 1, 2)
        self.cmbPartner = COrgComboBox(ReportNonCashDialog)
        self.cmbPartner.setObjectName(_fromUtf8("cmbPartner"))
        self.gridLayout.addWidget(self.cmbPartner, 2, 2, 1, 3)
        self.chkIsValid = QtGui.QCheckBox(ReportNonCashDialog)
        self.chkIsValid.setObjectName(_fromUtf8("chkIsValid"))
        self.gridLayout.addWidget(self.chkIsValid, 3, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ReportNonCashDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 4)

        self.retranslateUi(ReportNonCashDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportNonCashDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportNonCashDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportNonCashDialog)

    def retranslateUi(self, ReportNonCashDialog):
        ReportNonCashDialog.setWindowTitle(_translate("ReportNonCashDialog", "Отчет: безналичные договоры", None))
        self.lblBeginDate.setText(_translate("ReportNonCashDialog", "С:", None))
        self.lblEndDate.setText(_translate("ReportNonCashDialog", "По:", None))
        self.lblorgStatus.setText(_translate("ReportNonCashDialog", "Статус органиации:", None))
        self.cmbOrgStatus.setItemText(0, _translate("ReportNonCashDialog", "Не задано", None))
        self.cmbOrgStatus.setItemText(1, _translate("ReportNonCashDialog", "Страховая компания", None))
        self.cmbOrgStatus.setItemText(2, _translate("ReportNonCashDialog", "Медицинский центр", None))
        self.cmbOrgStatus.setItemText(3, _translate("ReportNonCashDialog", "Благотворительное общество", None))
        self.cmbOrgStatus.setItemText(4, _translate("ReportNonCashDialog", "Другая организация", None))
        self.lblPartner.setText(_translate("ReportNonCashDialog", "Контрагент:", None))
        self.chkIsValid.setText(_translate("ReportNonCashDialog", "Только действующие", None))

from Orgs.OrgComboBox import COrgComboBox
