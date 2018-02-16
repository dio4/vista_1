# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ReportReceivedPatientsSetup.ui'
#
# Created: Tue Oct 06 17:29:12 2015
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

class Ui_ReportReceivedPatientsSetupDialog(object):
    def setupUi(self, ReportReceivedPatientsSetupDialog):
        ReportReceivedPatientsSetupDialog.setObjectName(_fromUtf8("ReportReceivedPatientsSetupDialog"))
        ReportReceivedPatientsSetupDialog.resize(533, 233)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportReceivedPatientsSetupDialog.sizePolicy().hasHeightForWidth())
        ReportReceivedPatientsSetupDialog.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QtGui.QGridLayout(ReportReceivedPatientsSetupDialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(ReportReceivedPatientsSetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportReceivedPatientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout_2.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.edtBegTime = QtGui.QTimeEdit(ReportReceivedPatientsSetupDialog)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout_2.addWidget(self.edtBegTime, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(ReportReceivedPatientsSetupDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportReceivedPatientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout_2.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.edtEndTime = QtGui.QTimeEdit(ReportReceivedPatientsSetupDialog)
        self.edtEndTime.setObjectName(_fromUtf8("edtEndTime"))
        self.gridLayout_2.addWidget(self.edtEndTime, 1, 2, 1, 1)
        self.label_4 = QtGui.QLabel(ReportReceivedPatientsSetupDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 2, 0, 1, 1)
        self.cmbOrgStruct = COrgStructureComboBox(ReportReceivedPatientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbOrgStruct.sizePolicy().hasHeightForWidth())
        self.cmbOrgStruct.setSizePolicy(sizePolicy)
        self.cmbOrgStruct.setObjectName(_fromUtf8("cmbOrgStruct"))
        self.gridLayout_2.addWidget(self.cmbOrgStruct, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(ReportReceivedPatientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkAddress = QtGui.QCheckBox(ReportReceivedPatientsSetupDialog)
        self.chkAddress.setChecked(True)
        self.chkAddress.setObjectName(_fromUtf8("chkAddress"))
        self.gridLayout.addWidget(self.chkAddress, 2, 0, 1, 1)
        self.chkOMS = QtGui.QCheckBox(ReportReceivedPatientsSetupDialog)
        self.chkOMS.setChecked(True)
        self.chkOMS.setObjectName(_fromUtf8("chkOMS"))
        self.gridLayout.addWidget(self.chkOMS, 0, 1, 1, 1)
        self.chkAddressReg = QtGui.QCheckBox(ReportReceivedPatientsSetupDialog)
        self.chkAddressReg.setChecked(True)
        self.chkAddressReg.setObjectName(_fromUtf8("chkAddressReg"))
        self.gridLayout.addWidget(self.chkAddressReg, 1, 0, 1, 1)
        self.chkDMS = QtGui.QCheckBox(ReportReceivedPatientsSetupDialog)
        self.chkDMS.setChecked(True)
        self.chkDMS.setObjectName(_fromUtf8("chkDMS"))
        self.gridLayout.addWidget(self.chkDMS, 1, 1, 1, 1)
        self.chkDoc = QtGui.QCheckBox(ReportReceivedPatientsSetupDialog)
        self.chkDoc.setChecked(True)
        self.chkDoc.setObjectName(_fromUtf8("chkDoc"))
        self.gridLayout.addWidget(self.chkDoc, 0, 0, 1, 1)
        self.chkWork = QtGui.QCheckBox(ReportReceivedPatientsSetupDialog)
        self.chkWork.setChecked(True)
        self.chkWork.setObjectName(_fromUtf8("chkWork"))
        self.gridLayout.addWidget(self.chkWork, 2, 1, 1, 1)
        self.chkDir = QtGui.QCheckBox(ReportReceivedPatientsSetupDialog)
        self.chkDir.setChecked(True)
        self.chkDir.setObjectName(_fromUtf8("chkDir"))
        self.gridLayout.addWidget(self.chkDir, 0, 2, 1, 1)
        self.chkDiagDir = QtGui.QCheckBox(ReportReceivedPatientsSetupDialog)
        self.chkDiagDir.setChecked(True)
        self.chkDiagDir.setObjectName(_fromUtf8("chkDiagDir"))
        self.gridLayout.addWidget(self.chkDiagDir, 1, 2, 1, 1)
        self.chkDiag = QtGui.QCheckBox(ReportReceivedPatientsSetupDialog)
        self.chkDiag.setChecked(True)
        self.chkDiag.setObjectName(_fromUtf8("chkDiag"))
        self.gridLayout.addWidget(self.chkDiag, 2, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 4, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ReportReceivedPatientsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 5, 1, 1, 2)

        self.retranslateUi(ReportReceivedPatientsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportReceivedPatientsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportReceivedPatientsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportReceivedPatientsSetupDialog)

    def retranslateUi(self, ReportReceivedPatientsSetupDialog):
        ReportReceivedPatientsSetupDialog.setWindowTitle(_translate("ReportReceivedPatientsSetupDialog", "Dialog", None))
        self.label.setText(_translate("ReportReceivedPatientsSetupDialog", "Дата начала", None))
        self.label_2.setText(_translate("ReportReceivedPatientsSetupDialog", "Дата окончания", None))
        self.label_4.setText(_translate("ReportReceivedPatientsSetupDialog", "Подразделение", None))
        self.label_3.setText(_translate("ReportReceivedPatientsSetupDialog", "Выводить в отчёт:", None))
        self.chkAddress.setText(_translate("ReportReceivedPatientsSetupDialog", "Адрес проживания", None))
        self.chkOMS.setText(_translate("ReportReceivedPatientsSetupDialog", "Данные полиса ОМС", None))
        self.chkAddressReg.setText(_translate("ReportReceivedPatientsSetupDialog", "Адрес регистрации", None))
        self.chkDMS.setText(_translate("ReportReceivedPatientsSetupDialog", "Данные полиса ДМС", None))
        self.chkDoc.setText(_translate("ReportReceivedPatientsSetupDialog", "Документ, удостоверяющий личность", None))
        self.chkWork.setText(_translate("ReportReceivedPatientsSetupDialog", "Место работы", None))
        self.chkDir.setText(_translate("ReportReceivedPatientsSetupDialog", "Кем направлен", None))
        self.chkDiagDir.setText(_translate("ReportReceivedPatientsSetupDialog", "Диагноз направителя", None))
        self.chkDiag.setText(_translate("ReportReceivedPatientsSetupDialog", "Диагноз при поступлении", None))

from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
