# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportAccount.ui'
#
# Created: Tue Jan 20 19:09:56 2015
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

class Ui_ReportAccount(object):
    def setupUi(self, ReportAccount):
        ReportAccount.setObjectName(_fromUtf8("ReportAccount"))
        ReportAccount.resize(400, 145)
        self.gridLayout = QtGui.QGridLayout(ReportAccount)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ReportAccount)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.cmbInsurerFilterDialog = CInsurerComboBox(ReportAccount)
        self.cmbInsurerFilterDialog.setObjectName(_fromUtf8("cmbInsurerFilterDialog"))
        self.gridLayout.addWidget(self.cmbInsurerFilterDialog, 1, 1, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAccount)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 4)
        self.lblBegDate = QtGui.QLabel(ReportAccount)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportAccount)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblFinance = QtGui.QLabel(ReportAccount)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 2, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportAccount)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 2, 1, 1, 3)
        self.label_2 = QtGui.QLabel(ReportAccount)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.cmbEventProfile = CRBComboBox(ReportAccount)
        self.cmbEventProfile.setObjectName(_fromUtf8("cmbEventProfile"))
        self.gridLayout.addWidget(self.cmbEventProfile, 3, 1, 1, 3)

        self.retranslateUi(ReportAccount)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAccount.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAccount.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAccount)

    def retranslateUi(self, ReportAccount):
        ReportAccount.setWindowTitle(_translate("ReportAccount", "Dialog", None))
        self.label.setText(_translate("ReportAccount", "Плательщик", None))
        self.lblBegDate.setText(_translate("ReportAccount", "Расчетная дата", None))
        self.lblFinance.setText(_translate("ReportAccount", "Тип финансирования", None))
        self.label_2.setText(_translate("ReportAccount", "Вид помощи", None))

from Orgs.OrgComboBox import CInsurerComboBox
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
