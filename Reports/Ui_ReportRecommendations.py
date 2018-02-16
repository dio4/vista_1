# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportRecommendations.ui'
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

class Ui_ReportRecommendations(object):
    def setupUi(self, ReportRecommendations):
        ReportRecommendations.setObjectName(_fromUtf8("ReportRecommendations"))
        ReportRecommendations.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportRecommendations.resize(436, 193)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportRecommendations.sizePolicy().hasHeightForWidth())
        ReportRecommendations.setSizePolicy(sizePolicy)
        ReportRecommendations.setSizeGripEnabled(True)
        ReportRecommendations.setModal(True)
        self.gridLayout = QtGui.QGridLayout(ReportRecommendations)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(ReportRecommendations)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 3, 0, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportRecommendations)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 6, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportRecommendations)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 5, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(428, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 5)
        self.buttonBox = QtGui.QDialogButtonBox(ReportRecommendations)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 5)
        self.chkExtendedReport = QtGui.QCheckBox(ReportRecommendations)
        self.chkExtendedReport.setObjectName(_fromUtf8("chkExtendedReport"))
        self.gridLayout.addWidget(self.chkExtendedReport, 7, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportRecommendations)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 3, 2, 1, 1)
        self.lblBegDate_2 = QtGui.QLabel(ReportRecommendations)
        self.lblBegDate_2.setObjectName(_fromUtf8("lblBegDate_2"))
        self.gridLayout.addWidget(self.lblBegDate_2, 0, 0, 1, 3)
        self.edtBegDate = CDateEdit(ReportRecommendations)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 2, 2, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportRecommendations)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 2, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 3, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 3, 1, 1)
        self.lblContract = QtGui.QLabel(ReportRecommendations)
        self.lblContract.setObjectName(_fromUtf8("lblContract"))
        self.gridLayout.addWidget(self.lblContract, 4, 0, 1, 1)
        self.cmbContract = CContractComboBox(ReportRecommendations)
        self.cmbContract.setObjectName(_fromUtf8("cmbContract"))
        self.gridLayout.addWidget(self.cmbContract, 4, 2, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(ReportRecommendations)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 5, 2, 1, 2)
        self.cmbEventType = CRBComboBox(ReportRecommendations)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 6, 2, 1, 2)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblBegDate_2.setBuddy(self.edtBegDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportRecommendations)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportRecommendations.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportRecommendations.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportRecommendations)

    def retranslateUi(self, ReportRecommendations):
        ReportRecommendations.setWindowTitle(_translate("ReportRecommendations", "параметры отчёта", None))
        self.lblEndDate.setText(_translate("ReportRecommendations", "по", None))
        self.lblEventType.setText(_translate("ReportRecommendations", "&Тип обращения", None))
        self.lblOrgStructure.setText(_translate("ReportRecommendations", "Подразделение направителя", None))
        self.chkExtendedReport.setText(_translate("ReportRecommendations", "Подробный отчет", None))
        self.lblBegDate_2.setText(_translate("ReportRecommendations", "Дата выдачи направления:", None))
        self.lblBegDate.setText(_translate("ReportRecommendations", "с", None))
        self.lblContract.setText(_translate("ReportRecommendations", "Договор", None))

from Accounting.ContractComboBox import CContractComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
