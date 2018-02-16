# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportSearchUncorrectServiceEventsWithKSG.ui'
#
# Created: Fri May 29 15:42:48 2015
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

class Ui_ReportSearchUncorrectServiceEventsWithKSG(object):
    def setupUi(self, ReportSearchUncorrectServiceEventsWithKSG):
        ReportSearchUncorrectServiceEventsWithKSG.setObjectName(_fromUtf8("ReportSearchUncorrectServiceEventsWithKSG"))
        ReportSearchUncorrectServiceEventsWithKSG.resize(400, 209)
        self.formLayout = QtGui.QFormLayout(ReportSearchUncorrectServiceEventsWithKSG)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lblBegDate = QtGui.QLabel(ReportSearchUncorrectServiceEventsWithKSG)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lblBegDate)
        self.edtBegDate = CDateEdit(ReportSearchUncorrectServiceEventsWithKSG)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtBegDate)
        self.lblEndDate = QtGui.QLabel(ReportSearchUncorrectServiceEventsWithKSG)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lblEndDate)
        self.edtEndDate = CDateEdit(ReportSearchUncorrectServiceEventsWithKSG)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtEndDate)
        self.lblOrgStructure = QtGui.QLabel(ReportSearchUncorrectServiceEventsWithKSG)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.lblOrgStructure)
        self.cmbOrgStructure = COrgStructureComboBox(ReportSearchUncorrectServiceEventsWithKSG)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.cmbOrgStructure)
        self.lblPerson = QtGui.QLabel(ReportSearchUncorrectServiceEventsWithKSG)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.lblPerson)
        self.cmbPerson = CPersonComboBoxEx(ReportSearchUncorrectServiceEventsWithKSG)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.cmbPerson)
        self.lblFinance = QtGui.QLabel(ReportSearchUncorrectServiceEventsWithKSG)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.lblFinance)
        self.cmbFinance = CRBComboBox(ReportSearchUncorrectServiceEventsWithKSG)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.cmbFinance)
        self.label = QtGui.QLabel(ReportSearchUncorrectServiceEventsWithKSG)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.label)
        self.rb1 = QtGui.QRadioButton(ReportSearchUncorrectServiceEventsWithKSG)
        self.rb1.setText(_fromUtf8(""))
        self.rb1.setChecked(True)
        self.rb1.setObjectName(_fromUtf8("rb1"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.rb1)
        self.label_2 = QtGui.QLabel(ReportSearchUncorrectServiceEventsWithKSG)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.label_2)
        self.rb2 = QtGui.QRadioButton(ReportSearchUncorrectServiceEventsWithKSG)
        self.rb2.setText(_fromUtf8(""))
        self.rb2.setObjectName(_fromUtf8("rb2"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.rb2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportSearchUncorrectServiceEventsWithKSG)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.FieldRole, self.buttonBox)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportSearchUncorrectServiceEventsWithKSG)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportSearchUncorrectServiceEventsWithKSG.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportSearchUncorrectServiceEventsWithKSG.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportSearchUncorrectServiceEventsWithKSG)

    def retranslateUi(self, ReportSearchUncorrectServiceEventsWithKSG):
        ReportSearchUncorrectServiceEventsWithKSG.setWindowTitle(_translate("ReportSearchUncorrectServiceEventsWithKSG", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportSearchUncorrectServiceEventsWithKSG", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportSearchUncorrectServiceEventsWithKSG", "Дата &окончания периода", None))
        self.lblOrgStructure.setText(_translate("ReportSearchUncorrectServiceEventsWithKSG", "Подразделение", None))
        self.lblPerson.setText(_translate("ReportSearchUncorrectServiceEventsWithKSG", "Врач", None))
        self.lblFinance.setText(_translate("ReportSearchUncorrectServiceEventsWithKSG", "Тип финансирования", None))
        self.label.setText(_translate("ReportSearchUncorrectServiceEventsWithKSG", "По дате окончания лечения", None))
        self.label_2.setText(_translate("ReportSearchUncorrectServiceEventsWithKSG", "По расчетной дате реестра", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
