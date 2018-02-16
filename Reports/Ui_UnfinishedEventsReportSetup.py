# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\UnfinishedEventsReportSetup.ui'
#
# Created: Fri Jun 15 12:16:30 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_UnfinishedEventsReportSetupDialog(object):
    def setupUi(self, UnfinishedEventsReportSetupDialog):
        UnfinishedEventsReportSetupDialog.setObjectName(_fromUtf8("UnfinishedEventsReportSetupDialog"))
        UnfinishedEventsReportSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        UnfinishedEventsReportSetupDialog.resize(341, 234)
        UnfinishedEventsReportSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(UnfinishedEventsReportSetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(UnfinishedEventsReportSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(UnfinishedEventsReportSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(UnfinishedEventsReportSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(UnfinishedEventsReportSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.lblEventPurpose = QtGui.QLabel(UnfinishedEventsReportSetupDialog)
        self.lblEventPurpose.setObjectName(_fromUtf8("lblEventPurpose"))
        self.gridLayout.addWidget(self.lblEventPurpose, 2, 0, 1, 1)
        self.cmbEventPurpose = CRBComboBox(UnfinishedEventsReportSetupDialog)
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.gridLayout.addWidget(self.cmbEventPurpose, 2, 1, 1, 2)
        self.lblEventType = QtGui.QLabel(UnfinishedEventsReportSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 3, 0, 1, 1)
        self.cmbEventType = CRBComboBox(UnfinishedEventsReportSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 3, 1, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(UnfinishedEventsReportSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 4, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(UnfinishedEventsReportSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 4, 1, 1, 2)
        self.lblSpeciality = QtGui.QLabel(UnfinishedEventsReportSetupDialog)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout.addWidget(self.lblSpeciality, 5, 0, 1, 1)
        self.cmbSpeciality = CRBComboBox(UnfinishedEventsReportSetupDialog)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 5, 1, 1, 2)
        self.lblPerson = QtGui.QLabel(UnfinishedEventsReportSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 6, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(UnfinishedEventsReportSetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 6, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(129, 21, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 7, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(UnfinishedEventsReportSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblEventPurpose.setBuddy(self.cmbEventPurpose)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblSpeciality.setBuddy(self.cmbSpeciality)
        self.lblPerson.setBuddy(self.cmbPerson)

        self.retranslateUi(UnfinishedEventsReportSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), UnfinishedEventsReportSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), UnfinishedEventsReportSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(UnfinishedEventsReportSetupDialog)
        UnfinishedEventsReportSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        UnfinishedEventsReportSetupDialog.setTabOrder(self.edtEndDate, self.cmbEventPurpose)
        UnfinishedEventsReportSetupDialog.setTabOrder(self.cmbEventPurpose, self.cmbEventType)
        UnfinishedEventsReportSetupDialog.setTabOrder(self.cmbEventType, self.cmbOrgStructure)
        UnfinishedEventsReportSetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbSpeciality)
        UnfinishedEventsReportSetupDialog.setTabOrder(self.cmbSpeciality, self.cmbPerson)
        UnfinishedEventsReportSetupDialog.setTabOrder(self.cmbPerson, self.buttonBox)

    def retranslateUi(self, UnfinishedEventsReportSetupDialog):
        UnfinishedEventsReportSetupDialog.setWindowTitle(QtGui.QApplication.translate("UnfinishedEventsReportSetupDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("UnfinishedEventsReportSetupDialog", "Дата начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.edtBegDate.setDisplayFormat(QtGui.QApplication.translate("UnfinishedEventsReportSetupDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("UnfinishedEventsReportSetupDialog", "Дата окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.edtEndDate.setDisplayFormat(QtGui.QApplication.translate("UnfinishedEventsReportSetupDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventPurpose.setText(QtGui.QApplication.translate("UnfinishedEventsReportSetupDialog", "&Назначение обращения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventType.setText(QtGui.QApplication.translate("UnfinishedEventsReportSetupDialog", "&Тип обращения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("UnfinishedEventsReportSetupDialog", "&Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSpeciality.setText(QtGui.QApplication.translate("UnfinishedEventsReportSetupDialog", "&Специальность", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSpeciality.setWhatsThis(QtGui.QApplication.translate("UnfinishedEventsReportSetupDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPerson.setText(QtGui.QApplication.translate("UnfinishedEventsReportSetupDialog", "&Врач", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    UnfinishedEventsReportSetupDialog = QtGui.QDialog()
    ui = Ui_UnfinishedEventsReportSetupDialog()
    ui.setupUi(UnfinishedEventsReportSetupDialog)
    UnfinishedEventsReportSetupDialog.show()
    sys.exit(app.exec_())

