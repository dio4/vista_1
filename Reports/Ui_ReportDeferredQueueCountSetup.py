# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportDeferredQueueCountSetup.ui'
#
# Created: Tue Jun 24 19:11:00 2014
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

class Ui_ReportDeferredQueueCountSetupDialog(object):
    def setupUi(self, ReportDeferredQueueCountSetupDialog):
        ReportDeferredQueueCountSetupDialog.setObjectName(_fromUtf8("ReportDeferredQueueCountSetupDialog"))
        ReportDeferredQueueCountSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportDeferredQueueCountSetupDialog.resize(243, 107)
        ReportDeferredQueueCountSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportDeferredQueueCountSetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 3, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportDeferredQueueCountSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 5)
        self.lblEndDate = QtGui.QLabel(ReportDeferredQueueCountSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportDeferredQueueCountSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 3, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportDeferredQueueCountSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportDeferredQueueCountSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(ReportDeferredQueueCountSetupDialog)
        self.cmbOrgStructure.setEnabled(True)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 4, 0, 1, 4)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportDeferredQueueCountSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportDeferredQueueCountSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportDeferredQueueCountSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportDeferredQueueCountSetupDialog)
        ReportDeferredQueueCountSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportDeferredQueueCountSetupDialog.setTabOrder(self.edtEndDate, self.buttonBox)

    def retranslateUi(self, ReportDeferredQueueCountSetupDialog):
        ReportDeferredQueueCountSetupDialog.setWindowTitle(_translate("ReportDeferredQueueCountSetupDialog", "параметры отчёта", None))
        self.lblEndDate.setText(_translate("ReportDeferredQueueCountSetupDialog", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportDeferredQueueCountSetupDialog", "Дата &начала периода", None))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
