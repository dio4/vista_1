# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ReportAnalizeBillOnDirectionsSetup.ui'
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

class Ui_ReportAnalizeBillOnDirectionSetup(object):
    def setupUi(self, ReportAnalizeBillOnDirectionSetup):
        ReportAnalizeBillOnDirectionSetup.setObjectName(_fromUtf8("ReportAnalizeBillOnDirectionSetup"))
        ReportAnalizeBillOnDirectionSetup.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportAnalizeBillOnDirectionSetup.resize(283, 181)
        ReportAnalizeBillOnDirectionSetup.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportAnalizeBillOnDirectionSetup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtEndDate = CDateEdit(ReportAnalizeBillOnDirectionSetup)
        self.edtEndDate.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportAnalizeBillOnDirectionSetup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportAnalizeBillOnDirectionSetup)
        self.edtBegDate.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportAnalizeBillOnDirectionSetup)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 6, 0, 1, 1)
        self.cmbPerson = CPersonComboBox(ReportAnalizeBillOnDirectionSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbPerson.sizePolicy().hasHeightForWidth())
        self.cmbPerson.setSizePolicy(sizePolicy)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 7, 1, 1, 2)
        self.lblBegDae = QtGui.QLabel(ReportAnalizeBillOnDirectionSetup)
        self.lblBegDae.setObjectName(_fromUtf8("lblBegDae"))
        self.gridLayout.addWidget(self.lblBegDae, 0, 0, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportAnalizeBillOnDirectionSetup)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 7, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAnalizeBillOnDirectionSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 11, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(21, 21, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportAnalizeBillOnDirectionSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbEventType.sizePolicy().hasHeightForWidth())
        self.cmbEventType.setSizePolicy(sizePolicy)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 6, 1, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(ReportAnalizeBillOnDirectionSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbOrgStructure.sizePolicy().hasHeightForWidth())
        self.cmbOrgStructure.setSizePolicy(sizePolicy)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(19, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)
        self.lblSubdivision = QtGui.QLabel(ReportAnalizeBillOnDirectionSetup)
        self.lblSubdivision.setObjectName(_fromUtf8("lblSubdivision"))
        self.gridLayout.addWidget(self.lblSubdivision, 3, 0, 1, 1)
        self.label = QtGui.QLabel(ReportAnalizeBillOnDirectionSetup)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 8, 0, 1, 1)
        self.cmbContract = CContractComboBox(ReportAnalizeBillOnDirectionSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbContract.sizePolicy().hasHeightForWidth())
        self.cmbContract.setSizePolicy(sizePolicy)
        self.cmbContract.setObjectName(_fromUtf8("cmbContract"))
        self.gridLayout.addWidget(self.cmbContract, 8, 1, 1, 2)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblBegDae.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportAnalizeBillOnDirectionSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAnalizeBillOnDirectionSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAnalizeBillOnDirectionSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAnalizeBillOnDirectionSetup)
        ReportAnalizeBillOnDirectionSetup.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportAnalizeBillOnDirectionSetup.setTabOrder(self.edtEndDate, self.buttonBox)

    def retranslateUi(self, ReportAnalizeBillOnDirectionSetup):
        ReportAnalizeBillOnDirectionSetup.setWindowTitle(_translate("ReportAnalizeBillOnDirectionSetup", "параметры отчёта", None))
        self.lblEndDate.setText(_translate("ReportAnalizeBillOnDirectionSetup", "Дата окончания", None))
        self.lblEventType.setText(_translate("ReportAnalizeBillOnDirectionSetup", "&Тип обращения", None))
        self.lblBegDae.setText(_translate("ReportAnalizeBillOnDirectionSetup", "Дата начала", None))
        self.lblPerson.setText(_translate("ReportAnalizeBillOnDirectionSetup", "Врач", None))
        self.cmbEventType.setWhatsThis(_translate("ReportAnalizeBillOnDirectionSetup", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.lblSubdivision.setText(_translate("ReportAnalizeBillOnDirectionSetup", "Подразделение", None))
        self.label.setText(_translate("ReportAnalizeBillOnDirectionSetup", "Договор", None))

from Accounting.ContractComboBox import CContractComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.PersonComboBox import CPersonComboBox
from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
