# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/artiom/s11/s11/Reports/ReportPayersSetup.ui'
#
# Created: Wed Aug 29 15:09:13 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportPayersSetupDialog(object):
    def setupUi(self, ReportPayersSetupDialog):
        ReportPayersSetupDialog.setObjectName(_fromUtf8("ReportPayersSetupDialog"))
        ReportPayersSetupDialog.resize(404, 371)
        ReportPayersSetupDialog.setMinimumSize(QtCore.QSize(383, 0))
        self.gridLayout = QtGui.QGridLayout(ReportPayersSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ReportPayersSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 11, 1, 1, 2)
        self.edtBegDate = CDateEdit(ReportPayersSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportPayersSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblBegDate.sizePolicy().hasHeightForWidth())
        self.lblBegDate.setSizePolicy(sizePolicy)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportPayersSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbFinance.sizePolicy().hasHeightForWidth())
        self.cmbFinance.setSizePolicy(sizePolicy)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 2, 1, 1, 2)
        self.lblFinance = QtGui.QLabel(ReportPayersSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFinance.sizePolicy().hasHeightForWidth())
        self.lblFinance.setSizePolicy(sizePolicy)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 2, 0, 1, 1)
        self.chkFreeInputWork = QtGui.QCheckBox(ReportPayersSetupDialog)
        self.chkFreeInputWork.setObjectName(_fromUtf8("chkFreeInputWork"))
        self.gridLayout.addWidget(self.chkFreeInputWork, 6, 0, 1, 1)
        self.edtFreeInputWork = QtGui.QLineEdit(ReportPayersSetupDialog)
        self.edtFreeInputWork.setObjectName(_fromUtf8("edtFreeInputWork"))
        self.gridLayout.addWidget(self.edtFreeInputWork, 6, 1, 1, 2)
        self.lblInsurer = QtGui.QLabel(ReportPayersSetupDialog)
        self.lblInsurer.setObjectName(_fromUtf8("lblInsurer"))
        self.gridLayout.addWidget(self.lblInsurer, 7, 0, 1, 1)
        self.lblContract = QtGui.QLabel(ReportPayersSetupDialog)
        self.lblContract.setObjectName(_fromUtf8("lblContract"))
        self.gridLayout.addWidget(self.lblContract, 4, 0, 1, 1)
        self.chkPrintPayerResult = QtGui.QCheckBox(ReportPayersSetupDialog)
        self.chkPrintPayerResult.setObjectName(_fromUtf8("chkPrintPayerResult"))
        self.gridLayout.addWidget(self.chkPrintPayerResult, 8, 0, 1, 2)
        self.cmbClientOrganisation = COrgComboBox(ReportPayersSetupDialog)
        self.cmbClientOrganisation.setObjectName(_fromUtf8("cmbClientOrganisation"))
        self.gridLayout.addWidget(self.cmbClientOrganisation, 5, 1, 1, 2)
        self.edtEndDate = CDateEdit(ReportPayersSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportPayersSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEndDate.sizePolicy().hasHeightForWidth())
        self.lblEndDate.setSizePolicy(sizePolicy)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(368, 96, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 10, 0, 1, 3)
        self.cmbInsurer = CInsurerComboBox(ReportPayersSetupDialog)
        self.cmbInsurer.setObjectName(_fromUtf8("cmbInsurer"))
        self.gridLayout.addWidget(self.cmbInsurer, 7, 1, 1, 2)
        self.cmbContract = CIndependentContractComboBox(ReportPayersSetupDialog)
        self.cmbContract.setObjectName(_fromUtf8("cmbContract"))
        self.gridLayout.addWidget(self.cmbContract, 4, 1, 1, 2)
        self.lblClientOrganisation = QtGui.QLabel(ReportPayersSetupDialog)
        self.lblClientOrganisation.setObjectName(_fromUtf8("lblClientOrganisation"))
        self.gridLayout.addWidget(self.lblClientOrganisation, 5, 0, 1, 1)
        self.chkDetailContracts = QtGui.QCheckBox(ReportPayersSetupDialog)
        self.chkDetailContracts.setObjectName(_fromUtf8("chkDetailContracts"))
        self.gridLayout.addWidget(self.chkDetailContracts, 3, 0, 1, 2)
        self.lblSpeciality = QtGui.QLabel(ReportPayersSetupDialog)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout.addWidget(self.lblSpeciality, 9, 0, 1, 1)
        self.cmbSpeciality = CRBComboBox(ReportPayersSetupDialog)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 9, 1, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblSpeciality.setBuddy(self.cmbSpeciality)

        self.retranslateUi(ReportPayersSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportPayersSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportPayersSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportPayersSetupDialog)

    def retranslateUi(self, ReportPayersSetupDialog):
        ReportPayersSetupDialog.setWindowTitle(QtGui.QApplication.translate("ReportPayersSetupDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("ReportPayersSetupDialog", "Дата &начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFinance.setText(QtGui.QApplication.translate("ReportPayersSetupDialog", "Тип финанисирования", None, QtGui.QApplication.UnicodeUTF8))
        self.chkFreeInputWork.setText(QtGui.QApplication.translate("ReportPayersSetupDialog", "место работы по названию", None, QtGui.QApplication.UnicodeUTF8))
        self.lblInsurer.setText(QtGui.QApplication.translate("ReportPayersSetupDialog", "СМО", None, QtGui.QApplication.UnicodeUTF8))
        self.lblContract.setText(QtGui.QApplication.translate("ReportPayersSetupDialog", "Договор", None, QtGui.QApplication.UnicodeUTF8))
        self.chkPrintPayerResult.setText(QtGui.QApplication.translate("ReportPayersSetupDialog", "Выводить итоги по плательщику", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("ReportPayersSetupDialog", "Дата &окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblClientOrganisation.setText(QtGui.QApplication.translate("ReportPayersSetupDialog", "Место работы", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDetailContracts.setText(QtGui.QApplication.translate("ReportPayersSetupDialog", "Детализировать по договарам", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSpeciality.setText(QtGui.QApplication.translate("ReportPayersSetupDialog", "&Специальность врача", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSpeciality.setWhatsThis(QtGui.QApplication.translate("ReportPayersSetupDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.OrgComboBox import CInsurerComboBox, CIndependentContractComboBox, COrgComboBox
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportPayersSetupDialog = QtGui.QDialog()
    ui = Ui_ReportPayersSetupDialog()
    ui.setupUi(ReportPayersSetupDialog)
    ReportPayersSetupDialog.show()
    sys.exit(app.exec_())

