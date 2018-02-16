# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportDuplicateEventsSetup.ui'
#
# Created: Wed Jul 08 19:39:40 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_ReportDuplicateEventsSetupDialog(object):
    def setupUi(self, ReportDuplicateEventsSetupDialog):
        ReportDuplicateEventsSetupDialog.setObjectName(_fromUtf8("ReportDuplicateEventsSetupDialog"))
        ReportDuplicateEventsSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportDuplicateEventsSetupDialog.resize(397, 203)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportDuplicateEventsSetupDialog.sizePolicy().hasHeightForWidth())
        ReportDuplicateEventsSetupDialog.setSizePolicy(sizePolicy)
        ReportDuplicateEventsSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportDuplicateEventsSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbSpeciality = CRBComboBox(ReportDuplicateEventsSetupDialog)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 5, 1, 1, 1)
        self.edtBegDate = CDateEdit(ReportDuplicateEventsSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportDuplicateEventsSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportDuplicateEventsSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 4, 1, 1, 1)
        self.cmbEventType = CRBComboBox(ReportDuplicateEventsSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 3, 1, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportDuplicateEventsSetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 6, 1, 1, 1)
        self.edtEndDate = CDateEdit(ReportDuplicateEventsSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportDuplicateEventsSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 3, 0, 1, 1)
        self.label_4 = QtGui.QLabel(ReportDuplicateEventsSetupDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)
        self.label_2 = QtGui.QLabel(ReportDuplicateEventsSetupDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 6, 0, 1, 1)
        self.label = QtGui.QLabel(ReportDuplicateEventsSetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportDuplicateEventsSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportDuplicateEventsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 12, 0, 1, 2)
        self.rb1 = QtGui.QRadioButton(ReportDuplicateEventsSetupDialog)
        self.rb1.setText(_fromUtf8(""))
        self.rb1.setChecked(True)
        self.rb1.setObjectName(_fromUtf8("rb1"))
        self.gridLayout.addWidget(self.rb1, 7, 1, 1, 1)
        self.label_3 = QtGui.QLabel(ReportDuplicateEventsSetupDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 7, 0, 1, 1)
        self.rb2 = QtGui.QRadioButton(ReportDuplicateEventsSetupDialog)
        self.rb2.setText(_fromUtf8(""))
        self.rb2.setObjectName(_fromUtf8("rb2"))
        self.gridLayout.addWidget(self.rb2, 8, 1, 1, 1)
        self.label_5 = QtGui.QLabel(ReportDuplicateEventsSetupDialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 8, 0, 1, 1)
        self.lblEventType.setBuddy(self.cmbEventType)

        self.retranslateUi(ReportDuplicateEventsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportDuplicateEventsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportDuplicateEventsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportDuplicateEventsSetupDialog)

    def retranslateUi(self, ReportDuplicateEventsSetupDialog):
        ReportDuplicateEventsSetupDialog.setWindowTitle(_translate("ReportDuplicateEventsSetupDialog", "параметры отчёта", None))
        self.lblEndDate.setText(_translate("ReportDuplicateEventsSetupDialog", "Дата окончания периода", None))
        self.lblEventType.setText(_translate("ReportDuplicateEventsSetupDialog", "&Тип обращения", None))
        self.label_4.setText(_translate("ReportDuplicateEventsSetupDialog", "Специальность", None))
        self.label_2.setText(_translate("ReportDuplicateEventsSetupDialog", "Врач", None))
        self.label.setText(_translate("ReportDuplicateEventsSetupDialog", "Подразделение", None))
        self.lblBegDate.setText(_translate("ReportDuplicateEventsSetupDialog", "Дата начала периода", None))
        self.label_3.setText(_translate("ReportDuplicateEventsSetupDialog", "По дате окончания лечения", None))
        self.label_5.setText(_translate("ReportDuplicateEventsSetupDialog", "По расчетной дате реестра", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
