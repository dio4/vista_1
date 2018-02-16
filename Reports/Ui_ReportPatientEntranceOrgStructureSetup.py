# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPatientEntranceOrgStructureSetup.ui'
#
# Created: Thu Apr  2 21:46:07 2015
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

class Ui_PatientEntranceOrgStructureSetupDialog(object):
    def setupUi(self, PatientEntranceOrgStructureSetupDialog):
        PatientEntranceOrgStructureSetupDialog.setObjectName(_fromUtf8("PatientEntranceOrgStructureSetupDialog"))
        PatientEntranceOrgStructureSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PatientEntranceOrgStructureSetupDialog.resize(390, 233)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PatientEntranceOrgStructureSetupDialog.sizePolicy().hasHeightForWidth())
        PatientEntranceOrgStructureSetupDialog.setSizePolicy(sizePolicy)
        PatientEntranceOrgStructureSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(PatientEntranceOrgStructureSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEventType = QtGui.QLabel(PatientEntranceOrgStructureSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 4, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(PatientEntranceOrgStructureSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 1)
        self.lblFinanceType = QtGui.QLabel(PatientEntranceOrgStructureSetupDialog)
        self.lblFinanceType.setObjectName(_fromUtf8("lblFinanceType"))
        self.gridLayout.addWidget(self.lblFinanceType, 3, 0, 1, 1)
        self.edtBegDate = CDateEdit(PatientEntranceOrgStructureSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PatientEntranceOrgStructureSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 2)
        self.edtEndDate = CDateEdit(PatientEntranceOrgStructureSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(PatientEntranceOrgStructureSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(PatientEntranceOrgStructureSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 5, 0, 1, 1)
        self.edtBegTime = QtGui.QTimeEdit(PatientEntranceOrgStructureSetupDialog)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout.addWidget(self.edtBegTime, 1, 2, 1, 1)
        self.edtEndTime = QtGui.QTimeEdit(PatientEntranceOrgStructureSetupDialog)
        self.edtEndTime.setObjectName(_fromUtf8("edtEndTime"))
        self.gridLayout.addWidget(self.edtEndTime, 2, 2, 1, 1)
        self.cmbFinanceType = CRBComboBox(PatientEntranceOrgStructureSetupDialog)
        self.cmbFinanceType.setObjectName(_fromUtf8("cmbFinanceType"))
        self.gridLayout.addWidget(self.cmbFinanceType, 3, 1, 1, 2)
        self.cmbEventType = CRBComboBox(PatientEntranceOrgStructureSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 4, 1, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(PatientEntranceOrgStructureSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 5, 1, 1, 2)

        self.retranslateUi(PatientEntranceOrgStructureSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PatientEntranceOrgStructureSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PatientEntranceOrgStructureSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PatientEntranceOrgStructureSetupDialog)

    def retranslateUi(self, PatientEntranceOrgStructureSetupDialog):
        PatientEntranceOrgStructureSetupDialog.setWindowTitle(_translate("PatientEntranceOrgStructureSetupDialog", "параметры отчёта", None))
        self.lblEventType.setText(_translate("PatientEntranceOrgStructureSetupDialog", "Тип обращения", None))
        self.lblEndDate.setText(_translate("PatientEntranceOrgStructureSetupDialog", "Дата окончания периода", None))
        self.lblFinanceType.setText(_translate("PatientEntranceOrgStructureSetupDialog", "Тип финансирования", None))
        self.lblBegDate.setText(_translate("PatientEntranceOrgStructureSetupDialog", "Дата начала периода", None))
        self.lblOrgStructure.setText(_translate("PatientEntranceOrgStructureSetupDialog", "Подразделение", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
