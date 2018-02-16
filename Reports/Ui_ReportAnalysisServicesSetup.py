# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportAnalysisServicesSetup.ui'
#
# Created: Thu Oct 15 19:20:07 2015
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

class Ui_ReportAnalysisServicesSetupDialog(object):
    def setupUi(self, ReportAnalysisServicesSetupDialog):
        ReportAnalysisServicesSetupDialog.setObjectName(_fromUtf8("ReportAnalysisServicesSetupDialog"))
        ReportAnalysisServicesSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportAnalysisServicesSetupDialog.resize(390, 223)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportAnalysisServicesSetupDialog.sizePolicy().hasHeightForWidth())
        ReportAnalysisServicesSetupDialog.setSizePolicy(sizePolicy)
        ReportAnalysisServicesSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportAnalysisServicesSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEventType = QtGui.QLabel(ReportAnalysisServicesSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 5, 0, 1, 1)
        self.rbtnByFormingAccountDate = QtGui.QRadioButton(ReportAnalysisServicesSetupDialog)
        self.rbtnByFormingAccountDate.setChecked(True)
        self.rbtnByFormingAccountDate.setObjectName(_fromUtf8("rbtnByFormingAccountDate"))
        self.gridLayout.addWidget(self.rbtnByFormingAccountDate, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAnalysisServicesSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 11, 0, 1, 2)
        self.rbtnByActionEndDate = QtGui.QRadioButton(ReportAnalysisServicesSetupDialog)
        self.rbtnByActionEndDate.setObjectName(_fromUtf8("rbtnByActionEndDate"))
        self.gridLayout.addWidget(self.rbtnByActionEndDate, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 10, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportAnalysisServicesSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 2, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportAnalysisServicesSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 2, 1, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(ReportAnalysisServicesSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 3, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportAnalysisServicesSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 3, 0, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportAnalysisServicesSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 7, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportAnalysisServicesSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 5, 1, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportAnalysisServicesSetupDialog)
        self.cmbPerson.setEnabled(True)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 7, 1, 1, 1)
        self.chkIsActionPayed = QtGui.QCheckBox(ReportAnalysisServicesSetupDialog)
        self.chkIsActionPayed.setObjectName(_fromUtf8("chkIsActionPayed"))
        self.gridLayout.addWidget(self.chkIsActionPayed, 9, 0, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(ReportAnalysisServicesSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 6, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportAnalysisServicesSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 6, 1, 1, 1)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblPerson.setBuddy(self.cmbPerson)

        self.retranslateUi(ReportAnalysisServicesSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAnalysisServicesSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAnalysisServicesSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAnalysisServicesSetupDialog)

    def retranslateUi(self, ReportAnalysisServicesSetupDialog):
        ReportAnalysisServicesSetupDialog.setWindowTitle(_translate("ReportAnalysisServicesSetupDialog", "параметры отчёта", None))
        self.lblEventType.setText(_translate("ReportAnalysisServicesSetupDialog", "&Тип обращения", None))
        self.rbtnByFormingAccountDate.setText(_translate("ReportAnalysisServicesSetupDialog", "формирования счета", None))
        self.rbtnByActionEndDate.setText(_translate("ReportAnalysisServicesSetupDialog", "выполнения услуги", None))
        self.lblBegDate.setText(_translate("ReportAnalysisServicesSetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportAnalysisServicesSetupDialog", "Дата окончания периода", None))
        self.lblPerson.setText(_translate("ReportAnalysisServicesSetupDialog", "&Врач", None))
        self.cmbEventType.setWhatsThis(_translate("ReportAnalysisServicesSetupDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.chkIsActionPayed.setText(_translate("ReportAnalysisServicesSetupDialog", "Учитывать только оплаченные услуги", None))
        self.lblOrgStructure.setText(_translate("ReportAnalysisServicesSetupDialog", "Подразделение", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
