# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportF13Setup.ui'
#
# Created: Tue Jun 17 18:00:26 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_ReportF13SetupDialog(object):
    def setupUi(self, ReportF13SetupDialog):
        ReportF13SetupDialog.setObjectName(_fromUtf8("ReportF13SetupDialog"))
        ReportF13SetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportF13SetupDialog.resize(394, 224)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportF13SetupDialog.sizePolicy().hasHeightForWidth())
        ReportF13SetupDialog.setSizePolicy(sizePolicy)
        ReportF13SetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportF13SetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportF13SetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportF13SetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportF13SetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(ReportF13SetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportF13SetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 2, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportF13SetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 2, 1, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportF13SetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 3, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportF13SetupDialog)
        self.cmbPerson.setEnabled(True)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 3, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportF13SetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 4, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportF13SetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 4, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportF13SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblPerson.setBuddy(self.cmbPerson)

        self.retranslateUi(ReportF13SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF13SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF13SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF13SetupDialog)

    def retranslateUi(self, ReportF13SetupDialog):
        ReportF13SetupDialog.setWindowTitle(_translate("ReportF13SetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportF13SetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportF13SetupDialog", "Дата окончания периода", None))
        self.lblEventType.setText(_translate("ReportF13SetupDialog", "&Тип обращения", None))
        self.cmbEventType.setWhatsThis(_translate("ReportF13SetupDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.lblPerson.setText(_translate("ReportF13SetupDialog", "&Врач", None))
        self.lblOrgStructure.setText(_translate("ReportF13SetupDialog", "Подразделение", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
