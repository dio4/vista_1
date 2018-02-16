# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportClientsWithValidPolis.ui'
#
# Created: Wed Dec 05 17:33:36 2012
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportClientsWithValidPolisDialog(object):
    def setupUi(self, ReportClientsWithValidPolisDialog):
        ReportClientsWithValidPolisDialog.setObjectName(_fromUtf8("ReportClientsWithValidPolisDialog"))
        ReportClientsWithValidPolisDialog.resize(391, 265)
        self.gridLayout = QtGui.QGridLayout(ReportClientsWithValidPolisDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblAgeTo = QtGui.QLabel(ReportClientsWithValidPolisDialog)
        self.lblAgeTo.setObjectName(_fromUtf8("lblAgeTo"))
        self.gridLayout.addWidget(self.lblAgeTo, 3, 2, 1, 1)
        self.lblReportDate = QtGui.QLabel(ReportClientsWithValidPolisDialog)
        self.lblReportDate.setObjectName(_fromUtf8("lblReportDate"))
        self.gridLayout.addWidget(self.lblReportDate, 1, 0, 1, 1)
        self.lblInsurerDoctors = QtGui.QLabel(ReportClientsWithValidPolisDialog)
        self.lblInsurerDoctors.setObjectName(_fromUtf8("lblInsurerDoctors"))
        self.gridLayout.addWidget(self.lblInsurerDoctors, 0, 0, 1, 1)
        self.edtAgeTo = QtGui.QSpinBox(ReportClientsWithValidPolisDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeTo.sizePolicy().hasHeightForWidth())
        self.edtAgeTo.setSizePolicy(sizePolicy)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self.gridLayout.addWidget(self.edtAgeTo, 3, 3, 1, 1)
        self.lblAge = QtGui.QLabel(ReportClientsWithValidPolisDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout.addWidget(self.lblAge, 3, 0, 1, 1)
        self.cmbInsurerDoctors = CInsurerComboBox(ReportClientsWithValidPolisDialog)
        self.cmbInsurerDoctors.setObjectName(_fromUtf8("cmbInsurerDoctors"))
        self.gridLayout.addWidget(self.cmbInsurerDoctors, 0, 1, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(ReportClientsWithValidPolisDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 1, 1, 4)
        self.chkShowLocAddress = QtGui.QCheckBox(ReportClientsWithValidPolisDialog)
        self.chkShowLocAddress.setObjectName(_fromUtf8("chkShowLocAddress"))
        self.gridLayout.addWidget(self.chkShowLocAddress, 7, 0, 1, 5)
        self.lblConfirmDate = QtGui.QLabel(ReportClientsWithValidPolisDialog)
        self.lblConfirmDate.setObjectName(_fromUtf8("lblConfirmDate"))
        self.gridLayout.addWidget(self.lblConfirmDate, 2, 0, 1, 1)
        self.edtReportDate = CDateEdit(ReportClientsWithValidPolisDialog)
        self.edtReportDate.setObjectName(_fromUtf8("edtReportDate"))
        self.gridLayout.addWidget(self.edtReportDate, 1, 1, 1, 4)
        self.cmbSex = QtGui.QComboBox(ReportClientsWithValidPolisDialog)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbSex, 4, 1, 1, 4)
        spacerItem = QtGui.QSpacerItem(20, 185, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 1, 1, 1)
        self.edtConfirmDate = CDateEdit(ReportClientsWithValidPolisDialog)
        self.edtConfirmDate.setObjectName(_fromUtf8("edtConfirmDate"))
        self.gridLayout.addWidget(self.edtConfirmDate, 2, 1, 1, 4)
        self.edtAgeFrom = QtGui.QSpinBox(ReportClientsWithValidPolisDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeFrom.sizePolicy().hasHeightForWidth())
        self.edtAgeFrom.setSizePolicy(sizePolicy)
        self.edtAgeFrom.setMaximum(150)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self.gridLayout.addWidget(self.edtAgeFrom, 3, 1, 1, 1)
        self.lblAgeYears = QtGui.QLabel(ReportClientsWithValidPolisDialog)
        self.lblAgeYears.setObjectName(_fromUtf8("lblAgeYears"))
        self.gridLayout.addWidget(self.lblAgeYears, 3, 4, 1, 1)
        self.cmbAttachmentOrgStructureId = COrgStructureComboBox(ReportClientsWithValidPolisDialog)
        self.cmbAttachmentOrgStructureId.setObjectName(_fromUtf8("cmbAttachmentOrgStructureId"))
        self.gridLayout.addWidget(self.cmbAttachmentOrgStructureId, 5, 1, 1, 4)
        self.lblSex = QtGui.QLabel(ReportClientsWithValidPolisDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout.addWidget(self.lblSex, 4, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportClientsWithValidPolisDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 5, 0, 1, 1)
        self.chkShowRegAddress = QtGui.QCheckBox(ReportClientsWithValidPolisDialog)
        self.chkShowRegAddress.setObjectName(_fromUtf8("chkShowRegAddress"))
        self.gridLayout.addWidget(self.chkShowRegAddress, 6, 0, 1, 5)
        self.lblAgeTo.setBuddy(self.edtAgeTo)
        self.lblReportDate.setBuddy(self.edtReportDate)
        self.lblInsurerDoctors.setBuddy(self.cmbInsurerDoctors)
        self.lblAge.setBuddy(self.edtAgeFrom)
        self.lblConfirmDate.setBuddy(self.edtConfirmDate)
        self.lblAgeYears.setBuddy(self.edtAgeTo)

        self.retranslateUi(ReportClientsWithValidPolisDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportClientsWithValidPolisDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportClientsWithValidPolisDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportClientsWithValidPolisDialog)

    def retranslateUi(self, ReportClientsWithValidPolisDialog):
        ReportClientsWithValidPolisDialog.setWindowTitle(QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeTo.setText(QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.lblReportDate.setText(QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "Дата составления отчета", None, QtGui.QApplication.UnicodeUTF8))
        self.lblInsurerDoctors.setText(QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "&СМО", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAge.setText(QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "Во&зраст с", None, QtGui.QApplication.UnicodeUTF8))
        self.chkShowLocAddress.setText(QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "Выводить адрес проживания", None, QtGui.QApplication.UnicodeUTF8))
        self.lblConfirmDate.setText(QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "Дата подтверждения ЕИС", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(1, QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "М", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(2, QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "Ж", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeYears.setText(QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "лет", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSex.setText(QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "Пол", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.chkShowRegAddress.setText(QtGui.QApplication.translate("ReportClientsWithValidPolisDialog", "Выводить адрес регистрации", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.OrgComboBox import CInsurerComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
