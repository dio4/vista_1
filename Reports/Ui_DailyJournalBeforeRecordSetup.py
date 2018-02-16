# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DailyJournalBeforeRecordSetup.ui'
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

class Ui_DailyJournalBeforeRecordSetup(object):
    def setupUi(self, DailyJournalBeforeRecordSetup):
        DailyJournalBeforeRecordSetup.setObjectName(_fromUtf8("DailyJournalBeforeRecordSetup"))
        DailyJournalBeforeRecordSetup.setWindowModality(QtCore.Qt.ApplicationModal)
        DailyJournalBeforeRecordSetup.resize(605, 392)
        DailyJournalBeforeRecordSetup.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(DailyJournalBeforeRecordSetup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbAccountingSystem = CRBComboBox(DailyJournalBeforeRecordSetup)
        self.cmbAccountingSystem.setObjectName(_fromUtf8("cmbAccountingSystem"))
        self.gridLayout.addWidget(self.cmbAccountingSystem, 5, 2, 1, 3)
        self.cmbOrderSorting = QtGui.QComboBox(DailyJournalBeforeRecordSetup)
        self.cmbOrderSorting.setObjectName(_fromUtf8("cmbOrderSorting"))
        self.cmbOrderSorting.addItem(_fromUtf8(""))
        self.cmbOrderSorting.addItem(_fromUtf8(""))
        self.cmbOrderSorting.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbOrderSorting, 6, 2, 1, 3)
        self.lblOrgStructure = QtGui.QLabel(DailyJournalBeforeRecordSetup)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 3, 0, 1, 1)
        self.chkFreeTimes = QtGui.QCheckBox(DailyJournalBeforeRecordSetup)
        self.chkFreeTimes.setObjectName(_fromUtf8("chkFreeTimes"))
        self.gridLayout.addWidget(self.chkFreeTimes, 8, 2, 1, 2)
        self.chkNoTimeLinePerson = QtGui.QCheckBox(DailyJournalBeforeRecordSetup)
        self.chkNoTimeLinePerson.setObjectName(_fromUtf8("chkNoTimeLinePerson"))
        self.gridLayout.addWidget(self.chkNoTimeLinePerson, 10, 2, 1, 2)
        self.lblBegDate = QtGui.QLabel(DailyJournalBeforeRecordSetup)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.lblOrderSorting = QtGui.QLabel(DailyJournalBeforeRecordSetup)
        self.lblOrderSorting.setObjectName(_fromUtf8("lblOrderSorting"))
        self.gridLayout.addWidget(self.lblOrderSorting, 6, 0, 1, 1)
        self.lblUserProfile = QtGui.QLabel(DailyJournalBeforeRecordSetup)
        self.lblUserProfile.setObjectName(_fromUtf8("lblUserProfile"))
        self.gridLayout.addWidget(self.lblUserProfile, 5, 0, 1, 1)
        self.edtBegDate = CDateEdit(DailyJournalBeforeRecordSetup)
        self.edtBegDate.setEnabled(True)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(DailyJournalBeforeRecordSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 14, 0, 1, 4)
        self.lblIsPrimary = QtGui.QLabel(DailyJournalBeforeRecordSetup)
        self.lblIsPrimary.setObjectName(_fromUtf8("lblIsPrimary"))
        self.gridLayout.addWidget(self.lblIsPrimary, 7, 0, 1, 2)
        self.chkPegeFormat = QtGui.QCheckBox(DailyJournalBeforeRecordSetup)
        self.chkPegeFormat.setChecked(True)
        self.chkPegeFormat.setObjectName(_fromUtf8("chkPegeFormat"))
        self.gridLayout.addWidget(self.chkPegeFormat, 9, 2, 1, 2)
        self.lblPerson = QtGui.QLabel(DailyJournalBeforeRecordSetup)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 4, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.chkViewBirthDate = QtGui.QCheckBox(DailyJournalBeforeRecordSetup)
        self.chkViewBirthDate.setObjectName(_fromUtf8("chkViewBirthDate"))
        self.gridLayout.addWidget(self.chkViewBirthDate, 11, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(21, 21, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 13, 1, 1, 1)
        self.chkViewRegAdress = QtGui.QCheckBox(DailyJournalBeforeRecordSetup)
        self.chkViewRegAdress.setObjectName(_fromUtf8("chkViewRegAdress"))
        self.gridLayout.addWidget(self.chkViewRegAdress, 12, 2, 1, 1)
        self.cmbIsPrimary = QtGui.QComboBox(DailyJournalBeforeRecordSetup)
        self.cmbIsPrimary.setObjectName(_fromUtf8("cmbIsPrimary"))
        self.cmbIsPrimary.addItem(_fromUtf8(""))
        self.cmbIsPrimary.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbIsPrimary, 7, 2, 1, 3)
        self.cmbPerson = CPersonComboBoxEx(DailyJournalBeforeRecordSetup)
        self.cmbPerson.setEnabled(True)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 4, 2, 1, 3)
        self.cmbOrgStructure = COrgStructureComboBox(DailyJournalBeforeRecordSetup)
        self.cmbOrgStructure.setEnabled(True)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 2, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblPerson.setBuddy(self.cmbPerson)

        self.retranslateUi(DailyJournalBeforeRecordSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DailyJournalBeforeRecordSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DailyJournalBeforeRecordSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(DailyJournalBeforeRecordSetup)
        DailyJournalBeforeRecordSetup.setTabOrder(self.edtBegDate, self.cmbOrgStructure)
        DailyJournalBeforeRecordSetup.setTabOrder(self.cmbOrgStructure, self.cmbPerson)
        DailyJournalBeforeRecordSetup.setTabOrder(self.cmbPerson, self.cmbAccountingSystem)
        DailyJournalBeforeRecordSetup.setTabOrder(self.cmbAccountingSystem, self.cmbOrderSorting)
        DailyJournalBeforeRecordSetup.setTabOrder(self.cmbOrderSorting, self.cmbIsPrimary)
        DailyJournalBeforeRecordSetup.setTabOrder(self.cmbIsPrimary, self.chkFreeTimes)
        DailyJournalBeforeRecordSetup.setTabOrder(self.chkFreeTimes, self.chkPegeFormat)
        DailyJournalBeforeRecordSetup.setTabOrder(self.chkPegeFormat, self.chkNoTimeLinePerson)
        DailyJournalBeforeRecordSetup.setTabOrder(self.chkNoTimeLinePerson, self.buttonBox)

    def retranslateUi(self, DailyJournalBeforeRecordSetup):
        DailyJournalBeforeRecordSetup.setWindowTitle(_translate("DailyJournalBeforeRecordSetup", "Суточный журнал предварительной записи", None))
        self.cmbOrderSorting.setItemText(0, _translate("DailyJournalBeforeRecordSetup", "по идентификатору", None))
        self.cmbOrderSorting.setItemText(1, _translate("DailyJournalBeforeRecordSetup", "по времени", None))
        self.cmbOrderSorting.setItemText(2, _translate("DailyJournalBeforeRecordSetup", "по ФИО", None))
        self.lblOrgStructure.setText(_translate("DailyJournalBeforeRecordSetup", "Подразделение", None))
        self.chkFreeTimes.setText(_translate("DailyJournalBeforeRecordSetup", "Выводить свободное время", None))
        self.chkNoTimeLinePerson.setText(_translate("DailyJournalBeforeRecordSetup", "Выводить пустые графики", None))
        self.lblBegDate.setText(_translate("DailyJournalBeforeRecordSetup", "Дата", None))
        self.lblOrderSorting.setText(_translate("DailyJournalBeforeRecordSetup", "Порядок сортировки", None))
        self.lblUserProfile.setText(_translate("DailyJournalBeforeRecordSetup", "Тип идентификатора пациента", None))
        self.lblIsPrimary.setText(_translate("DailyJournalBeforeRecordSetup", "Первичные", None))
        self.chkPegeFormat.setText(_translate("DailyJournalBeforeRecordSetup", "Выводить с начала листа", None))
        self.lblPerson.setText(_translate("DailyJournalBeforeRecordSetup", "&Врач", None))
        self.chkViewBirthDate.setText(_translate("DailyJournalBeforeRecordSetup", "Выводить дату рождения вместо возраста", None))
        self.chkViewRegAdress.setText(_translate("DailyJournalBeforeRecordSetup", "Выводить адрес регистрации вместо прикрекления", None))
        self.cmbIsPrimary.setItemText(0, _translate("DailyJournalBeforeRecordSetup", "Нет", None))
        self.cmbIsPrimary.setItemText(1, _translate("DailyJournalBeforeRecordSetup", "Да", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
