# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportMovingDispClients.ui'
#
# Created: Thu Jun 11 17:27:30 2015
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

class Ui_ReportMovingDispClients(object):
    def setupUi(self, ReportMovingDispClients):
        ReportMovingDispClients.setObjectName(_fromUtf8("ReportMovingDispClients"))
        ReportMovingDispClients.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportMovingDispClients.resize(425, 151)
        ReportMovingDispClients.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ReportMovingDispClients)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.edtEndDate = CDateEdit(ReportMovingDispClients)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridlayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportMovingDispClients)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridlayout.addWidget(self.cmbOrgStructure, 4, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 0, 2, 1, 1)
        self.cmbRowGrouping = QtGui.QComboBox(ReportMovingDispClients)
        self.cmbRowGrouping.setObjectName(_fromUtf8("cmbRowGrouping"))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbRowGrouping, 6, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportMovingDispClients)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 7, 0, 1, 3)
        self.lblEndDate = QtGui.QLabel(ReportMovingDispClients)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridlayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportMovingDispClients)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridlayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportMovingDispClients)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridlayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportMovingDispClients)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridlayout.addWidget(self.lblPerson, 5, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportMovingDispClients)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbPerson, 5, 1, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(ReportMovingDispClients)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridlayout.addWidget(self.lblOrgStructure, 4, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.lblRowGrouping = QtGui.QLabel(ReportMovingDispClients)
        self.lblRowGrouping.setObjectName(_fromUtf8("lblRowGrouping"))
        self.gridlayout.addWidget(self.lblRowGrouping, 6, 0, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblRowGrouping.setBuddy(self.cmbRowGrouping)

        self.retranslateUi(ReportMovingDispClients)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportMovingDispClients.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportMovingDispClients.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportMovingDispClients)
        ReportMovingDispClients.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportMovingDispClients.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        ReportMovingDispClients.setTabOrder(self.cmbOrgStructure, self.cmbPerson)
        ReportMovingDispClients.setTabOrder(self.cmbPerson, self.cmbRowGrouping)
        ReportMovingDispClients.setTabOrder(self.cmbRowGrouping, self.buttonBox)

    def retranslateUi(self, ReportMovingDispClients):
        ReportMovingDispClients.setWindowTitle(_translate("ReportMovingDispClients", "параметры отчёта", None))
        self.cmbRowGrouping.setItemText(0, _translate("ReportMovingDispClients", "Подразделениям", None))
        self.cmbRowGrouping.setItemText(1, _translate("ReportMovingDispClients", "Специальности", None))
        self.cmbRowGrouping.setItemText(2, _translate("ReportMovingDispClients", "Врачам", None))
        self.lblEndDate.setText(_translate("ReportMovingDispClients", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportMovingDispClients", "Дата &начала периода", None))
        self.lblPerson.setText(_translate("ReportMovingDispClients", "&Врач", None))
        self.cmbPerson.setItemText(0, _translate("ReportMovingDispClients", "Врач", None))
        self.lblOrgStructure.setText(_translate("ReportMovingDispClients", "&Подразделение", None))
        self.lblRowGrouping.setText(_translate("ReportMovingDispClients", "Группировать по", None))

from library.DateEdit import CDateEdit
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
