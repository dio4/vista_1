# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\ReportOnPersonSetupDialog.ui'
#
# Created: Fri Jun 15 12:17:20 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportOnPersonSetupDialog(object):
    def setupUi(self, ReportOnPersonSetupDialog):
        ReportOnPersonSetupDialog.setObjectName(_fromUtf8("ReportOnPersonSetupDialog"))
        ReportOnPersonSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportOnPersonSetupDialog.resize(467, 236)
        ReportOnPersonSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportOnPersonSetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportOnPersonSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportOnPersonSetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportOnPersonSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportOnPersonSetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportOnPersonSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportOnPersonSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 2)
        self.lblSpec = QtGui.QLabel(ReportOnPersonSetupDialog)
        self.lblSpec.setObjectName(_fromUtf8("lblSpec"))
        self.gridLayout.addWidget(self.lblSpec, 3, 0, 1, 1)
        self.cmbSpeciality = CRBComboBox(ReportOnPersonSetupDialog)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 3, 1, 1, 2)
        self.lblPerson = QtGui.QLabel(ReportOnPersonSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 4, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportOnPersonSetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbPerson, 4, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(111, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 6, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ReportOnPersonSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 3)
        self.lblIdentifierType = QtGui.QLabel(ReportOnPersonSetupDialog)
        self.lblIdentifierType.setObjectName(_fromUtf8("lblIdentifierType"))
        self.gridLayout.addWidget(self.lblIdentifierType, 5, 0, 1, 1)
        self.cmbIdentifierType = QtGui.QComboBox(ReportOnPersonSetupDialog)
        self.cmbIdentifierType.setObjectName(_fromUtf8("cmbIdentifierType"))
        self.cmbIdentifierType.addItem(_fromUtf8(""))
        self.cmbIdentifierType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbIdentifierType, 5, 1, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblOrgStructure.setBuddy(self.cmbPerson)
        self.lblSpec.setBuddy(self.cmbPerson)
        self.lblPerson.setBuddy(self.cmbPerson)

        self.retranslateUi(ReportOnPersonSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportOnPersonSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportOnPersonSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportOnPersonSetupDialog)
        ReportOnPersonSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportOnPersonSetupDialog.setTabOrder(self.edtEndDate, self.buttonBox)

    def retranslateUi(self, ReportOnPersonSetupDialog):
        ReportOnPersonSetupDialog.setWindowTitle(QtGui.QApplication.translate("ReportOnPersonSetupDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("ReportOnPersonSetupDialog", "Дата начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("ReportOnPersonSetupDialog", "Дата окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("ReportOnPersonSetupDialog", "Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSpec.setText(QtGui.QApplication.translate("ReportOnPersonSetupDialog", "Специальность", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSpeciality.setWhatsThis(QtGui.QApplication.translate("ReportOnPersonSetupDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPerson.setText(QtGui.QApplication.translate("ReportOnPersonSetupDialog", "&Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPerson.setItemText(0, QtGui.QApplication.translate("ReportOnPersonSetupDialog", "Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.lblIdentifierType.setText(QtGui.QApplication.translate("ReportOnPersonSetupDialog", "Тип идентификатора", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbIdentifierType.setItemText(0, QtGui.QApplication.translate("ReportOnPersonSetupDialog", "Идентификатор клиента", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbIdentifierType.setItemText(1, QtGui.QApplication.translate("ReportOnPersonSetupDialog", "Идентификатор во внешней учётной системе", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportOnPersonSetupDialog = QtGui.QDialog()
    ui = Ui_ReportOnPersonSetupDialog()
    ui.setupUi(ReportOnPersonSetupDialog)
    ReportOnPersonSetupDialog.show()
    sys.exit(app.exec_())

