# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportReferralForHospitalizationSetup.ui'
#
# Created: Thu Jul 24 16:54:38 2014
#      by: PyQt4 UI code generator 4.11
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

class Ui_ReportReferralForHospitalizationSetupDialog(object):
    def setupUi(self, ReportReferralForHospitalizationSetupDialog):
        ReportReferralForHospitalizationSetupDialog.setObjectName(_fromUtf8("ReportReferralForHospitalizationSetupDialog"))
        ReportReferralForHospitalizationSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportReferralForHospitalizationSetupDialog.resize(325, 124)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportReferralForHospitalizationSetupDialog.sizePolicy().hasHeightForWidth())
        ReportReferralForHospitalizationSetupDialog.setSizePolicy(sizePolicy)
        ReportReferralForHospitalizationSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportReferralForHospitalizationSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportReferralForHospitalizationSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportReferralForHospitalizationSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportReferralForHospitalizationSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(ReportReferralForHospitalizationSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 1, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportReferralForHospitalizationSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 1, 1, 1, 1)

        self.retranslateUi(ReportReferralForHospitalizationSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportReferralForHospitalizationSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportReferralForHospitalizationSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportReferralForHospitalizationSetupDialog)

    def retranslateUi(self, ReportReferralForHospitalizationSetupDialog):
        ReportReferralForHospitalizationSetupDialog.setWindowTitle(_translate("ReportReferralForHospitalizationSetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportReferralForHospitalizationSetupDialog", "Дата начала периода", None))
        self.lblOrgStructure.setText(_translate("ReportReferralForHospitalizationSetupDialog", "Подразделение", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
