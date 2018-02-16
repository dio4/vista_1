# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StatReportF57NewSetup.ui'
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

class Ui_StatReportF57NewSetupDialog(object):
    def setupUi(self, StatReportF57NewSetupDialog):
        StatReportF57NewSetupDialog.setObjectName(_fromUtf8("StatReportF57NewSetupDialog"))
        StatReportF57NewSetupDialog.resize(517, 130)
        self.gridLayout = QtGui.QGridLayout(StatReportF57NewSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblReportType = QtGui.QLabel(StatReportF57NewSetupDialog)
        self.lblReportType.setObjectName(_fromUtf8("lblReportType"))
        self.gridLayout.addWidget(self.lblReportType, 0, 0, 1, 1)
        self.cmbReportType = QtGui.QComboBox(StatReportF57NewSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbReportType.sizePolicy().hasHeightForWidth())
        self.cmbReportType.setSizePolicy(sizePolicy)
        self.cmbReportType.setObjectName(_fromUtf8("cmbReportType"))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.cmbReportType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbReportType, 0, 1, 1, 1)
        self.lblDateRange = QtGui.QLabel(StatReportF57NewSetupDialog)
        self.lblDateRange.setObjectName(_fromUtf8("lblDateRange"))
        self.gridLayout.addWidget(self.lblDateRange, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.edtDateFrom = CDateEdit(StatReportF57NewSetupDialog)
        self.edtDateFrom.setObjectName(_fromUtf8("edtDateFrom"))
        self.horizontalLayout_2.addWidget(self.edtDateFrom)
        self.lblDateTo = QtGui.QLabel(StatReportF57NewSetupDialog)
        self.lblDateTo.setObjectName(_fromUtf8("lblDateTo"))
        self.horizontalLayout_2.addWidget(self.lblDateTo)
        self.edtDateTo = CDateEdit(StatReportF57NewSetupDialog)
        self.edtDateTo.setObjectName(_fromUtf8("edtDateTo"))
        self.horizontalLayout_2.addWidget(self.edtDateTo)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(StatReportF57NewSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 2)
        self.gridLayout.setColumnStretch(1, 1)

        self.retranslateUi(StatReportF57NewSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StatReportF57NewSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StatReportF57NewSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StatReportF57NewSetupDialog)

    def retranslateUi(self, StatReportF57NewSetupDialog):
        StatReportF57NewSetupDialog.setWindowTitle(_translate("StatReportF57NewSetupDialog", "Форма 57", None))
        self.lblReportType.setText(_translate("StatReportF57NewSetupDialog", "Тип отчета", None))
        self.cmbReportType.setItemText(0, _translate("StatReportF57NewSetupDialog", "Дети (0-17 лет включительно)", None))
        self.cmbReportType.setItemText(1, _translate("StatReportF57NewSetupDialog", "Взрослые (18+ лет)", None))
        self.cmbReportType.setItemText(2, _translate("StatReportF57NewSetupDialog", "Старше трудоспособного возраста (муж. 60+ лет, жен. 55+ лет)", None))
        self.cmbReportType.setItemText(3, _translate("StatReportF57NewSetupDialog", "Общая сводка", None))
        self.lblDateRange.setText(_translate("StatReportF57NewSetupDialog", "За период с", None))
        self.lblDateTo.setText(_translate("StatReportF57NewSetupDialog", "по", None))

from library.DateEdit import CDateEdit
