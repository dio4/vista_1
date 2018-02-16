# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPatientsAtHome.ui'
#
# Created: Fri Feb  7 18:48:00 2014
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

class Ui_ReportPatientAtHome(object):
    def setupUi(self, ReportPatientAtHome):
        ReportPatientAtHome.setObjectName(_fromUtf8("ReportPatientAtHome"))
        ReportPatientAtHome.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportPatientAtHome.resize(418, 251)
        ReportPatientAtHome.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ReportPatientAtHome)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblBegDate = QtGui.QLabel(ReportPatientAtHome)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridlayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportPatientAtHome)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridlayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportPatientAtHome)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridlayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportPatientAtHome)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridlayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportPatientAtHome)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridlayout.addWidget(self.lblOrgStructure, 6, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportPatientAtHome)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridlayout.addWidget(self.cmbOrgStructure, 6, 1, 1, 2)
        self.lblPerson = QtGui.QLabel(ReportPatientAtHome)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridlayout.addWidget(self.lblPerson, 7, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportPatientAtHome)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbPerson, 7, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportPatientAtHome)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 11, 0, 1, 3)
        self.lblRowGrouping = QtGui.QLabel(ReportPatientAtHome)
        self.lblRowGrouping.setObjectName(_fromUtf8("lblRowGrouping"))
        self.gridlayout.addWidget(self.lblRowGrouping, 9, 0, 1, 1)
        self.cmbRowGrouping = QtGui.QComboBox(ReportPatientAtHome)
        self.cmbRowGrouping.setObjectName(_fromUtf8("cmbRowGrouping"))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbRowGrouping, 9, 1, 1, 2)
        self.lblSex = QtGui.QLabel(ReportPatientAtHome)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridlayout.addWidget(self.lblSex, 8, 0, 1, 1)
        self.cmbSex = QtGui.QComboBox(ReportPatientAtHome)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSex.sizePolicy().hasHeightForWidth())
        self.cmbSex.setSizePolicy(sizePolicy)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbSex, 8, 1, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblRowGrouping.setBuddy(self.cmbRowGrouping)
        self.lblSex.setBuddy(self.cmbSex)

        self.retranslateUi(ReportPatientAtHome)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportPatientAtHome.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportPatientAtHome.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportPatientAtHome)
        ReportPatientAtHome.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportPatientAtHome.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        ReportPatientAtHome.setTabOrder(self.cmbOrgStructure, self.cmbPerson)
        ReportPatientAtHome.setTabOrder(self.cmbPerson, self.cmbSex)
        ReportPatientAtHome.setTabOrder(self.cmbSex, self.cmbRowGrouping)
        ReportPatientAtHome.setTabOrder(self.cmbRowGrouping, self.buttonBox)

    def retranslateUi(self, ReportPatientAtHome):
        ReportPatientAtHome.setWindowTitle(_translate("ReportPatientAtHome", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportPatientAtHome", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportPatientAtHome", "Дата &окончания периода", None))
        self.lblOrgStructure.setText(_translate("ReportPatientAtHome", "&Подразделение", None))
        self.lblPerson.setText(_translate("ReportPatientAtHome", "&Врач", None))
        self.cmbPerson.setItemText(0, _translate("ReportPatientAtHome", "Врач", None))
        self.lblRowGrouping.setText(_translate("ReportPatientAtHome", "&Строки по", None))
        self.cmbRowGrouping.setItemText(0, _translate("ReportPatientAtHome", "Датам", None))
        self.cmbRowGrouping.setItemText(1, _translate("ReportPatientAtHome", "Врачам", None))
        self.cmbRowGrouping.setItemText(2, _translate("ReportPatientAtHome", "Подразделениям", None))
        self.cmbRowGrouping.setItemText(3, _translate("ReportPatientAtHome", "Специальности", None))
        self.cmbRowGrouping.setItemText(4, _translate("ReportPatientAtHome", "Должности", None))
        self.lblSex.setText(_translate("ReportPatientAtHome", "По&л", None))
        self.cmbSex.setItemText(1, _translate("ReportPatientAtHome", "М", None))
        self.cmbSex.setItemText(2, _translate("ReportPatientAtHome", "Ж", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
