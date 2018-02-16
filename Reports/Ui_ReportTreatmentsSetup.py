# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\ReportTreatmentsSetup.ui'
#
# Created: Fri Jun 15 12:17:52 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportTreatmentsSetupDialog(object):
    def setupUi(self, ReportTreatmentsSetupDialog):
        ReportTreatmentsSetupDialog.setObjectName(_fromUtf8("ReportTreatmentsSetupDialog"))
        ReportTreatmentsSetupDialog.resize(370, 336)
        self.gridLayout = QtGui.QGridLayout(ReportTreatmentsSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportTreatmentsSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportTreatmentsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 3)
        self.lblEventType = QtGui.QLabel(ReportTreatmentsSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 4, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportTreatmentsSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 4, 1, 1, 3)
        self.lblFinance = QtGui.QLabel(ReportTreatmentsSetupDialog)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 5, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportTreatmentsSetupDialog)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 5, 1, 1, 3)
        self.lblOrgStructure = QtGui.QLabel(ReportTreatmentsSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 6, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportTreatmentsSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 6, 1, 1, 3)
        self.lblPerson = QtGui.QLabel(ReportTreatmentsSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 7, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportTreatmentsSetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 7, 1, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ReportTreatmentsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 4)
        self.edtEndDate = CDateEdit(ReportTreatmentsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 3)
        self.lblEndDate = QtGui.QLabel(ReportTreatmentsSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 0, 1, 4)
        self.lblPurpose = QtGui.QLabel(ReportTreatmentsSetupDialog)
        self.lblPurpose.setObjectName(_fromUtf8("lblPurpose"))
        self.gridLayout.addWidget(self.lblPurpose, 2, 0, 1, 1)
        self.cmbPurpose = CRBComboBox(ReportTreatmentsSetupDialog)
        self.cmbPurpose.setObjectName(_fromUtf8("cmbPurpose"))
        self.gridLayout.addWidget(self.cmbPurpose, 2, 1, 1, 3)
        self.lblMedicalAidType = QtGui.QLabel(ReportTreatmentsSetupDialog)
        self.lblMedicalAidType.setObjectName(_fromUtf8("lblMedicalAidType"))
        self.gridLayout.addWidget(self.lblMedicalAidType, 3, 0, 1, 1)
        self.cmbMedicalAidType = CRBComboBox(ReportTreatmentsSetupDialog)
        self.cmbMedicalAidType.setObjectName(_fromUtf8("cmbMedicalAidType"))
        self.gridLayout.addWidget(self.cmbMedicalAidType, 3, 1, 1, 3)
        self.lblTariffing = QtGui.QLabel(ReportTreatmentsSetupDialog)
        self.lblTariffing.setObjectName(_fromUtf8("lblTariffing"))
        self.gridLayout.addWidget(self.lblTariffing, 8, 0, 1, 1)
        self.cmbTariffing = QtGui.QComboBox(ReportTreatmentsSetupDialog)
        self.cmbTariffing.setObjectName(_fromUtf8("cmbTariffing"))
        self.cmbTariffing.addItem(_fromUtf8(""))
        self.cmbTariffing.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbTariffing, 8, 1, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportTreatmentsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportTreatmentsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportTreatmentsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportTreatmentsSetupDialog)
        ReportTreatmentsSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportTreatmentsSetupDialog.setTabOrder(self.edtEndDate, self.cmbPurpose)
        ReportTreatmentsSetupDialog.setTabOrder(self.cmbPurpose, self.cmbMedicalAidType)
        ReportTreatmentsSetupDialog.setTabOrder(self.cmbMedicalAidType, self.cmbEventType)
        ReportTreatmentsSetupDialog.setTabOrder(self.cmbEventType, self.cmbFinance)
        ReportTreatmentsSetupDialog.setTabOrder(self.cmbFinance, self.cmbOrgStructure)
        ReportTreatmentsSetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbPerson)
        ReportTreatmentsSetupDialog.setTabOrder(self.cmbPerson, self.cmbTariffing)
        ReportTreatmentsSetupDialog.setTabOrder(self.cmbTariffing, self.buttonBox)

    def retranslateUi(self, ReportTreatmentsSetupDialog):
        ReportTreatmentsSetupDialog.setWindowTitle(QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "Дата &начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventType.setText(QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "&Тип обращения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFinance.setText(QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "Тип финанисирования", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPerson.setText(QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "Дата &окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPurpose.setText(QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "Назначение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMedicalAidType.setText(QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "Тип помощи", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTariffing.setText(QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "Тарификация", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbTariffing.setItemText(0, QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "Не учитывать", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbTariffing.setItemText(1, QtGui.QApplication.translate("ReportTreatmentsSetupDialog", "Учитывать", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportTreatmentsSetupDialog = QtGui.QDialog()
    ui = Ui_ReportTreatmentsSetupDialog()
    ui.setupUi(ReportTreatmentsSetupDialog)
    ReportTreatmentsSetupDialog.show()
    sys.exit(app.exec_())

