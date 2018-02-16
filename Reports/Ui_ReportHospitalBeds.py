# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportHospitalBeds.ui'
#
# Created: Mon Sep 01 19:05:14 2014
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

class Ui_ReportHospitalBegs(object):
    def setupUi(self, ReportHospitalBegs):
        ReportHospitalBegs.setObjectName(_fromUtf8("ReportHospitalBegs"))
        ReportHospitalBegs.resize(374, 159)
        ReportHospitalBegs.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.gridLayout = QtGui.QGridLayout(ReportHospitalBegs)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(ReportHospitalBegs)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportHospitalBegs)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportHospitalBegs)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.edtBegDate = CDateEdit(ReportHospitalBegs)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.edtEndDate = CDateEdit(ReportHospitalBegs)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 2, 1, 1)
        self.label = QtGui.QLabel(ReportHospitalBegs)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportHospitalBegs)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 1, 1, 2)
        self.label_2 = QtGui.QLabel(ReportHospitalBegs)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.cmbTypeHospitalization = QtGui.QComboBox(ReportHospitalBegs)
        self.cmbTypeHospitalization.setObjectName(_fromUtf8("cmbTypeHospitalization"))
        self.cmbTypeHospitalization.addItem(_fromUtf8(""))
        self.cmbTypeHospitalization.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbTypeHospitalization, 4, 1, 1, 2)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportHospitalBegs)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportHospitalBegs.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportHospitalBegs.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportHospitalBegs)
        ReportHospitalBegs.setTabOrder(self.edtBegDate, self.edtEndDate)

    def retranslateUi(self, ReportHospitalBegs):
        ReportHospitalBegs.setWindowTitle(_translate("ReportHospitalBegs", "Dialog", None))
        self.lblEndDate.setText(_translate("ReportHospitalBegs", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportHospitalBegs", "Дата &начала периода", None))
        self.label.setText(_translate("ReportHospitalBegs", "Подразделение", None))
        self.label_2.setText(_translate("ReportHospitalBegs", "Тип госпитализации", None))
        self.cmbTypeHospitalization.setItemText(0, _translate("ReportHospitalBegs", "Круглосуточная", None))
        self.cmbTypeHospitalization.setItemText(1, _translate("ReportHospitalBegs", "Дневной стационар", None))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
