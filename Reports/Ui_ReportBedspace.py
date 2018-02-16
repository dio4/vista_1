# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportBedspace.ui'
#
# Created: Wed Nov 26 19:22:43 2014
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

class Ui_ReportBedspace(object):
    def setupUi(self, ReportBedspace):
        ReportBedspace.setObjectName(_fromUtf8("ReportBedspace"))
        ReportBedspace.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportBedspace.resize(389, 214)
        ReportBedspace.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportBedspace)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtBegDate = CDateEdit(ReportBedspace)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 3, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportBedspace)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 5)
        self.lblOrgStructure = QtGui.QLabel(ReportBedspace)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportBedspace)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportBedspace)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportBedspace)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 4)
        self.lblEndDate = QtGui.QLabel(ReportBedspace)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lblInsurance = QtGui.QLabel(ReportBedspace)
        self.lblInsurance.setObjectName(_fromUtf8("lblInsurance"))
        self.gridLayout.addWidget(self.lblInsurance, 5, 0, 1, 1)
        self.cmbInsurance = CInsurerComboBox(ReportBedspace)
        self.cmbInsurance.setObjectName(_fromUtf8("cmbInsurance"))
        self.gridLayout.addWidget(self.cmbInsurance, 5, 1, 1, 4)
        self.chkUngroupInsurer = QtGui.QCheckBox(ReportBedspace)
        self.chkUngroupInsurer.setObjectName(_fromUtf8("chkUngroupInsurer"))
        self.gridLayout.addWidget(self.chkUngroupInsurer, 6, 1, 1, 2)
        self.lblProfileBed = QtGui.QLabel(ReportBedspace)
        self.lblProfileBed.setObjectName(_fromUtf8("lblProfileBed"))
        self.gridLayout.addWidget(self.lblProfileBed, 3, 0, 1, 1)
        self.cmbProfileBed = CRBComboBox(ReportBedspace)
        self.cmbProfileBed.setObjectName(_fromUtf8("cmbProfileBed"))
        self.gridLayout.addWidget(self.cmbProfileBed, 3, 1, 1, 4)
        self.chkUngroupOrgStructure = QtGui.QCheckBox(ReportBedspace)
        self.chkUngroupOrgStructure.setEnabled(False)
        self.chkUngroupOrgStructure.setObjectName(_fromUtf8("chkUngroupOrgStructure"))
        self.gridLayout.addWidget(self.chkUngroupOrgStructure, 8, 0, 1, 2)
        self.chkUngroupProfileBeds = QtGui.QCheckBox(ReportBedspace)
        self.chkUngroupProfileBeds.setObjectName(_fromUtf8("chkUngroupProfileBeds"))
        self.gridLayout.addWidget(self.chkUngroupProfileBeds, 7, 0, 1, 2)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportBedspace)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportBedspace.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportBedspace.reject)
        QtCore.QObject.connect(self.chkUngroupProfileBeds, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkUngroupOrgStructure.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ReportBedspace)
        ReportBedspace.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportBedspace.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        ReportBedspace.setTabOrder(self.cmbOrgStructure, self.buttonBox)

    def retranslateUi(self, ReportBedspace):
        ReportBedspace.setWindowTitle(_translate("ReportBedspace", "параметры отчёта", None))
        self.lblOrgStructure.setText(_translate("ReportBedspace", "&Подразделение", None))
        self.lblBegDate.setText(_translate("ReportBedspace", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportBedspace", "Дата &окончания периода", None))
        self.lblInsurance.setText(_translate("ReportBedspace", "Страховая компания", None))
        self.chkUngroupInsurer.setText(_translate("ReportBedspace", "не группировать страховые компании", None))
        self.lblProfileBed.setText(_translate("ReportBedspace", "Профиль койки", None))
        self.chkUngroupOrgStructure.setText(_translate("ReportBedspace", "не группировать по подразделениям", None))
        self.chkUngroupProfileBeds.setText(_translate("ReportBedspace", "не группировать по профилям", None))

from Orgs.OrgComboBox import CInsurerComboBox
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
