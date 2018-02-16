# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportF16.ui'
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

class Ui_ReportF16(object):
    def setupUi(self, ReportF16):
        ReportF16.setObjectName(_fromUtf8("ReportF16"))
        ReportF16.resize(429, 488)
        self.gridLayout = QtGui.QGridLayout(ReportF16)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lstOrgStructure = CRBListBox(ReportF16)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridLayout.addWidget(self.lstOrgStructure, 7, 0, 1, 3)
        self.cmbProfileBed = CRBComboBox(ReportF16)
        self.cmbProfileBed.setObjectName(_fromUtf8("cmbProfileBed"))
        self.gridLayout.addWidget(self.cmbProfileBed, 8, 1, 1, 2)
        self.lstProfileBed = CRBListBox(ReportF16)
        self.lstProfileBed.setObjectName(_fromUtf8("lstProfileBed"))
        self.gridLayout.addWidget(self.lstProfileBed, 10, 0, 1, 3)
        self.label = QtGui.QLabel(ReportF16)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 5, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportF16)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 6, 1, 1, 2)
        self.chkProfileBed = QtGui.QCheckBox(ReportF16)
        self.chkProfileBed.setObjectName(_fromUtf8("chkProfileBed"))
        self.gridLayout.addWidget(self.chkProfileBed, 8, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportF16)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 12, 2, 1, 1)
        self.cmbOrder = QtGui.QComboBox(ReportF16)
        self.cmbOrder.setObjectName(_fromUtf8("cmbOrder"))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbOrder, 4, 1, 1, 2)
        self.cmbTypeHosp = QtGui.QComboBox(ReportF16)
        self.cmbTypeHosp.setObjectName(_fromUtf8("cmbTypeHosp"))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbTypeHosp, 3, 1, 1, 2)
        self.edtBegDate = CDateEdit(ReportF16)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportF16)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportF16)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblOrder = QtGui.QLabel(ReportF16)
        self.lblOrder.setObjectName(_fromUtf8("lblOrder"))
        self.gridLayout.addWidget(self.lblOrder, 4, 0, 1, 1)
        self.chkOrgStructure = QtGui.QCheckBox(ReportF16)
        self.chkOrgStructure.setObjectName(_fromUtf8("chkOrgStructure"))
        self.gridLayout.addWidget(self.chkOrgStructure, 6, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportF16)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 5, 1, 1, 2)
        self.edtEndDate = CDateEdit(ReportF16)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblTypeHosp = QtGui.QLabel(ReportF16)
        self.lblTypeHosp.setObjectName(_fromUtf8("lblTypeHosp"))
        self.gridLayout.addWidget(self.lblTypeHosp, 3, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 11, 2, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportF16)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF16.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF16.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF16)

    def retranslateUi(self, ReportF16):
        ReportF16.setWindowTitle(_translate("ReportF16", "Dialog", None))
        self.label.setText(_translate("ReportF16", "Тип финансирования", None))
        self.chkProfileBed.setText(_translate("ReportF16", "Профиль", None))
        self.cmbOrder.setItemText(0, _translate("ReportF16", "не задано", None))
        self.cmbOrder.setItemText(1, _translate("ReportF16", "планово", None))
        self.cmbOrder.setItemText(2, _translate("ReportF16", "экстренно", None))
        self.cmbTypeHosp.setItemText(0, _translate("ReportF16", "не задано", None))
        self.cmbTypeHosp.setItemText(1, _translate("ReportF16", "круглосуточный стационар", None))
        self.cmbTypeHosp.setItemText(2, _translate("ReportF16", "дневной стационар", None))
        self.cmbTypeHosp.setItemText(3, _translate("ReportF16", "амбулаторно", None))
        self.lblBegDate.setText(_translate("ReportF16", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportF16", "Дата &окончания периода", None))
        self.lblOrder.setText(_translate("ReportF16", "Порядок", None))
        self.chkOrgStructure.setText(_translate("ReportF16", "Подразделение", None))
        self.lblTypeHosp.setText(_translate("ReportF16", "Тип госпитализации", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
from library.crbcombobox import CRBComboBox
