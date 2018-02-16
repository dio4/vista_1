# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPeriodontist.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_ReportPeriodontist(object):
    def setupUi(self, ReportPeriodontist):
        ReportPeriodontist.setObjectName(_fromUtf8("ReportPeriodontist"))
        ReportPeriodontist.resize(401, 272)
        self.gridLayout = QtGui.QGridLayout(ReportPeriodontist)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbOrgStructure = COrgStructureComboBox(ReportPeriodontist)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 8, 4, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportPeriodontist)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 13, 5, 1, 1)
        self.edtEndDate = CDateEdit(ReportPeriodontist)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 4, 2, 1)
        self.label_2 = QtGui.QLabel(ReportPeriodontist)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 5, 1, 1, 1)
        self.label = QtGui.QLabel(ReportPeriodontist)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 7, 1, 1, 1)
        self.edtBegDate = CDateEdit(ReportPeriodontist)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 4, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportPeriodontist)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 1, 1, 3)
        self.label_3 = QtGui.QLabel(ReportPeriodontist)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 10, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportPeriodontist)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 1, 2, 3)
        self.cmbEventPurpose = CRBComboBox(ReportPeriodontist)
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.gridLayout.addWidget(self.cmbEventPurpose, 4, 4, 1, 2)
        self.cmbPerson = CPersonComboBoxEx(ReportPeriodontist)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 10, 4, 1, 2)
        self.lblEventPurpose = QtGui.QLabel(ReportPeriodontist)
        self.lblEventPurpose.setObjectName(_fromUtf8("lblEventPurpose"))
        self.gridLayout.addWidget(self.lblEventPurpose, 4, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 5, 1, 1)
        self.cmbEventType = CRBComboBox(ReportPeriodontist)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 5, 4, 1, 2)
        self.cmbSpeciality = CRBComboBox(ReportPeriodontist)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 7, 4, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(ReportPeriodontist)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 8, 1, 1, 1)
        self.chkDetailPerson = QtGui.QCheckBox(ReportPeriodontist)
        self.chkDetailPerson.setObjectName(_fromUtf8("chkDetailPerson"))
        self.gridLayout.addWidget(self.chkDetailPerson, 12, 1, 1, 5)
        self.cmbActionType = QtGui.QComboBox(ReportPeriodontist)
        self.cmbActionType.setObjectName(_fromUtf8("cmbActionType"))
        self.cmbActionType.addItem(_fromUtf8(""))
        self.cmbActionType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbActionType, 3, 4, 1, 1)
        self.lblActionType = QtGui.QLabel(ReportPeriodontist)
        self.lblActionType.setObjectName(_fromUtf8("lblActionType"))
        self.gridLayout.addWidget(self.lblActionType, 3, 1, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportPeriodontist)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportPeriodontist.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportPeriodontist.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportPeriodontist)

    def retranslateUi(self, ReportPeriodontist):
        ReportPeriodontist.setWindowTitle(_translate("ReportPeriodontist", "Dialog", None))
        self.label_2.setText(_translate("ReportPeriodontist", "Тип обращения", None))
        self.label.setText(_translate("ReportPeriodontist", "Специальность", None))
        self.lblBegDate.setText(_translate("ReportPeriodontist", "Дата &начала периода", None))
        self.label_3.setText(_translate("ReportPeriodontist", "Врач", None))
        self.lblEndDate.setText(_translate("ReportPeriodontist", "Дата &окончания периода", None))
        self.lblEventPurpose.setText(_translate("ReportPeriodontist", "Назначение обращения", None))
        self.lblOrgStructure.setText(_translate("ReportPeriodontist", "Подразделение", None))
        self.chkDetailPerson.setText(_translate("ReportPeriodontist", "Детализировать по врачам", None))
        self.cmbActionType.setItemText(0, _translate("ReportPeriodontist", "з", None))
        self.cmbActionType.setItemText(1, _translate("ReportPeriodontist", "стх", None))
        self.lblActionType.setText(_translate("ReportPeriodontist", "Тип услуг", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
