# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportSurgicalIndicators.ui'
#
# Created: Thu Jun 11 15:03:12 2015
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

class Ui_ReportSurgicalIndicators(object):
    def setupUi(self, ReportSurgicalIndicators):
        ReportSurgicalIndicators.setObjectName(_fromUtf8("ReportSurgicalIndicators"))
        ReportSurgicalIndicators.resize(498, 640)
        self.gridLayout = QtGui.QGridLayout(ReportSurgicalIndicators)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkOrgStructure = QtGui.QCheckBox(ReportSurgicalIndicators)
        self.chkOrgStructure.setObjectName(_fromUtf8("chkOrgStructure"))
        self.gridLayout.addWidget(self.chkOrgStructure, 9, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.lstOperation = CRBListBox(ReportSurgicalIndicators)
        self.lstOperation.setObjectName(_fromUtf8("lstOperation"))
        self.gridLayout.addWidget(self.lstOperation, 13, 0, 1, 4)
        self.lstSpeciality = CRBListBox(ReportSurgicalIndicators)
        self.lstSpeciality.setObjectName(_fromUtf8("lstSpeciality"))
        self.gridLayout.addWidget(self.lstSpeciality, 8, 0, 1, 4)
        self.lblOrder = QtGui.QLabel(ReportSurgicalIndicators)
        self.lblOrder.setObjectName(_fromUtf8("lblOrder"))
        self.gridLayout.addWidget(self.lblOrder, 5, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportSurgicalIndicators)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.chkOperation = QtGui.QCheckBox(ReportSurgicalIndicators)
        self.chkOperation.setObjectName(_fromUtf8("chkOperation"))
        self.gridLayout.addWidget(self.chkOperation, 12, 0, 1, 1)
        self.cmbTypeHosp = QtGui.QComboBox(ReportSurgicalIndicators)
        self.cmbTypeHosp.setObjectName(_fromUtf8("cmbTypeHosp"))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbTypeHosp, 2, 2, 1, 2)
        self.cmbOrder = QtGui.QComboBox(ReportSurgicalIndicators)
        self.cmbOrder.setObjectName(_fromUtf8("cmbOrder"))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbOrder, 5, 2, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportSurgicalIndicators)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportSurgicalIndicators)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 15, 0, 1, 4)
        self.lblTypeHosp = QtGui.QLabel(ReportSurgicalIndicators)
        self.lblTypeHosp.setObjectName(_fromUtf8("lblTypeHosp"))
        self.gridLayout.addWidget(self.lblTypeHosp, 2, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportSurgicalIndicators)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.edtEndDate = CDateEdit(ReportSurgicalIndicators)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportSurgicalIndicators)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 9, 2, 1, 2)
        self.cmbOperation = CRBComboBox(ReportSurgicalIndicators)
        self.cmbOperation.setObjectName(_fromUtf8("cmbOperation"))
        self.gridLayout.addWidget(self.cmbOperation, 12, 2, 1, 2)
        self.lstOrgStructure = CRBListBox(ReportSurgicalIndicators)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridLayout.addWidget(self.lstOrgStructure, 10, 0, 1, 4)
        self.label = QtGui.QLabel(ReportSurgicalIndicators)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 6, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportSurgicalIndicators)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 6, 2, 1, 2)
        self.chkSpeciality = QtGui.QCheckBox(ReportSurgicalIndicators)
        self.chkSpeciality.setObjectName(_fromUtf8("chkSpeciality"))
        self.gridLayout.addWidget(self.chkSpeciality, 7, 0, 1, 1)
        self.cmbSpeciality = CRBComboBox(ReportSurgicalIndicators)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 7, 2, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 14, 0, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportSurgicalIndicators)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportSurgicalIndicators.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportSurgicalIndicators.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportSurgicalIndicators)

    def retranslateUi(self, ReportSurgicalIndicators):
        ReportSurgicalIndicators.setWindowTitle(_translate("ReportSurgicalIndicators", "Dialog", None))
        self.chkOrgStructure.setText(_translate("ReportSurgicalIndicators", "Подразделение", None))
        self.lblOrder.setText(_translate("ReportSurgicalIndicators", "Порядок", None))
        self.lblBegDate.setText(_translate("ReportSurgicalIndicators", "Дата &начала периода", None))
        self.chkOperation.setText(_translate("ReportSurgicalIndicators", "Операция", None))
        self.cmbTypeHosp.setItemText(0, _translate("ReportSurgicalIndicators", "не задано", None))
        self.cmbTypeHosp.setItemText(1, _translate("ReportSurgicalIndicators", "круглосуточный стационар", None))
        self.cmbTypeHosp.setItemText(2, _translate("ReportSurgicalIndicators", "дневной стационар", None))
        self.cmbTypeHosp.setItemText(3, _translate("ReportSurgicalIndicators", "амбулаторно", None))
        self.cmbOrder.setItemText(0, _translate("ReportSurgicalIndicators", "не задано", None))
        self.cmbOrder.setItemText(1, _translate("ReportSurgicalIndicators", "планово", None))
        self.cmbOrder.setItemText(2, _translate("ReportSurgicalIndicators", "экстренно", None))
        self.lblEndDate.setText(_translate("ReportSurgicalIndicators", "Дата &окончания периода", None))
        self.lblTypeHosp.setText(_translate("ReportSurgicalIndicators", "Тип госпитализации", None))
        self.label.setText(_translate("ReportSurgicalIndicators", "Тип финансирования", None))
        self.chkSpeciality.setText(_translate("ReportSurgicalIndicators", "Специальность", None))

from library.RBListBox import CRBListBox
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
