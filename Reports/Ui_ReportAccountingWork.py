# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Reports/ReportAccountingWork.ui'
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

class Ui_ReportAccountingWork(object):
    def setupUi(self, ReportAccountingWork):
        ReportAccountingWork.setObjectName(_fromUtf8("ReportAccountingWork"))
        ReportAccountingWork.resize(375, 269)
        self.gridLayout = QtGui.QGridLayout(ReportAccountingWork)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblOrgStructure = QtGui.QLabel(ReportAccountingWork)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 6, 0, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportAccountingWork)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 8, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportAccountingWork)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 6, 1, 1, 2)
        self.cmbEventType = CRBComboBox(ReportAccountingWork)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 4, 1, 1, 2)
        self.lblEventType = QtGui.QLabel(ReportAccountingWork)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 4, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportAccountingWork)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportAccountingWork)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        self.edtBegDate = CDateEdit(ReportAccountingWork)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportAccountingWork)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.cmbPerson = CPersonComboBoxEx(ReportAccountingWork)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 8, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAccountingWork)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 12, 0, 1, 3)
        self.chkGroup = QtGui.QCheckBox(ReportAccountingWork)
        self.chkGroup.setObjectName(_fromUtf8("chkGroup"))
        self.gridLayout.addWidget(self.chkGroup, 10, 1, 1, 1)
        self.lblSpeciality = QtGui.QLabel(ReportAccountingWork)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout.addWidget(self.lblSpeciality, 5, 0, 1, 1)
        self.cmbSpetiality = CRBComboBox(ReportAccountingWork)
        self.cmbSpetiality.setObjectName(_fromUtf8("cmbSpetiality"))
        self.gridLayout.addWidget(self.cmbSpetiality, 5, 1, 1, 2)
        self.lblEventPurpose = QtGui.QLabel(ReportAccountingWork)
        self.lblEventPurpose.setObjectName(_fromUtf8("lblEventPurpose"))
        self.gridLayout.addWidget(self.lblEventPurpose, 3, 0, 1, 1)
        self.cmbEventPurpose = CRBComboBox(ReportAccountingWork)
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.gridLayout.addWidget(self.cmbEventPurpose, 3, 1, 1, 2)
        self.chkDetailPerson = QtGui.QCheckBox(ReportAccountingWork)
        self.chkDetailPerson.setObjectName(_fromUtf8("chkDetailPerson"))
        self.gridLayout.addWidget(self.chkDetailPerson, 11, 0, 1, 3)
        self.cmbActionType = QtGui.QComboBox(ReportAccountingWork)
        self.cmbActionType.setObjectName(_fromUtf8("cmbActionType"))
        self.cmbActionType.addItem(_fromUtf8(""))
        self.cmbActionType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbActionType, 9, 1, 1, 2)
        self.lblActionType = QtGui.QLabel(ReportAccountingWork)
        self.lblActionType.setObjectName(_fromUtf8("lblActionType"))
        self.gridLayout.addWidget(self.lblActionType, 9, 0, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportAccountingWork)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAccountingWork.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAccountingWork.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAccountingWork)

    def retranslateUi(self, ReportAccountingWork):
        ReportAccountingWork.setWindowTitle(_translate("ReportAccountingWork", "Dialog", None))
        self.lblOrgStructure.setText(_translate("ReportAccountingWork", "Подразделение", None))
        self.lblPerson.setText(_translate("ReportAccountingWork", "Врач", None))
        self.lblEventType.setText(_translate("ReportAccountingWork", "Тип обращения", None))
        self.lblEndDate.setText(_translate("ReportAccountingWork", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportAccountingWork", "Дата &начала периода", None))
        self.chkGroup.setText(_translate("ReportAccountingWork", "По дате", None))
        self.lblSpeciality.setText(_translate("ReportAccountingWork", "Специальность", None))
        self.lblEventPurpose.setText(_translate("ReportAccountingWork", "Назначение обращения", None))
        self.chkDetailPerson.setText(_translate("ReportAccountingWork", "Детализировать по врачам", None))
        self.cmbActionType.setItemText(0, _translate("ReportAccountingWork", "з", None))
        self.cmbActionType.setItemText(1, _translate("ReportAccountingWork", "стх", None))
        self.lblActionType.setText(_translate("ReportAccountingWork", "Услуги типа:", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
