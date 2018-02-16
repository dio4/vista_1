# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPlanningAndEconomicIndicators.ui'
#
# Created: Fri Jul 31 15:26:22 2015
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

class Ui_ReportPlanningAndEconomicIndicators(object):
    def setupUi(self, ReportPlanningAndEconomicIndicators):
        ReportPlanningAndEconomicIndicators.setObjectName(_fromUtf8("ReportPlanningAndEconomicIndicators"))
        ReportPlanningAndEconomicIndicators.resize(430, 331)
        self.gridLayout = QtGui.QGridLayout(ReportPlanningAndEconomicIndicators)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtBegDate = CDateEdit(ReportPlanningAndEconomicIndicators)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportPlanningAndEconomicIndicators)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 2, 1, 1)
        self.chkGroupingOrgStructure = QtGui.QCheckBox(ReportPlanningAndEconomicIndicators)
        self.chkGroupingOrgStructure.setObjectName(_fromUtf8("chkGroupingOrgStructure"))
        self.gridLayout.addWidget(self.chkGroupingOrgStructure, 6, 0, 1, 3)
        self.lstItems = CRBListBox(ReportPlanningAndEconomicIndicators)
        self.lstItems.setObjectName(_fromUtf8("lstItems"))
        self.gridLayout.addWidget(self.lstItems, 4, 0, 1, 3)
        self.lblBegDate = QtGui.QLabel(ReportPlanningAndEconomicIndicators)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportPlanningAndEconomicIndicators)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lblFinanceType = QtGui.QLabel(ReportPlanningAndEconomicIndicators)
        self.lblFinanceType.setObjectName(_fromUtf8("lblFinanceType"))
        self.gridLayout.addWidget(self.lblFinanceType, 2, 0, 1, 1)
        self.label = QtGui.QLabel(ReportPlanningAndEconomicIndicators)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.cmbFinanceType = CRBComboBox(ReportPlanningAndEconomicIndicators)
        self.cmbFinanceType.setObjectName(_fromUtf8("cmbFinanceType"))
        self.gridLayout.addWidget(self.cmbFinanceType, 2, 1, 1, 2)
        self.edtEndDate = CDateEdit(ReportPlanningAndEconomicIndicators)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportPlanningAndEconomicIndicators)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 5, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportPlanningAndEconomicIndicators)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 5, 1, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportPlanningAndEconomicIndicators)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportPlanningAndEconomicIndicators.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportPlanningAndEconomicIndicators.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportPlanningAndEconomicIndicators)

    def retranslateUi(self, ReportPlanningAndEconomicIndicators):
        ReportPlanningAndEconomicIndicators.setWindowTitle(_translate("ReportPlanningAndEconomicIndicators", "Dialog", None))
        self.chkGroupingOrgStructure.setText(_translate("ReportPlanningAndEconomicIndicators", "группировать по отделениям", None))
        self.lblBegDate.setText(_translate("ReportPlanningAndEconomicIndicators", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportPlanningAndEconomicIndicators", "Дата окончания периода", None))
        self.lblFinanceType.setText(_translate("ReportPlanningAndEconomicIndicators", "Источник финансирования", None))
        self.label.setText(_translate("ReportPlanningAndEconomicIndicators", "Исключить типы обращений:", None))
        self.lblOrgStructure.setText(_translate("ReportPlanningAndEconomicIndicators", "Подразделение", None))

from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
from library.RBListBox import CRBListBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
