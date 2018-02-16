# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportAnalysisOfDisease.ui'
#
# Created: Fri Apr 24 20:37:46 2015
#      by: PyQt4 UI code generator 4.11.1
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

class Ui_ReportAnalysisOfDisease(object):
    def setupUi(self, ReportAnalysisOfDisease):
        ReportAnalysisOfDisease.setObjectName(_fromUtf8("ReportAnalysisOfDisease"))
        ReportAnalysisOfDisease.resize(345, 171)
        ReportAnalysisOfDisease.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.gridLayout = QtGui.QGridLayout(ReportAnalysisOfDisease)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportAnalysisOfDisease)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportAnalysisOfDisease)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportAnalysisOfDisease)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.label = QtGui.QLabel(ReportAnalysisOfDisease)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportAnalysisOfDisease)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 2, 1, 1, 1)
        self.chkFinishedDiagnosis = QtGui.QCheckBox(ReportAnalysisOfDisease)
        self.chkFinishedDiagnosis.setObjectName(_fromUtf8("chkFinishedDiagnosis"))
        self.gridLayout.addWidget(self.chkFinishedDiagnosis, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAnalysisOfDisease)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 1, 1, 1)
        self.edtBegDate = CDateEdit(ReportAnalysisOfDisease)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.chkOrgGroup = QtGui.QCheckBox(ReportAnalysisOfDisease)
        self.chkOrgGroup.setChecked(True)
        self.chkOrgGroup.setObjectName(_fromUtf8("chkOrgGroup"))
        self.gridLayout.addWidget(self.chkOrgGroup, 4, 0, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportAnalysisOfDisease)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAnalysisOfDisease.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAnalysisOfDisease.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAnalysisOfDisease)

    def retranslateUi(self, ReportAnalysisOfDisease):
        ReportAnalysisOfDisease.setWindowTitle(_translate("ReportAnalysisOfDisease", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportAnalysisOfDisease", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportAnalysisOfDisease", "Дата &окончания периода", None))
        self.label.setText(_translate("ReportAnalysisOfDisease", "Тип обращения", None))
        self.chkFinishedDiagnosis.setText(_translate("ReportAnalysisOfDisease", "Заключительному диагнозу обращения", None))
        self.chkOrgGroup.setText(_translate("ReportAnalysisOfDisease", "Показывать номера ИБ", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
