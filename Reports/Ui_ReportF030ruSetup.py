# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportF030ruSetup.ui'
#
# Created: Fri Jan  1 19:20:54 2016
#      by: PyQt4 UI code generator 4.11.1
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

class Ui_ReportF030ruSetup(object):
    def setupUi(self, ReportF030ruSetup):
        ReportF030ruSetup.setObjectName(_fromUtf8("ReportF030ruSetup"))
        ReportF030ruSetup.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportF030ruSetup.resize(483, 209)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportF030ruSetup.sizePolicy().hasHeightForWidth())
        ReportF030ruSetup.setSizePolicy(sizePolicy)
        ReportF030ruSetup.setSizeGripEnabled(True)
        ReportF030ruSetup.setModal(True)
        self.gridLayout = QtGui.QGridLayout(ReportF030ruSetup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(ReportF030ruSetup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 3, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportF030ruSetup)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 7, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportF030ruSetup)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 7, 1, 1, 4)
        spacerItem = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 2)
        self.edtBegDate = CDateEdit(ReportF030ruSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 1, 1, 2)
        self.edtEndDate = CDateEdit(ReportF030ruSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 3, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 3, 3, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportF030ruSetup)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 1, 0, 1, 1)
        self.lblBegDate_2 = QtGui.QLabel(ReportF030ruSetup)
        self.lblBegDate_2.setObjectName(_fromUtf8("lblBegDate_2"))
        self.gridLayout.addWidget(self.lblBegDate_2, 0, 0, 1, 3)
        self.lblFinance = QtGui.QLabel(ReportF030ruSetup)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 4, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportF030ruSetup)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 4, 1, 1, 4)
        self.lblOrgStructure_2 = QtGui.QLabel(ReportF030ruSetup)
        self.lblOrgStructure_2.setObjectName(_fromUtf8("lblOrgStructure_2"))
        self.gridLayout.addWidget(self.lblOrgStructure_2, 8, 0, 1, 1)
        self.cmbRecipeStatus = CRecipeStatusComboBox(ReportF030ruSetup)
        self.cmbRecipeStatus.setObjectName(_fromUtf8("cmbRecipeStatus"))
        self.gridLayout.addWidget(self.cmbRecipeStatus, 8, 1, 1, 4)
        self.btnOk = QtGui.QPushButton(ReportF030ruSetup)
        self.btnOk.setObjectName(_fromUtf8("btnOk"))
        self.gridLayout.addWidget(self.btnOk, 10, 4, 1, 1)
        self.btnCancel = QtGui.QPushButton(ReportF030ruSetup)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridLayout.addWidget(self.btnCancel, 10, 3, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 9, 0, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblBegDate_2.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportF030ruSetup)
        QtCore.QObject.connect(self.btnCancel, QtCore.SIGNAL(_fromUtf8("clicked()")), ReportF030ruSetup.reject)
        QtCore.QObject.connect(self.btnOk, QtCore.SIGNAL(_fromUtf8("clicked()")), ReportF030ruSetup.accept)
        QtCore.QMetaObject.connectSlotsByName(ReportF030ruSetup)
        ReportF030ruSetup.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportF030ruSetup.setTabOrder(self.edtEndDate, self.cmbFinance)
        ReportF030ruSetup.setTabOrder(self.cmbFinance, self.cmbOrgStructure)
        ReportF030ruSetup.setTabOrder(self.cmbOrgStructure, self.cmbRecipeStatus)
        ReportF030ruSetup.setTabOrder(self.cmbRecipeStatus, self.btnOk)
        ReportF030ruSetup.setTabOrder(self.btnOk, self.btnCancel)

    def retranslateUi(self, ReportF030ruSetup):
        ReportF030ruSetup.setWindowTitle(_translate("ReportF030ruSetup", "параметры отчёта", None))
        self.lblEndDate.setText(_translate("ReportF030ruSetup", "по", None))
        self.lblOrgStructure.setText(_translate("ReportF030ruSetup", "Подразделение", None))
        self.lblBegDate.setText(_translate("ReportF030ruSetup", "с", None))
        self.lblBegDate_2.setText(_translate("ReportF030ruSetup", "Дата выписки рецепта:", None))
        self.lblFinance.setText(_translate("ReportF030ruSetup", "Источник финансирования", None))
        self.lblOrgStructure_2.setText(_translate("ReportF030ruSetup", "Статус рецепта", None))
        self.btnOk.setText(_translate("ReportF030ruSetup", "ОК", None))
        self.btnCancel.setText(_translate("ReportF030ruSetup", "Отмена", None))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Reports.ComboBoxes import CRecipeStatusComboBox
from library.crbcombobox import CRBComboBox
