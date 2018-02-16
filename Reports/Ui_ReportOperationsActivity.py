# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportOperationsActivity.ui'
#
# Created: Wed Aug 12 11:21:02 2015
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

class Ui_ReportOperationsActivity(object):
    def setupUi(self, ReportOperationsActivity):
        ReportOperationsActivity.setObjectName(_fromUtf8("ReportOperationsActivity"))
        ReportOperationsActivity.resize(789, 456)
        self.gridLayout = QtGui.QGridLayout(ReportOperationsActivity)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ReportOperationsActivity)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 8, 0, 1, 1)
        self.lstOrgStructure = CRBListBox(ReportOperationsActivity)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridLayout.addWidget(self.lstOrgStructure, 5, 0, 1, 3)
        self.chkOrgStructureMulti = QtGui.QCheckBox(ReportOperationsActivity)
        self.chkOrgStructureMulti.setObjectName(_fromUtf8("chkOrgStructureMulti"))
        self.gridLayout.addWidget(self.chkOrgStructureMulti, 3, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportOperationsActivity)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 1, 1, 2)
        self.edtBegDate = CDateEdit(ReportOperationsActivity)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportOperationsActivity)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(ReportOperationsActivity)
        self.groupBox.setEnabled(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.chkExternalId = QtGui.QCheckBox(self.groupBox)
        self.chkExternalId.setChecked(True)
        self.chkExternalId.setObjectName(_fromUtf8("chkExternalId"))
        self.gridLayout_2.addWidget(self.chkExternalId, 1, 0, 1, 1)
        self.chkClientId = QtGui.QCheckBox(self.groupBox)
        self.chkClientId.setChecked(True)
        self.chkClientId.setObjectName(_fromUtf8("chkClientId"))
        self.gridLayout_2.addWidget(self.chkClientId, 3, 0, 1, 1)
        self.chkFullName = QtGui.QCheckBox(self.groupBox)
        self.chkFullName.setChecked(True)
        self.chkFullName.setObjectName(_fromUtf8("chkFullName"))
        self.gridLayout_2.addWidget(self.chkFullName, 5, 0, 1, 1)
        self.chkDaysBefore = QtGui.QCheckBox(self.groupBox)
        self.chkDaysBefore.setChecked(True)
        self.chkDaysBefore.setObjectName(_fromUtf8("chkDaysBefore"))
        self.gridLayout_2.addWidget(self.chkDaysBefore, 1, 1, 1, 1)
        self.chkDaysAfter = QtGui.QCheckBox(self.groupBox)
        self.chkDaysAfter.setChecked(True)
        self.chkDaysAfter.setObjectName(_fromUtf8("chkDaysAfter"))
        self.gridLayout_2.addWidget(self.chkDaysAfter, 3, 1, 1, 1)
        self.chkExecPerson = QtGui.QCheckBox(self.groupBox)
        self.chkExecPerson.setChecked(True)
        self.chkExecPerson.setObjectName(_fromUtf8("chkExecPerson"))
        self.gridLayout_2.addWidget(self.chkExecPerson, 5, 1, 1, 1)
        self.chkExecDate = QtGui.QCheckBox(self.groupBox)
        self.chkExecDate.setChecked(True)
        self.chkExecDate.setObjectName(_fromUtf8("chkExecDate"))
        self.gridLayout_2.addWidget(self.chkExecDate, 1, 2, 1, 1)
        self.chkResult = QtGui.QCheckBox(self.groupBox)
        self.chkResult.setChecked(True)
        self.chkResult.setObjectName(_fromUtf8("chkResult"))
        self.gridLayout_2.addWidget(self.chkResult, 3, 2, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 9, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ReportOperationsActivity)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 11, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)
        self.edtEndDate = CDateEdit(ReportOperationsActivity)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.cmbResult = CRBComboBox(ReportOperationsActivity)
        self.cmbResult.setObjectName(_fromUtf8("cmbResult"))
        self.cmbResult.addItem(_fromUtf8(""))
        self.cmbResult.addItem(_fromUtf8(""))
        self.cmbResult.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbResult, 8, 1, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportOperationsActivity)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.chkGroupOrgStructure = QtGui.QCheckBox(ReportOperationsActivity)
        self.chkGroupOrgStructure.setObjectName(_fromUtf8("chkGroupOrgStructure"))
        self.gridLayout.addWidget(self.chkGroupOrgStructure, 6, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 10, 0, 1, 1)
        self.chkClientDetail = QtGui.QCheckBox(ReportOperationsActivity)
        self.chkClientDetail.setObjectName(_fromUtf8("chkClientDetail"))
        self.gridLayout.addWidget(self.chkClientDetail, 7, 0, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportOperationsActivity)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportOperationsActivity.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportOperationsActivity.reject)
        QtCore.QObject.connect(self.chkClientDetail, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.groupBox.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ReportOperationsActivity)

    def retranslateUi(self, ReportOperationsActivity):
        ReportOperationsActivity.setWindowTitle(_translate("ReportOperationsActivity", "Dialog", None))
        self.label.setText(_translate("ReportOperationsActivity", "Результат события", None))
        self.chkOrgStructureMulti.setText(_translate("ReportOperationsActivity", "Подразделение", None))
        self.lblBegDate.setText(_translate("ReportOperationsActivity", "Дата &начала периода", None))
        self.groupBox.setTitle(_translate("ReportOperationsActivity", "Отчет строится по столбцам", None))
        self.chkExternalId.setText(_translate("ReportOperationsActivity", "№ ИБ", None))
        self.chkClientId.setText(_translate("ReportOperationsActivity", "№ Амб. карты", None))
        self.chkFullName.setText(_translate("ReportOperationsActivity", "ФИО", None))
        self.chkDaysBefore.setText(_translate("ReportOperationsActivity", "Кол-во дней до", None))
        self.chkDaysAfter.setText(_translate("ReportOperationsActivity", "Кол-во дней после", None))
        self.chkExecPerson.setText(_translate("ReportOperationsActivity", "Лечащий врач", None))
        self.chkExecDate.setText(_translate("ReportOperationsActivity", "Дата выписки", None))
        self.chkResult.setText(_translate("ReportOperationsActivity", "Результат", None))
        self.cmbResult.setItemText(0, _translate("ReportOperationsActivity", "не задано", None))
        self.cmbResult.setItemText(1, _translate("ReportOperationsActivity", "умер", None))
        self.cmbResult.setItemText(2, _translate("ReportOperationsActivity", "выписан", None))
        self.lblEndDate.setText(_translate("ReportOperationsActivity", "Дата &окончания периода", None))
        self.chkGroupOrgStructure.setText(_translate("ReportOperationsActivity", "Группировать по отделениям", None))
        self.chkClientDetail.setText(_translate("ReportOperationsActivity", "Детализировать по пациентам", None))

from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.RBListBox import CRBListBox
