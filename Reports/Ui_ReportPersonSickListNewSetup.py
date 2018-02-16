# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPersonSickListNewSetup.ui'
#
# Created: Mon Aug 04 13:26:37 2014
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

class Ui_ReportPersonSickListNewSetupDialog(object):
    def setupUi(self, ReportPersonSickListNewSetupDialog):
        ReportPersonSickListNewSetupDialog.setObjectName(_fromUtf8("ReportPersonSickListNewSetupDialog"))
        ReportPersonSickListNewSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportPersonSickListNewSetupDialog.resize(294, 177)
        ReportPersonSickListNewSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportPersonSickListNewSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportPersonSickListNewSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportPersonSickListNewSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportPersonSickListNewSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportPersonSickListNewSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportPersonSickListNewSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 2, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportPersonSickListNewSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 2, 1, 1, 1)
        self.chkDiagnosis = QtGui.QCheckBox(ReportPersonSickListNewSetupDialog)
        self.chkDiagnosis.setEnabled(True)
        self.chkDiagnosis.setObjectName(_fromUtf8("chkDiagnosis"))
        self.gridLayout.addWidget(self.chkDiagnosis, 3, 0, 1, 2)
        self.chkResult = QtGui.QCheckBox(ReportPersonSickListNewSetupDialog)
        self.chkResult.setObjectName(_fromUtf8("chkResult"))
        self.gridLayout.addWidget(self.chkResult, 4, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportPersonSickListNewSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblEventType.setBuddy(self.cmbEventType)

        self.retranslateUi(ReportPersonSickListNewSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportPersonSickListNewSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportPersonSickListNewSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportPersonSickListNewSetupDialog)
        ReportPersonSickListNewSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportPersonSickListNewSetupDialog.setTabOrder(self.edtEndDate, self.buttonBox)

    def retranslateUi(self, ReportPersonSickListNewSetupDialog):
        ReportPersonSickListNewSetupDialog.setWindowTitle(_translate("ReportPersonSickListNewSetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportPersonSickListNewSetupDialog", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportPersonSickListNewSetupDialog", "Дата &окончания периода", None))
        self.lblEventType.setText(_translate("ReportPersonSickListNewSetupDialog", "&Тип обращения", None))
        self.cmbEventType.setWhatsThis(_translate("ReportPersonSickListNewSetupDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.chkDiagnosis.setText(_translate("ReportPersonSickListNewSetupDialog", "Учитывать наличие диагноза", None))
        self.chkResult.setText(_translate("ReportPersonSickListNewSetupDialog", "Учитывать наличие результата", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
