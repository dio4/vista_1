# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportF14Children.ui'
#
# Created: Tue Dec 16 20:03:42 2014
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

class Ui_ReportF14Children(object):
    def setupUi(self, ReportF14Children):
        ReportF14Children.setObjectName(_fromUtf8("ReportF14Children"))
        ReportF14Children.resize(445, 458)
        self.gridLayout = QtGui.QGridLayout(ReportF14Children)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEventType = QtGui.QLabel(ReportF14Children)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 2, 0, 1, 1)
        self.label = QtGui.QLabel(ReportF14Children)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 7, 0, 1, 2)
        self.cmbFinance = CRBComboBox(ReportF14Children)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 7, 2, 1, 1)
        self.lblOrder = QtGui.QLabel(ReportF14Children)
        self.lblOrder.setObjectName(_fromUtf8("lblOrder"))
        self.gridLayout.addWidget(self.lblOrder, 5, 0, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(ReportF14Children)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 8, 2, 1, 1)
        self.cmbTypeHosp = QtGui.QComboBox(ReportF14Children)
        self.cmbTypeHosp.setObjectName(_fromUtf8("cmbTypeHosp"))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbTypeHosp, 4, 2, 1, 1)
        self.edtBegDate = CDateEdit(ReportF14Children)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.cmbOrder = QtGui.QComboBox(ReportF14Children)
        self.cmbOrder.setObjectName(_fromUtf8("cmbOrder"))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbOrder, 5, 2, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportF14Children)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportF14Children)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        self.lstOrgStructure = CRBListBox(ReportF14Children)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridLayout.addWidget(self.lstOrgStructure, 9, 0, 2, 3)
        self.chkOrgStructure = QtGui.QCheckBox(ReportF14Children)
        self.chkOrgStructure.setObjectName(_fromUtf8("chkOrgStructure"))
        self.gridLayout.addWidget(self.chkOrgStructure, 8, 0, 1, 2)
        self.edtEndDate = CDateEdit(ReportF14Children)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 1)
        self.lblTypeHosp = QtGui.QLabel(ReportF14Children)
        self.lblTypeHosp.setObjectName(_fromUtf8("lblTypeHosp"))
        self.gridLayout.addWidget(self.lblTypeHosp, 4, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportF14Children)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 11, 2, 1, 1)
        self.cmbEventType = CRBComboBox(ReportF14Children)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 2, 2, 1, 1)
        self.lblEventPerpose = QtGui.QLabel(ReportF14Children)
        self.lblEventPerpose.setObjectName(_fromUtf8("lblEventPerpose"))
        self.gridLayout.addWidget(self.lblEventPerpose, 3, 0, 1, 2)
        self.cmbEventPurpose = CRBComboBox(ReportF14Children)
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.gridLayout.addWidget(self.cmbEventPurpose, 3, 2, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportF14Children)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF14Children.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF14Children.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF14Children)

    def retranslateUi(self, ReportF14Children):
        ReportF14Children.setWindowTitle(_translate("ReportF14Children", "Dialog", None))
        self.lblEventType.setText(_translate("ReportF14Children", "Тип обращения", None))
        self.label.setText(_translate("ReportF14Children", "Тип финансирования", None))
        self.lblOrder.setText(_translate("ReportF14Children", "Порядок", None))
        self.cmbTypeHosp.setItemText(0, _translate("ReportF14Children", "не задано", None))
        self.cmbTypeHosp.setItemText(1, _translate("ReportF14Children", "круглосуточный стационар", None))
        self.cmbTypeHosp.setItemText(2, _translate("ReportF14Children", "дневной стационар", None))
        self.cmbTypeHosp.setItemText(3, _translate("ReportF14Children", "амбулаторно", None))
        self.cmbOrder.setItemText(0, _translate("ReportF14Children", "не задано", None))
        self.cmbOrder.setItemText(1, _translate("ReportF14Children", "планово", None))
        self.cmbOrder.setItemText(2, _translate("ReportF14Children", "экстренно", None))
        self.lblBegDate.setText(_translate("ReportF14Children", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportF14Children", "Дата &окончания периода", None))
        self.chkOrgStructure.setText(_translate("ReportF14Children", "Подразделение", None))
        self.lblTypeHosp.setText(_translate("ReportF14Children", "Тип госпитализации", None))
        self.lblEventPerpose.setText(_translate("ReportF14Children", "Тип направления", None))

from library.RBListBox import CRBListBox
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
