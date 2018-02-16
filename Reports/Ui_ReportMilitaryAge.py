# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportMilitaryAge.ui'
#
# Created: Thu Jul 10 16:51:01 2014
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

class Ui_ReportMilitaryAge(object):
    def setupUi(self, ReportMilitaryAge):
        ReportMilitaryAge.setObjectName(_fromUtf8("ReportMilitaryAge"))
        ReportMilitaryAge.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportMilitaryAge.resize(442, 206)
        ReportMilitaryAge.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportMilitaryAge)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblOrgStructure = QtGui.QLabel(ReportMilitaryAge)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportMilitaryAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportMilitaryAge)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 5)
        self.cmbOrgStructure = COrgStructureComboBox(ReportMilitaryAge)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 4)
        self.lblBegDate = QtGui.QLabel(ReportMilitaryAge)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 2)
        self.edtEndDate = CDateEdit(ReportMilitaryAge)
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
        self.lblEndDate = QtGui.QLabel(ReportMilitaryAge)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.cmbAttach = QtGui.QComboBox(ReportMilitaryAge)
        self.cmbAttach.setObjectName(_fromUtf8("cmbAttach"))
        self.cmbAttach.addItem(_fromUtf8(""))
        self.cmbAttach.addItem(_fromUtf8(""))
        self.cmbAttach.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbAttach, 3, 1, 1, 4)
        self.label = QtGui.QLabel(ReportMilitaryAge)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.chkGroupByArea = QtGui.QCheckBox(ReportMilitaryAge)
        self.chkGroupByArea.setObjectName(_fromUtf8("chkGroupByArea"))
        self.gridLayout.addWidget(self.chkGroupByArea, 4, 1, 1, 1)
        self.chkGroupByYear = QtGui.QCheckBox(ReportMilitaryAge)
        self.chkGroupByYear.setObjectName(_fromUtf8("chkGroupByYear"))
        self.gridLayout.addWidget(self.chkGroupByYear, 5, 1, 1, 1)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportMilitaryAge)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportMilitaryAge.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportMilitaryAge.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportMilitaryAge)
        ReportMilitaryAge.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportMilitaryAge.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        ReportMilitaryAge.setTabOrder(self.cmbOrgStructure, self.buttonBox)

    def retranslateUi(self, ReportMilitaryAge):
        ReportMilitaryAge.setWindowTitle(_translate("ReportMilitaryAge", "параметры отчёта", None))
        self.lblOrgStructure.setText(_translate("ReportMilitaryAge", "&Подразделение", None))
        self.lblBegDate.setText(_translate("ReportMilitaryAge", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportMilitaryAge", "Дата &окончания периода", None))
        self.cmbAttach.setItemText(0, _translate("ReportMilitaryAge", "не задано", None))
        self.cmbAttach.setItemText(1, _translate("ReportMilitaryAge", "K", None))
        self.cmbAttach.setItemText(2, _translate("ReportMilitaryAge", "Д", None))
        self.label.setText(_translate("ReportMilitaryAge", "Тип наблюдения", None))
        self.chkGroupByArea.setText(_translate("ReportMilitaryAge", "Группировка по участку", None))
        self.chkGroupByYear.setText(_translate("ReportMilitaryAge", "Группировка по году рождения", None))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
