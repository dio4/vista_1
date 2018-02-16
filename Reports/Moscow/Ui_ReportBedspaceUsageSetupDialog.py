# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportBedspaceUsageSetupDialog.ui'
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

class Ui_ReportBedspaceUsageSetupDialog(object):
    def setupUi(self, ReportBedspaceUsageSetupDialog):
        ReportBedspaceUsageSetupDialog.setObjectName(_fromUtf8("ReportBedspaceUsageSetupDialog"))
        ReportBedspaceUsageSetupDialog.resize(450, 250)
        self.gridLayout = QtGui.QGridLayout(ReportBedspaceUsageSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtEndDate = CDateEdit(ReportBedspaceUsageSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportBedspaceUsageSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 4)
        self.lblBegDate = QtGui.QLabel(ReportBedspaceUsageSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.chkShowPrevYear = QtGui.QCheckBox(ReportBedspaceUsageSetupDialog)
        self.chkShowPrevYear.setObjectName(_fromUtf8("chkShowPrevYear"))
        self.gridLayout.addWidget(self.chkShowPrevYear, 2, 0, 1, 4)
        spacerItem = QtGui.QSpacerItem(218, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportBedspaceUsageSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 3, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportBedspaceUsageSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportBedspaceUsageSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.edtBegTime = CTimeEdit(ReportBedspaceUsageSetupDialog)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout.addWidget(self.edtBegTime, 0, 2, 1, 1)
        self.edtEndTime = CTimeEdit(ReportBedspaceUsageSetupDialog)
        self.edtEndTime.setObjectName(_fromUtf8("edtEndTime"))
        self.gridLayout.addWidget(self.edtEndTime, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 4, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportBedspaceUsageSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 1, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportBedspaceUsageSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportBedspaceUsageSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportBedspaceUsageSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportBedspaceUsageSetupDialog)
        ReportBedspaceUsageSetupDialog.setTabOrder(self.edtBegDate, self.edtBegTime)
        ReportBedspaceUsageSetupDialog.setTabOrder(self.edtBegTime, self.edtEndDate)
        ReportBedspaceUsageSetupDialog.setTabOrder(self.edtEndDate, self.edtEndTime)
        ReportBedspaceUsageSetupDialog.setTabOrder(self.edtEndTime, self.chkShowPrevYear)
        ReportBedspaceUsageSetupDialog.setTabOrder(self.chkShowPrevYear, self.cmbOrgStructure)
        ReportBedspaceUsageSetupDialog.setTabOrder(self.cmbOrgStructure, self.buttonBox)

    def retranslateUi(self, ReportBedspaceUsageSetupDialog):
        ReportBedspaceUsageSetupDialog.setWindowTitle(_translate("ReportBedspaceUsageSetupDialog", "Dialog", None))
        self.edtEndDate.setDisplayFormat(_translate("ReportBedspaceUsageSetupDialog", "dd.MM.yyyy", None))
        self.lblBegDate.setText(_translate("ReportBedspaceUsageSetupDialog", "Дата &начала периода", None))
        self.chkShowPrevYear.setText(_translate("ReportBedspaceUsageSetupDialog", "Добавить данные за предыдущий год", None))
        self.lblOrgStructure.setText(_translate("ReportBedspaceUsageSetupDialog", "&Подразделение", None))
        self.lblEndDate.setText(_translate("ReportBedspaceUsageSetupDialog", "Дата &окончания периода", None))
        self.edtBegDate.setDisplayFormat(_translate("ReportBedspaceUsageSetupDialog", "dd.MM.yyyy", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from library.TimeEdit import CTimeEdit
