# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportHospitalOnkoSetupDialog.ui'
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

class Ui_ReportHospitalOnkoSetupDialog(object):
    def setupUi(self, ReportHospitalOnkoSetupDialog):
        ReportHospitalOnkoSetupDialog.setObjectName(_fromUtf8("ReportHospitalOnkoSetupDialog"))
        ReportHospitalOnkoSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportHospitalOnkoSetupDialog.resize(467, 242)
        ReportHospitalOnkoSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportHospitalOnkoSetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbCitizenship = QtGui.QComboBox(ReportHospitalOnkoSetupDialog)
        self.cmbCitizenship.setObjectName(_fromUtf8("cmbCitizenship"))
        self.gridLayout.addWidget(self.cmbCitizenship, 5, 1, 1, 2)
        self.lblDiagnosis = QtGui.QLabel(ReportHospitalOnkoSetupDialog)
        self.lblDiagnosis.setObjectName(_fromUtf8("lblDiagnosis"))
        self.gridLayout.addWidget(self.lblDiagnosis, 2, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportHospitalOnkoSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 6, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportHospitalOnkoSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportHospitalOnkoSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportHospitalOnkoSetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportHospitalOnkoSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 3)
        self.edtBegDate = CDateEdit(ReportHospitalOnkoSetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)
        self.lblSex = QtGui.QLabel(ReportHospitalOnkoSetupDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout.addWidget(self.lblSex, 3, 0, 1, 1)
        self.cmbAge = QtGui.QComboBox(ReportHospitalOnkoSetupDialog)
        self.cmbAge.setObjectName(_fromUtf8("cmbAge"))
        self.gridLayout.addWidget(self.cmbAge, 4, 1, 1, 2)
        self.cmbDiagnosis = QtGui.QComboBox(ReportHospitalOnkoSetupDialog)
        self.cmbDiagnosis.setObjectName(_fromUtf8("cmbDiagnosis"))
        self.gridLayout.addWidget(self.cmbDiagnosis, 2, 1, 1, 2)
        self.lblCitizenship = QtGui.QLabel(ReportHospitalOnkoSetupDialog)
        self.lblCitizenship.setObjectName(_fromUtf8("lblCitizenship"))
        self.gridLayout.addWidget(self.lblCitizenship, 5, 0, 1, 1)
        self.cmbOrgStructure = QtGui.QComboBox(ReportHospitalOnkoSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 6, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(111, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 7, 0, 1, 3)
        self.lblAge = QtGui.QLabel(ReportHospitalOnkoSetupDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout.addWidget(self.lblAge, 4, 0, 1, 1)
        self.cmbSex = QtGui.QComboBox(ReportHospitalOnkoSetupDialog)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.gridLayout.addWidget(self.cmbSex, 3, 1, 1, 2)
        self.lblDiagnosis.setBuddy(self.cmbDiagnosis)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblCitizenship.setBuddy(self.cmbCitizenship)
        self.lblAge.setBuddy(self.cmbAge)

        self.retranslateUi(ReportHospitalOnkoSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportHospitalOnkoSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportHospitalOnkoSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportHospitalOnkoSetupDialog)
        ReportHospitalOnkoSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportHospitalOnkoSetupDialog.setTabOrder(self.edtEndDate, self.cmbDiagnosis)
        ReportHospitalOnkoSetupDialog.setTabOrder(self.cmbDiagnosis, self.cmbSex)
        ReportHospitalOnkoSetupDialog.setTabOrder(self.cmbSex, self.cmbAge)
        ReportHospitalOnkoSetupDialog.setTabOrder(self.cmbAge, self.cmbCitizenship)
        ReportHospitalOnkoSetupDialog.setTabOrder(self.cmbCitizenship, self.cmbOrgStructure)
        ReportHospitalOnkoSetupDialog.setTabOrder(self.cmbOrgStructure, self.buttonBox)

    def retranslateUi(self, ReportHospitalOnkoSetupDialog):
        ReportHospitalOnkoSetupDialog.setWindowTitle(_translate("ReportHospitalOnkoSetupDialog", "параметры отчёта", None))
        self.lblDiagnosis.setText(_translate("ReportHospitalOnkoSetupDialog", "Диагноз", None))
        self.lblOrgStructure.setText(_translate("ReportHospitalOnkoSetupDialog", "Подразделение", None))
        self.lblEndDate.setText(_translate("ReportHospitalOnkoSetupDialog", "Дата окончания периода", None))
        self.lblBegDate.setText(_translate("ReportHospitalOnkoSetupDialog", "Дата начала периода", None))
        self.lblSex.setText(_translate("ReportHospitalOnkoSetupDialog", "Пол", None))
        self.lblCitizenship.setText(_translate("ReportHospitalOnkoSetupDialog", "Территориальный", None))
        self.lblAge.setText(_translate("ReportHospitalOnkoSetupDialog", "Возраст", None))
        self.cmbSex.setWhatsThis(_translate("ReportHospitalOnkoSetupDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))

from library.DateEdit import CDateEdit
