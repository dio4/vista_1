# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TimelineSetupDialog.ui'
#
# Created: Mon Jul 21 17:37:59 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_TimelineSetupDialog(object):
    def setupUi(self, TimelineSetupDialog):
        TimelineSetupDialog.setObjectName(_fromUtf8("TimelineSetupDialog"))
        TimelineSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        TimelineSetupDialog.resize(345, 176)
        TimelineSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(TimelineSetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(TimelineSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 4)
        self.lblBegDate = QtGui.QLabel(TimelineSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.edtBegDate = CDateEdit(TimelineSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(101, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.lblEndDate = QtGui.QLabel(TimelineSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        self.edtEndDate = CDateEdit(TimelineSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(101, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 3, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(TimelineSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(TimelineSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 2, 1, 2)
        self.lblSpeciality = QtGui.QLabel(TimelineSetupDialog)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout.addWidget(self.lblSpeciality, 3, 0, 1, 2)
        self.cmbSpeciality = CRBComboBox(TimelineSetupDialog)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 3, 2, 1, 2)
        self.lblPerson = QtGui.QLabel(TimelineSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 4, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(TimelineSetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 4, 2, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(21, 21, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 6, 0, 1, 1)
        self.chkCommon = QtGui.QCheckBox(TimelineSetupDialog)
        self.chkCommon.setObjectName(_fromUtf8("chkCommon"))
        self.gridLayout.addWidget(self.chkCommon, 5, 0, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblSpeciality.setBuddy(self.cmbSpeciality)
        self.lblPerson.setBuddy(self.cmbPerson)

        self.retranslateUi(TimelineSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TimelineSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TimelineSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TimelineSetupDialog)
        TimelineSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        TimelineSetupDialog.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        TimelineSetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbSpeciality)
        TimelineSetupDialog.setTabOrder(self.cmbSpeciality, self.cmbPerson)
        TimelineSetupDialog.setTabOrder(self.cmbPerson, self.buttonBox)

    def retranslateUi(self, TimelineSetupDialog):
        TimelineSetupDialog.setWindowTitle(_translate("TimelineSetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("TimelineSetupDialog", "Дата &начала периода", None))
        self.edtBegDate.setDisplayFormat(_translate("TimelineSetupDialog", "dd.MM.yyyy", None))
        self.lblEndDate.setText(_translate("TimelineSetupDialog", "Дата &окончания периода", None))
        self.edtEndDate.setDisplayFormat(_translate("TimelineSetupDialog", "dd.MM.yyyy", None))
        self.lblOrgStructure.setText(_translate("TimelineSetupDialog", "&Подразделение", None))
        self.lblSpeciality.setText(_translate("TimelineSetupDialog", "&Специальность", None))
        self.cmbSpeciality.setWhatsThis(_translate("TimelineSetupDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.lblPerson.setText(_translate("TimelineSetupDialog", "&Врач", None))
        self.chkCommon.setText(_translate("TimelineSetupDialog", "Общее расписание", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
