# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\ReportF32Setup.ui'
#
# Created: Fri Jun 15 12:17:58 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportF32SetupDialog(object):
    def setupUi(self, ReportF32SetupDialog):
        ReportF32SetupDialog.setObjectName(_fromUtf8("ReportF32SetupDialog"))
        ReportF32SetupDialog.resize(408, 258)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportF32SetupDialog.sizePolicy().hasHeightForWidth())
        ReportF32SetupDialog.setSizePolicy(sizePolicy)
        self.label = QtGui.QLabel(ReportF32SetupDialog)
        self.label.setGeometry(QtCore.QRect(10, 20, 141, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.edtEndDate = CDateEdit(ReportF32SetupDialog)
        self.edtEndDate.setGeometry(QtCore.QRect(210, 50, 110, 22))
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.edtBegDate = CDateEdit(ReportF32SetupDialog)
        self.edtBegDate.setGeometry(QtCore.QRect(210, 20, 110, 22))
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.label_2 = QtGui.QLabel(ReportF32SetupDialog)
        self.label_2.setGeometry(QtCore.QRect(10, 50, 161, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_4 = QtGui.QLabel(ReportF32SetupDialog)
        self.label_4.setGeometry(QtCore.QRect(10, 110, 131, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.cmbOrgStructure = COrgStructureComboBox(ReportF32SetupDialog)
        self.cmbOrgStructure.setGeometry(QtCore.QRect(210, 110, 191, 22))
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.cmbEventType = CRBComboBox(ReportF32SetupDialog)
        self.cmbEventType.setGeometry(QtCore.QRect(210, 80, 191, 22))
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.label_3 = QtGui.QLabel(ReportF32SetupDialog)
        self.label_3.setGeometry(QtCore.QRect(10, 80, 131, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.buttonBox = QtGui.QDialogButtonBox(ReportF32SetupDialog)
        self.buttonBox.setGeometry(QtCore.QRect(180, 230, 221, 23))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lblSpeciality = QtGui.QLabel(ReportF32SetupDialog)
        self.lblSpeciality.setGeometry(QtCore.QRect(9, 140, 197, 25))
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.cmbPerson = CPersonComboBoxEx(ReportF32SetupDialog)
        self.cmbPerson.setGeometry(QtCore.QRect(210, 169, 191, 25))
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.lblPerson = QtGui.QLabel(ReportF32SetupDialog)
        self.lblPerson.setGeometry(QtCore.QRect(9, 169, 197, 25))
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.cmbSpeciality = CRBComboBox(ReportF32SetupDialog)
        self.cmbSpeciality.setGeometry(QtCore.QRect(210, 140, 191, 25))
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.lblAgeYears = QtGui.QLabel(ReportF32SetupDialog)
        self.lblAgeYears.setGeometry(QtCore.QRect(348, 200, 23, 25))
        self.lblAgeYears.setObjectName(_fromUtf8("lblAgeYears"))
        self.edtAgeTo = QtGui.QSpinBox(ReportF32SetupDialog)
        self.edtAgeTo.setGeometry(QtCore.QRect(289, 200, 55, 25))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeTo.sizePolicy().hasHeightForWidth())
        self.edtAgeTo.setSizePolicy(sizePolicy)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self.edtAgeFrom = QtGui.QSpinBox(ReportF32SetupDialog)
        self.edtAgeFrom.setGeometry(QtCore.QRect(210, 200, 55, 25))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeFrom.sizePolicy().hasHeightForWidth())
        self.edtAgeFrom.setSizePolicy(sizePolicy)
        self.edtAgeFrom.setMaximum(150)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self.lblAge = QtGui.QLabel(ReportF32SetupDialog)
        self.lblAge.setGeometry(QtCore.QRect(384, 612, 197, 25))
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.lblAge_2 = QtGui.QLabel(ReportF32SetupDialog)
        self.lblAge_2.setGeometry(QtCore.QRect(10, 200, 197, 25))
        self.lblAge_2.setObjectName(_fromUtf8("lblAge_2"))
        self.lblAgeTo = QtGui.QLabel(ReportF32SetupDialog)
        self.lblAgeTo.setGeometry(QtCore.QRect(270, 200, 16, 25))
        self.lblAgeTo.setObjectName(_fromUtf8("lblAgeTo"))
        self.lblSpeciality.setBuddy(self.cmbSpeciality)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblAgeYears.setBuddy(self.edtAgeTo)
        self.lblAge.setBuddy(self.edtAgeFrom)
        self.lblAge_2.setBuddy(self.edtAgeFrom)
        self.lblAgeTo.setBuddy(self.edtAgeTo)

        self.retranslateUi(ReportF32SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF32SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF32SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF32SetupDialog)

    def retranslateUi(self, ReportF32SetupDialog):
        ReportF32SetupDialog.setWindowTitle(QtGui.QApplication.translate("ReportF32SetupDialog", "Параметры отчета", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ReportF32SetupDialog", "Дата начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ReportF32SetupDialog", "Дата окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ReportF32SetupDialog", "Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ReportF32SetupDialog", "Тип обращения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSpeciality.setText(QtGui.QApplication.translate("ReportF32SetupDialog", "&Специальность", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPerson.setText(QtGui.QApplication.translate("ReportF32SetupDialog", "&Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSpeciality.setWhatsThis(QtGui.QApplication.translate("ReportF32SetupDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeYears.setText(QtGui.QApplication.translate("ReportF32SetupDialog", "лет", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAge.setText(QtGui.QApplication.translate("ReportF32SetupDialog", "Во&зраст с", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAge_2.setText(QtGui.QApplication.translate("ReportF32SetupDialog", "Во&зраст с", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeTo.setText(QtGui.QApplication.translate("ReportF32SetupDialog", "по", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportF32SetupDialog = QtGui.QDialog()
    ui = Ui_ReportF32SetupDialog()
    ui.setupUi(ReportF32SetupDialog)
    ReportF32SetupDialog.show()
    sys.exit(app.exec_())

