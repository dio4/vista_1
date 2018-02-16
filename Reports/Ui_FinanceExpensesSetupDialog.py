# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\FinanceExpensesSetupDialog.ui'
#
# Created: Fri Jun 15 12:17:21 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FinanceExpensesSetupDialog(object):
    def setupUi(self, FinanceExpensesSetupDialog):
        FinanceExpensesSetupDialog.setObjectName(_fromUtf8("FinanceExpensesSetupDialog"))
        FinanceExpensesSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        FinanceExpensesSetupDialog.resize(345, 264)
        FinanceExpensesSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(FinanceExpensesSetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(FinanceExpensesSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.edtBegDate = CDateEdit(FinanceExpensesSetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(101, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.lblEndDate = QtGui.QLabel(FinanceExpensesSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        self.edtEndDate = CDateEdit(FinanceExpensesSetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(101, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 3, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(FinanceExpensesSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(FinanceExpensesSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 2, 1, 2)
        self.lblSpeciality = QtGui.QLabel(FinanceExpensesSetupDialog)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout.addWidget(self.lblSpeciality, 3, 0, 1, 2)
        self.cmbSpeciality = CRBComboBox(FinanceExpensesSetupDialog)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 3, 2, 1, 2)
        self.lblPerson = QtGui.QLabel(FinanceExpensesSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 4, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(FinanceExpensesSetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 4, 2, 1, 2)
        self.lblInsurerDoctors = QtGui.QLabel(FinanceExpensesSetupDialog)
        self.lblInsurerDoctors.setObjectName(_fromUtf8("lblInsurerDoctors"))
        self.gridLayout.addWidget(self.lblInsurerDoctors, 5, 0, 1, 1)
        self.cmbInsurerDoctors = CInsurerComboBox(FinanceExpensesSetupDialog)
        self.cmbInsurerDoctors.setObjectName(_fromUtf8("cmbInsurerDoctors"))
        self.gridLayout.addWidget(self.cmbInsurerDoctors, 5, 2, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(21, 21, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 7, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(FinanceExpensesSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 4)
        self.lblAnalysisAccountItems = QtGui.QLabel(FinanceExpensesSetupDialog)
        self.lblAnalysisAccountItems.setObjectName(_fromUtf8("lblAnalysisAccountItems"))
        self.gridLayout.addWidget(self.lblAnalysisAccountItems, 6, 0, 1, 1)
        self.cmbAnalysisAccountItems = QtGui.QComboBox(FinanceExpensesSetupDialog)
        self.cmbAnalysisAccountItems.setObjectName(_fromUtf8("cmbAnalysisAccountItems"))
        self.cmbAnalysisAccountItems.addItem(_fromUtf8(""))
        self.cmbAnalysisAccountItems.addItem(_fromUtf8(""))
        self.cmbAnalysisAccountItems.addItem(_fromUtf8(""))
        self.cmbAnalysisAccountItems.addItem(_fromUtf8(""))
        self.cmbAnalysisAccountItems.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbAnalysisAccountItems, 6, 2, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblSpeciality.setBuddy(self.cmbSpeciality)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblInsurerDoctors.setBuddy(self.cmbInsurerDoctors)

        self.retranslateUi(FinanceExpensesSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FinanceExpensesSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FinanceExpensesSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FinanceExpensesSetupDialog)
        FinanceExpensesSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        FinanceExpensesSetupDialog.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        FinanceExpensesSetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbSpeciality)
        FinanceExpensesSetupDialog.setTabOrder(self.cmbSpeciality, self.cmbPerson)
        FinanceExpensesSetupDialog.setTabOrder(self.cmbPerson, self.cmbInsurerDoctors)
        FinanceExpensesSetupDialog.setTabOrder(self.cmbInsurerDoctors, self.cmbAnalysisAccountItems)
        FinanceExpensesSetupDialog.setTabOrder(self.cmbAnalysisAccountItems, self.buttonBox)

    def retranslateUi(self, FinanceExpensesSetupDialog):
        FinanceExpensesSetupDialog.setWindowTitle(QtGui.QApplication.translate("FinanceExpensesSetupDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("FinanceExpensesSetupDialog", "Дата &начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("FinanceExpensesSetupDialog", "Дата &окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("FinanceExpensesSetupDialog", "&Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSpeciality.setText(QtGui.QApplication.translate("FinanceExpensesSetupDialog", "&Специальность", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSpeciality.setWhatsThis(QtGui.QApplication.translate("FinanceExpensesSetupDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPerson.setText(QtGui.QApplication.translate("FinanceExpensesSetupDialog", "&Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.lblInsurerDoctors.setText(QtGui.QApplication.translate("FinanceExpensesSetupDialog", "&СМО", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAnalysisAccountItems.setText(QtGui.QApplication.translate("FinanceExpensesSetupDialog", "Статус оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAnalysisAccountItems.setItemText(0, QtGui.QApplication.translate("FinanceExpensesSetupDialog", "Все", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAnalysisAccountItems.setItemText(1, QtGui.QApplication.translate("FinanceExpensesSetupDialog", "Без подтверждения", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAnalysisAccountItems.setItemText(2, QtGui.QApplication.translate("FinanceExpensesSetupDialog", "Подтверждённые", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAnalysisAccountItems.setItemText(3, QtGui.QApplication.translate("FinanceExpensesSetupDialog", "Оплаченные", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAnalysisAccountItems.setItemText(4, QtGui.QApplication.translate("FinanceExpensesSetupDialog", "Отказанные", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.OrgComboBox import CInsurerComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    FinanceExpensesSetupDialog = QtGui.QDialog()
    ui = Ui_FinanceExpensesSetupDialog()
    ui.setupUi(FinanceExpensesSetupDialog)
    FinanceExpensesSetupDialog.show()
    sys.exit(app.exec_())

