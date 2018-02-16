# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DailyServicesReport.ui'
#
# Created: Tue Jan 12 19:44:52 2016
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

class Ui_DailyServicesReportSetupDialog(object):
    def setupUi(self, DailyServicesReportSetupDialog):
        DailyServicesReportSetupDialog.setObjectName(_fromUtf8("DailyServicesReportSetupDialog"))
        DailyServicesReportSetupDialog.resize(357, 209)
        self.gridLayout = QtGui.QGridLayout(DailyServicesReportSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbPayStatus = QtGui.QComboBox(DailyServicesReportSetupDialog)
        self.cmbPayStatus.setObjectName(_fromUtf8("cmbPayStatus"))
        self.cmbPayStatus.addItem(_fromUtf8(""))
        self.cmbPayStatus.addItem(_fromUtf8(""))
        self.cmbPayStatus.addItem(_fromUtf8(""))
        self.cmbPayStatus.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbPayStatus, 2, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(64, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.edtDate = CDateEdit(DailyServicesReportSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDate.sizePolicy().hasHeightForWidth())
        self.edtDate.setSizePolicy(sizePolicy)
        self.edtDate.setCalendarPopup(True)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 0, 1, 1, 1)
        self.lblPayStatus = QtGui.QLabel(DailyServicesReportSetupDialog)
        self.lblPayStatus.setObjectName(_fromUtf8("lblPayStatus"))
        self.gridLayout.addWidget(self.lblPayStatus, 2, 0, 1, 1)
        self.lblDate = QtGui.QLabel(DailyServicesReportSetupDialog)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.cmbFinanceSource = CRBComboBox(DailyServicesReportSetupDialog)
        self.cmbFinanceSource.setObjectName(_fromUtf8("cmbFinanceSource"))
        self.gridLayout.addWidget(self.cmbFinanceSource, 1, 1, 1, 2)
        self.lblFinanceSource = QtGui.QLabel(DailyServicesReportSetupDialog)
        self.lblFinanceSource.setObjectName(_fromUtf8("lblFinanceSource"))
        self.gridLayout.addWidget(self.lblFinanceSource, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(DailyServicesReportSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 2)
        self.lblDate.setBuddy(self.edtDate)

        self.retranslateUi(DailyServicesReportSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DailyServicesReportSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DailyServicesReportSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DailyServicesReportSetupDialog)

    def retranslateUi(self, DailyServicesReportSetupDialog):
        DailyServicesReportSetupDialog.setWindowTitle(_translate("DailyServicesReportSetupDialog", "Dialog", None))
        self.cmbPayStatus.setItemText(0, _translate("DailyServicesReportSetupDialog", "не выбрано", None))
        self.cmbPayStatus.setItemText(1, _translate("DailyServicesReportSetupDialog", "оплачено", None))
        self.cmbPayStatus.setItemText(2, _translate("DailyServicesReportSetupDialog", "выставлено", None))
        self.cmbPayStatus.setItemText(3, _translate("DailyServicesReportSetupDialog", "отказано", None))
        self.lblPayStatus.setText(_translate("DailyServicesReportSetupDialog", "Состояние оплаты", None))
        self.lblDate.setText(_translate("DailyServicesReportSetupDialog", "Дата", None))
        self.lblFinanceSource.setText(_translate("DailyServicesReportSetupDialog", "Источник финансирования", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
