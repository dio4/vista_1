# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\ReportVeteransSetup.ui'
#
# Created: Fri Jun 15 12:18:00 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportVeteransSetupDialog(object):
    def setupUi(self, ReportVeteransSetupDialog):
        ReportVeteransSetupDialog.setObjectName(_fromUtf8("ReportVeteransSetupDialog"))
        ReportVeteransSetupDialog.resize(405, 211)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportVeteransSetupDialog.sizePolicy().hasHeightForWidth())
        ReportVeteransSetupDialog.setSizePolicy(sizePolicy)
        self.label = QtGui.QLabel(ReportVeteransSetupDialog)
        self.label.setGeometry(QtCore.QRect(10, 20, 141, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.edtEndDate = CDateEdit(ReportVeteransSetupDialog)
        self.edtEndDate.setGeometry(QtCore.QRect(210, 50, 110, 22))
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.edtBegDate = CDateEdit(ReportVeteransSetupDialog)
        self.edtBegDate.setGeometry(QtCore.QRect(210, 20, 110, 22))
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.label_2 = QtGui.QLabel(ReportVeteransSetupDialog)
        self.label_2.setGeometry(QtCore.QRect(10, 50, 161, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_4 = QtGui.QLabel(ReportVeteransSetupDialog)
        self.label_4.setGeometry(QtCore.QRect(10, 80, 131, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.cmbOrgStructure = COrgStructureComboBox(ReportVeteransSetupDialog)
        self.cmbOrgStructure.setGeometry(QtCore.QRect(210, 80, 191, 22))
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.buttonBox = QtGui.QDialogButtonBox(ReportVeteransSetupDialog)
        self.buttonBox.setGeometry(QtCore.QRect(180, 180, 221, 23))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.cmbPerson = CPersonComboBoxEx(ReportVeteransSetupDialog)
        self.cmbPerson.setGeometry(QtCore.QRect(210, 109, 191, 25))
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.lblPerson = QtGui.QLabel(ReportVeteransSetupDialog)
        self.lblPerson.setGeometry(QtCore.QRect(9, 109, 197, 25))
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.lblAge = QtGui.QLabel(ReportVeteransSetupDialog)
        self.lblAge.setGeometry(QtCore.QRect(384, 612, 197, 25))
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.cmbEventType = CRBComboBox(ReportVeteransSetupDialog)
        self.cmbEventType.setGeometry(QtCore.QRect(210, 140, 191, 27))
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.lblEventType = QtGui.QLabel(ReportVeteransSetupDialog)
        self.lblEventType.setGeometry(QtCore.QRect(10, 140, 199, 27))
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblEventType.setBuddy(self.cmbEventType)

        self.retranslateUi(ReportVeteransSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportVeteransSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportVeteransSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportVeteransSetupDialog)

    def retranslateUi(self, ReportVeteransSetupDialog):
        ReportVeteransSetupDialog.setWindowTitle(QtGui.QApplication.translate("ReportVeteransSetupDialog", "Параметры отчета", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ReportVeteransSetupDialog", "Дата начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ReportVeteransSetupDialog", "Дата окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ReportVeteransSetupDialog", "Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPerson.setText(QtGui.QApplication.translate("ReportVeteransSetupDialog", "&Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAge.setText(QtGui.QApplication.translate("ReportVeteransSetupDialog", "Во&зраст с", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventType.setText(QtGui.QApplication.translate("ReportVeteransSetupDialog", "&Тип обращения", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportVeteransSetupDialog = QtGui.QDialog()
    ui = Ui_ReportVeteransSetupDialog()
    ui.setupUi(ReportVeteransSetupDialog)
    ReportVeteransSetupDialog.show()
    sys.exit(app.exec_())

