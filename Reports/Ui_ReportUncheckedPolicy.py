# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportUncheckedPolicy.ui'
#
# Created: Mon Jul 21 15:45:20 2014
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

class Ui_ReportUncheckedPolicy(object):
    def setupUi(self, ReportUncheckedPolicy):
        ReportUncheckedPolicy.setObjectName(_fromUtf8("ReportUncheckedPolicy"))
        ReportUncheckedPolicy.resize(400, 128)
        self.gridLayout = QtGui.QGridLayout(ReportUncheckedPolicy)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportUncheckedPolicy)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.edtBegDate = CDateEdit(ReportUncheckedPolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportUncheckedPolicy)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        self.edtEndDate = CDateEdit(ReportUncheckedPolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 1)
        self.lblOrgStrucutreAttachType = QtGui.QLabel(ReportUncheckedPolicy)
        self.lblOrgStrucutreAttachType.setObjectName(_fromUtf8("lblOrgStrucutreAttachType"))
        self.gridLayout.addWidget(self.lblOrgStrucutreAttachType, 2, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportUncheckedPolicy)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportUncheckedPolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportUncheckedPolicy)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportUncheckedPolicy.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportUncheckedPolicy.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportUncheckedPolicy)

    def retranslateUi(self, ReportUncheckedPolicy):
        ReportUncheckedPolicy.setWindowTitle(_translate("ReportUncheckedPolicy", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportUncheckedPolicy", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportUncheckedPolicy", "Дата окончания периода", None))
        self.lblOrgStrucutreAttachType.setText(_translate("ReportUncheckedPolicy", "Подразделение", None))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
