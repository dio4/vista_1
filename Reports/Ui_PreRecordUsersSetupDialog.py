# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PreRecordUsersSetupDialog.ui'
#
# Created: Wed Jun 18 21:51:54 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_PreRecordUsersSetupDialog(object):
    def setupUi(self, PreRecordUsersSetupDialog):
        PreRecordUsersSetupDialog.setObjectName(_fromUtf8("PreRecordUsersSetupDialog"))
        PreRecordUsersSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PreRecordUsersSetupDialog.resize(592, 232)
        PreRecordUsersSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(PreRecordUsersSetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbOrgStructure = COrgStructureComboBox(PreRecordUsersSetupDialog)
        self.cmbOrgStructure.setEnabled(False)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 4)
        self.chkWrittenFromZhos = QtGui.QCheckBox(PreRecordUsersSetupDialog)
        self.chkWrittenFromZhos.setObjectName(_fromUtf8("chkWrittenFromZhos"))
        self.gridLayout.addWidget(self.chkWrittenFromZhos, 8, 1, 1, 1)
        self.chkDetailCallCentr = QtGui.QCheckBox(PreRecordUsersSetupDialog)
        self.chkDetailCallCentr.setObjectName(_fromUtf8("chkDetailCallCentr"))
        self.gridLayout.addWidget(self.chkDetailCallCentr, 4, 1, 1, 4)
        self.lblEndDate = QtGui.QLabel(PreRecordUsersSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 0, 2, 1, 1)
        self.edtEndDate = CDateEdit(PreRecordUsersSetupDialog)
        self.edtEndDate.setEnabled(True)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 0, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(28, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 4, 1, 1)
        self.chkPeriodBeforeRecord = QtGui.QCheckBox(PreRecordUsersSetupDialog)
        self.chkPeriodBeforeRecord.setChecked(False)
        self.chkPeriodBeforeRecord.setObjectName(_fromUtf8("chkPeriodBeforeRecord"))
        self.gridLayout.addWidget(self.chkPeriodBeforeRecord, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(PreRecordUsersSetupDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PreRecordUsersSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 5)
        self.edtEndDateRecord = CDateEdit(PreRecordUsersSetupDialog)
        self.edtEndDateRecord.setEnabled(False)
        self.edtEndDateRecord.setCalendarPopup(True)
        self.edtEndDateRecord.setObjectName(_fromUtf8("edtEndDateRecord"))
        self.gridLayout.addWidget(self.edtEndDateRecord, 1, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(28, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 4, 1, 1)
        self.chkOrgStructure = QtGui.QCheckBox(PreRecordUsersSetupDialog)
        self.chkOrgStructure.setObjectName(_fromUtf8("chkOrgStructure"))
        self.gridLayout.addWidget(self.chkOrgStructure, 2, 0, 1, 1)
        self.chkPeriodRecord = QtGui.QCheckBox(PreRecordUsersSetupDialog)
        self.chkPeriodRecord.setChecked(True)
        self.chkPeriodRecord.setObjectName(_fromUtf8("chkPeriodRecord"))
        self.gridLayout.addWidget(self.chkPeriodRecord, 0, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(PreRecordUsersSetupDialog)
        self.cmbPerson.setEnabled(False)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 3, 1, 1, 4)
        self.edtBegDateRecord = CDateEdit(PreRecordUsersSetupDialog)
        self.edtBegDateRecord.setEnabled(False)
        self.edtBegDateRecord.setCalendarPopup(True)
        self.edtBegDateRecord.setObjectName(_fromUtf8("edtBegDateRecord"))
        self.gridLayout.addWidget(self.edtBegDateRecord, 1, 1, 1, 1)
        self.lblPerson = QtGui.QLabel(PreRecordUsersSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 3, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 30, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 8, 0, 1, 1)
        self.edtBegDate = CDateEdit(PreRecordUsersSetupDialog)
        self.edtBegDate.setEnabled(True)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.chkShowWithoutOverTime = QtGui.QCheckBox(PreRecordUsersSetupDialog)
        self.chkShowWithoutOverTime.setObjectName(_fromUtf8("chkShowWithoutOverTime"))
        self.gridLayout.addWidget(self.chkShowWithoutOverTime, 5, 1, 1, 3)
        self.chkIgnoreRehabilitation = QtGui.QCheckBox(PreRecordUsersSetupDialog)
        self.chkIgnoreRehabilitation.setObjectName(_fromUtf8("chkIgnoreRehabilitation"))
        self.gridLayout.addWidget(self.chkIgnoreRehabilitation, 6, 1, 1, 3)
        self.chkIsGroupBySpeciality = QtGui.QCheckBox(PreRecordUsersSetupDialog)
        self.chkIsGroupBySpeciality.setObjectName(_fromUtf8("chkIsGroupBySpeciality"))
        self.gridLayout.addWidget(self.chkIsGroupBySpeciality, 7, 1, 1, 3)
        self.chkOnlyWithExternalQuota = QtGui.QCheckBox(PreRecordUsersSetupDialog)
        self.chkOnlyWithExternalQuota.setObjectName(_fromUtf8("chkOnlyWithExternalQuota"))
        self.gridLayout.addWidget(self.chkOnlyWithExternalQuota, 9, 1, 1, 4)
        self.lblPerson.setBuddy(self.cmbPerson)

        self.retranslateUi(PreRecordUsersSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PreRecordUsersSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PreRecordUsersSetupDialog.reject)
        QtCore.QObject.connect(self.chkOrgStructure, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cmbOrgStructure.setEnabled)
        QtCore.QObject.connect(self.chkOrgStructure, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cmbPerson.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(PreRecordUsersSetupDialog)
        PreRecordUsersSetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbPerson)
        PreRecordUsersSetupDialog.setTabOrder(self.cmbPerson, self.buttonBox)

    def retranslateUi(self, PreRecordUsersSetupDialog):
        PreRecordUsersSetupDialog.setWindowTitle(_translate("PreRecordUsersSetupDialog", "параметры отчёта", None))
        self.chkWrittenFromZhos.setText(_translate("PreRecordUsersSetupDialog", "Записаны из ЖОС", None))
        self.chkDetailCallCentr.setText(_translate("PreRecordUsersSetupDialog", "Детализировать Call-центр", None))
        self.lblEndDate.setText(_translate("PreRecordUsersSetupDialog", "по", None))
        self.chkPeriodBeforeRecord.setText(_translate("PreRecordUsersSetupDialog", "Период предварительной записи с", None))
        self.label_2.setText(_translate("PreRecordUsersSetupDialog", "по", None))
        self.chkOrgStructure.setText(_translate("PreRecordUsersSetupDialog", "&Подразделение", None))
        self.chkPeriodRecord.setText(_translate("PreRecordUsersSetupDialog", "Период постановки в очередь с", None))
        self.lblPerson.setText(_translate("PreRecordUsersSetupDialog", "&Врач", None))
        self.chkShowWithoutOverTime.setText(_translate("PreRecordUsersSetupDialog", "Не выводить пациентов сверх очереди", None))
        self.chkIgnoreRehabilitation.setText(_translate("PreRecordUsersSetupDialog", "Не учитывать реабилитационное отделение", None))
        self.chkIsGroupBySpeciality.setText(_translate("PreRecordUsersSetupDialog", "Группировать по специальностям", None))
        self.chkOnlyWithExternalQuota.setText(_translate("PreRecordUsersSetupDialog", "Учитывать запись только к врачам, имеющим внешнюю квоту", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
