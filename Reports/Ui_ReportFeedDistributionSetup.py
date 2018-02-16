# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportFeedDistributionSetup.ui'
#
# Created: Wed Mar 04 17:05:19 2015
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

class Ui_ReportFeedDistributionSetup(object):
    def setupUi(self, ReportFeedDistributionSetup):
        ReportFeedDistributionSetup.setObjectName(_fromUtf8("ReportFeedDistributionSetup"))
        ReportFeedDistributionSetup.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportFeedDistributionSetup.resize(436, 192)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportFeedDistributionSetup.sizePolicy().hasHeightForWidth())
        ReportFeedDistributionSetup.setSizePolicy(sizePolicy)
        ReportFeedDistributionSetup.setSizeGripEnabled(True)
        ReportFeedDistributionSetup.setModal(True)
        self.gridLayout = QtGui.QGridLayout(ReportFeedDistributionSetup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportFeedDistributionSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 11, 0, 1, 5)
        spacerItem1 = QtGui.QSpacerItem(428, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 10, 0, 1, 5)
        self.lblFinance = QtGui.QLabel(ReportFeedDistributionSetup)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 7, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportFeedDistributionSetup)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 7, 1, 1, 4)
        self.edtBegDate = CDateEdit(ReportFeedDistributionSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.lblEventType = QtGui.QLabel(ReportFeedDistributionSetup)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 2, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 3, 1, 2)
        self.cmbEventType = CRBComboBox(ReportFeedDistributionSetup)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 2, 1, 1, 4)
        self.edtEndDate = CDateEdit(ReportFeedDistributionSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportFeedDistributionSetup)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportFeedDistributionSetup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportFeedDistributionSetup)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 8, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportFeedDistributionSetup)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 8, 1, 1, 4)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportFeedDistributionSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportFeedDistributionSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportFeedDistributionSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportFeedDistributionSetup)
        ReportFeedDistributionSetup.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportFeedDistributionSetup.setTabOrder(self.edtEndDate, self.cmbEventType)
        ReportFeedDistributionSetup.setTabOrder(self.cmbEventType, self.cmbFinance)
        ReportFeedDistributionSetup.setTabOrder(self.cmbFinance, self.buttonBox)

    def retranslateUi(self, ReportFeedDistributionSetup):
        ReportFeedDistributionSetup.setWindowTitle(_translate("ReportFeedDistributionSetup", "параметры отчёта", None))
        self.lblFinance.setText(_translate("ReportFeedDistributionSetup", "Тип финанисирования", None))
        self.lblEventType.setText(_translate("ReportFeedDistributionSetup", "&Тип обращения", None))
        self.lblBegDate.setText(_translate("ReportFeedDistributionSetup", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportFeedDistributionSetup", "Дата &окончания периода", None))
        self.lblOrgStructure.setText(_translate("ReportFeedDistributionSetup", "Подразделение", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
