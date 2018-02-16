# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportBasicIndicatorsSetup.ui'
#
# Created: Wed Sep 17 18:07:06 2014
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

class Ui_ReportBasicIndicatorsSetupDialog(object):
    def setupUi(self, ReportBasicIndicatorsSetupDialog):
        ReportBasicIndicatorsSetupDialog.setObjectName(_fromUtf8("ReportBasicIndicatorsSetupDialog"))
        ReportBasicIndicatorsSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportBasicIndicatorsSetupDialog.resize(323, 200)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportBasicIndicatorsSetupDialog.sizePolicy().hasHeightForWidth())
        ReportBasicIndicatorsSetupDialog.setSizePolicy(sizePolicy)
        ReportBasicIndicatorsSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportBasicIndicatorsSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportBasicIndicatorsSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportBasicIndicatorsSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportBasicIndicatorsSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportBasicIndicatorsSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportBasicIndicatorsSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 3, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportBasicIndicatorsSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 3, 1, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportBasicIndicatorsSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 5, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportBasicIndicatorsSetupDialog)
        self.cmbPerson.setEnabled(True)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 5, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportBasicIndicatorsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)
        self.chkGroupByProfile = QtGui.QCheckBox(ReportBasicIndicatorsSetupDialog)
        self.chkGroupByProfile.setObjectName(_fromUtf8("chkGroupByProfile"))
        self.gridLayout.addWidget(self.chkGroupByProfile, 7, 0, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(ReportBasicIndicatorsSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 4, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportBasicIndicatorsSetupDialog)
        self.cmbOrgStructure.setEnabled(True)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 4, 1, 1, 1)
        self.lblEventPurpose = QtGui.QLabel(ReportBasicIndicatorsSetupDialog)
        self.lblEventPurpose.setObjectName(_fromUtf8("lblEventPurpose"))
        self.gridLayout.addWidget(self.lblEventPurpose, 2, 0, 1, 1)
        self.cmbEventPurpose = CRBComboBox(ReportBasicIndicatorsSetupDialog)
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.gridLayout.addWidget(self.cmbEventPurpose, 2, 1, 1, 1)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblEventPurpose.setBuddy(self.cmbEventPurpose)

        self.retranslateUi(ReportBasicIndicatorsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportBasicIndicatorsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportBasicIndicatorsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportBasicIndicatorsSetupDialog)

    def retranslateUi(self, ReportBasicIndicatorsSetupDialog):
        ReportBasicIndicatorsSetupDialog.setWindowTitle(_translate("ReportBasicIndicatorsSetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportBasicIndicatorsSetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportBasicIndicatorsSetupDialog", "Дата окончания периода", None))
        self.lblEventType.setText(_translate("ReportBasicIndicatorsSetupDialog", "&Тип обращения", None))
        self.cmbEventType.setWhatsThis(_translate("ReportBasicIndicatorsSetupDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.lblPerson.setText(_translate("ReportBasicIndicatorsSetupDialog", "&Врач", None))
        self.chkGroupByProfile.setText(_translate("ReportBasicIndicatorsSetupDialog", "Группировать по профилям", None))
        self.lblOrgStructure.setText(_translate("ReportBasicIndicatorsSetupDialog", "Подразделение", None))
        self.lblEventPurpose.setText(_translate("ReportBasicIndicatorsSetupDialog", "&Назначение обращения", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
