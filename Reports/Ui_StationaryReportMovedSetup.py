# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StationaryReportMovedSetup.ui'
#
# Created: Wed Jan 29 16:05:11 2014
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

class Ui_StationaryReportMovedSetupDialog(object):
    def setupUi(self, StationaryReportMovedSetupDialog):
        StationaryReportMovedSetupDialog.setObjectName(_fromUtf8("StationaryReportMovedSetupDialog"))
        StationaryReportMovedSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        StationaryReportMovedSetupDialog.resize(317, 215)
        StationaryReportMovedSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(StationaryReportMovedSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(StationaryReportMovedSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.lblMode = QtGui.QLabel(StationaryReportMovedSetupDialog)
        self.lblMode.setObjectName(_fromUtf8("lblMode"))
        self.gridLayout.addWidget(self.lblMode, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(StationaryReportMovedSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 3)
        self.cmbMode = QtGui.QComboBox(StationaryReportMovedSetupDialog)
        self.cmbMode.setObjectName(_fromUtf8("cmbMode"))
        self.cmbMode.addItem(_fromUtf8(""))
        self.cmbMode.addItem(_fromUtf8(""))
        self.cmbMode.addItem(_fromUtf8(""))
        self.cmbMode.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbMode, 1, 1, 2, 2)
        self.edtBegDate = QtGui.QDateEdit(StationaryReportMovedSetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(StationaryReportMovedSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 3, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(StationaryReportMovedSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 1, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(StationaryReportMovedSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StationaryReportMovedSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StationaryReportMovedSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StationaryReportMovedSetupDialog)
        StationaryReportMovedSetupDialog.setTabOrder(self.edtBegDate, self.buttonBox)

    def retranslateUi(self, StationaryReportMovedSetupDialog):
        StationaryReportMovedSetupDialog.setWindowTitle(_translate("StationaryReportMovedSetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("StationaryReportMovedSetupDialog", "Отчетная дата", None))
        self.lblMode.setText(_translate("StationaryReportMovedSetupDialog", "Используемый период", None))
        self.cmbMode.setItemText(0, _translate("StationaryReportMovedSetupDialog", "00.00 - 23.59", None))
        self.cmbMode.setItemText(1, _translate("StationaryReportMovedSetupDialog", "07.00 - 15.00", None))
        self.cmbMode.setItemText(2, _translate("StationaryReportMovedSetupDialog", "15.00 - 07.00", None))
        self.cmbMode.setItemText(3, _translate("StationaryReportMovedSetupDialog", "07.00 - 07.00", None))
        self.lblOrgStructure.setText(_translate("StationaryReportMovedSetupDialog", "&Подразделение", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
