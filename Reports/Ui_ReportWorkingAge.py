# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportWorkingAge.ui'
#
# Created: Tue Feb 18 18:50:37 2014
#      by: PyQt4 UI code generator 4.10
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

class Ui_ReportWorkingAge(object):
    def setupUi(self, ReportWorkingAge):
        ReportWorkingAge.setObjectName(_fromUtf8("ReportWorkingAge"))
        ReportWorkingAge.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportWorkingAge.resize(442, 179)
        ReportWorkingAge.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportWorkingAge)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblOrgStructure = QtGui.QLabel(ReportWorkingAge)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportWorkingAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportWorkingAge)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 5)
        self.cmbOrgStructure = COrgStructureComboBox(ReportWorkingAge)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 4)
        self.lblBegDate = QtGui.QLabel(ReportWorkingAge)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 2)
        self.edtEndDate = CDateEdit(ReportWorkingAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 3, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportWorkingAge)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.cmbAge = QtGui.QComboBox(ReportWorkingAge)
        self.cmbAge.setObjectName(_fromUtf8("cmbAge"))
        self.cmbAge.addItem(_fromUtf8(""))
        self.cmbAge.addItem(_fromUtf8(""))
        self.cmbAge.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbAge, 3, 1, 1, 4)
        self.label = QtGui.QLabel(ReportWorkingAge)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportWorkingAge)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportWorkingAge.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportWorkingAge.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportWorkingAge)
        ReportWorkingAge.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportWorkingAge.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        ReportWorkingAge.setTabOrder(self.cmbOrgStructure, self.buttonBox)

    def retranslateUi(self, ReportWorkingAge):
        ReportWorkingAge.setWindowTitle(_translate("ReportWorkingAge", "параметры отчёта", None))
        self.lblOrgStructure.setText(_translate("ReportWorkingAge", "&Подразделение", None))
        self.lblBegDate.setText(_translate("ReportWorkingAge", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportWorkingAge", "Дата &окончания периода", None))
        self.cmbAge.setItemText(0, _translate("ReportWorkingAge", "не задано", None))
        self.cmbAge.setItemText(1, _translate("ReportWorkingAge", "Трудоспособный", None))
        self.cmbAge.setItemText(2, _translate("ReportWorkingAge", "Нетрудоспособный", None))
        self.label.setText(_translate("ReportWorkingAge", "Возраст", None))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
