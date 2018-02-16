# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/shutov/s11/Reports/ReportDDStudentsResultsSetup.ui'
#
# Created: Thu Oct 18 16:52:13 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportDDStudentsResultsSetupDialog(object):
    def setupUi(self, ReportDDStudentsResultsSetupDialog):
        ReportDDStudentsResultsSetupDialog.setObjectName(_fromUtf8("ReportDDStudentsResultsSetupDialog"))
        ReportDDStudentsResultsSetupDialog.resize(463, 302)
        self.edtBegDate = CDateEdit(ReportDDStudentsResultsSetupDialog)
        self.edtBegDate.setGeometry(QtCore.QRect(249, 10, 205, 27))
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.edtEndDate = CDateEdit(ReportDDStudentsResultsSetupDialog)
        self.edtEndDate.setGeometry(QtCore.QRect(249, 43, 205, 27))
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.lblEndDate = QtGui.QLabel(ReportDDStudentsResultsSetupDialog)
        self.lblEndDate.setGeometry(QtCore.QRect(10, 43, 233, 27))
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.lblBegDate = QtGui.QLabel(ReportDDStudentsResultsSetupDialog)
        self.lblBegDate.setGeometry(QtCore.QRect(10, 10, 233, 27))
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.lblPodtver = QtGui.QLabel(ReportDDStudentsResultsSetupDialog)
        self.lblPodtver.setEnabled(False)
        self.lblPodtver.setGeometry(QtCore.QRect(10, 104, 143, 27))
        self.lblPodtver.setObjectName(_fromUtf8("lblPodtver"))
        self.lblBegDatePodtver = QtGui.QLabel(ReportDDStudentsResultsSetupDialog)
        self.lblBegDatePodtver.setEnabled(False)
        self.lblBegDatePodtver.setGeometry(QtCore.QRect(10, 137, 233, 27))
        self.lblBegDatePodtver.setObjectName(_fromUtf8("lblBegDatePodtver"))
        self.cmbPodtver = QtGui.QComboBox(ReportDDStudentsResultsSetupDialog)
        self.cmbPodtver.setEnabled(False)
        self.cmbPodtver.setGeometry(QtCore.QRect(310, 104, 144, 27))
        self.cmbPodtver.setObjectName(_fromUtf8("cmbPodtver"))
        self.edtEndDatePodtver = CDateEdit(ReportDDStudentsResultsSetupDialog)
        self.edtEndDatePodtver.setEnabled(False)
        self.edtEndDatePodtver.setGeometry(QtCore.QRect(310, 170, 144, 27))
        self.edtEndDatePodtver.setObjectName(_fromUtf8("edtEndDatePodtver"))
        self.cmbRefuseType = CRBComboBox(ReportDDStudentsResultsSetupDialog)
        self.cmbRefuseType.setEnabled(False)
        self.cmbRefuseType.setGeometry(QtCore.QRect(310, 203, 144, 27))
        self.cmbRefuseType.setObjectName(_fromUtf8("cmbRefuseType"))
        self.lblRefuseType = QtGui.QLabel(ReportDDStudentsResultsSetupDialog)
        self.lblRefuseType.setEnabled(False)
        self.lblRefuseType.setGeometry(QtCore.QRect(10, 203, 143, 27))
        self.lblRefuseType.setObjectName(_fromUtf8("lblRefuseType"))
        self.chkPodtver = QtGui.QCheckBox(ReportDDStudentsResultsSetupDialog)
        self.chkPodtver.setGeometry(QtCore.QRect(10, 76, 233, 22))
        self.chkPodtver.setObjectName(_fromUtf8("chkPodtver"))
        self.edtBegDatePodtver = CDateEdit(ReportDDStudentsResultsSetupDialog)
        self.edtBegDatePodtver.setEnabled(False)
        self.edtBegDatePodtver.setGeometry(QtCore.QRect(310, 137, 144, 27))
        self.edtBegDatePodtver.setObjectName(_fromUtf8("edtBegDatePodtver"))
        self.lblEndDatePodtver = QtGui.QLabel(ReportDDStudentsResultsSetupDialog)
        self.lblEndDatePodtver.setEnabled(False)
        self.lblEndDatePodtver.setGeometry(QtCore.QRect(10, 170, 294, 27))
        self.lblEndDatePodtver.setObjectName(_fromUtf8("lblEndDatePodtver"))
        self.buttonBox = QtGui.QDialogButtonBox(ReportDDStudentsResultsSetupDialog)
        self.buttonBox.setGeometry(QtCore.QRect(280, 260, 176, 27))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblPodtver.setBuddy(self.cmbPodtver)
        self.lblBegDatePodtver.setBuddy(self.edtBegDatePodtver)
        self.lblRefuseType.setBuddy(self.cmbRefuseType)
        self.lblEndDatePodtver.setBuddy(self.edtEndDatePodtver)

        self.retranslateUi(ReportDDStudentsResultsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportDDStudentsResultsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportDDStudentsResultsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportDDStudentsResultsSetupDialog)

    def retranslateUi(self, ReportDDStudentsResultsSetupDialog):
        ReportDDStudentsResultsSetupDialog.setWindowTitle(QtGui.QApplication.translate("ReportDDStudentsResultsSetupDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("ReportDDStudentsResultsSetupDialog", "Дата окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("ReportDDStudentsResultsSetupDialog", "Дата начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPodtver.setText(QtGui.QApplication.translate("ReportDDStudentsResultsSetupDialog", "Тип подтве&рждения:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDatePodtver.setText(QtGui.QApplication.translate("ReportDDStudentsResultsSetupDialog", "Начало пер&иода подтверждения:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRefuseType.setText(QtGui.QApplication.translate("ReportDDStudentsResultsSetupDialog", "При&чина отказа:", None, QtGui.QApplication.UnicodeUTF8))
        self.chkPodtver.setText(QtGui.QApplication.translate("ReportDDStudentsResultsSetupDialog", "Подтверждение оп&латы", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDatePodtver.setText(QtGui.QApplication.translate("ReportDDStudentsResultsSetupDialog", "Окончание периода подтверждени&я:", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportDDStudentsResultsSetupDialog = QtGui.QDialog()
    ui = Ui_ReportDDStudentsResultsSetupDialog()
    ui.setupUi(ReportDDStudentsResultsSetupDialog)
    ReportDDStudentsResultsSetupDialog.show()
    sys.exit(app.exec_())

