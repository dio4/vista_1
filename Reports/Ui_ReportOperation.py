# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportOperation.ui'
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

class Ui_ReportOperation(object):
    def setupUi(self, ReportOperation):
        ReportOperation.setObjectName(_fromUtf8("ReportOperation"))
        ReportOperation.resize(411, 501)
        self.gridLayout = QtGui.QGridLayout(ReportOperation)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btnPerson = QtGui.QRadioButton(ReportOperation)
        self.btnPerson.setChecked(True)
        self.btnPerson.setObjectName(_fromUtf8("btnPerson"))
        self.gridLayout.addWidget(self.btnPerson, 8, 5, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportOperation)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 9, 4, 1, 5)
        self.lblBegDate = QtGui.QLabel(ReportOperation)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 1, 1, 4)
        self.lblEndDate = QtGui.QLabel(ReportOperation)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 1, 1, 4)
        self.chkOrgStructure = QtGui.QCheckBox(ReportOperation)
        self.chkOrgStructure.setObjectName(_fromUtf8("chkOrgStructure"))
        self.gridLayout.addWidget(self.chkOrgStructure, 9, 1, 1, 3)
        self.edtEndDate = CDateEdit(ReportOperation)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 5, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportOperation)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 12, 4, 1, 5)
        self.edtBegDate = CDateEdit(ReportOperation)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 5, 1, 1)
        self.lstOrgStructure = CRBListBox(ReportOperation)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridLayout.addWidget(self.lstOrgStructure, 10, 1, 1, 8)
        self.chkOperation = QtGui.QCheckBox(ReportOperation)
        self.chkOperation.setObjectName(_fromUtf8("chkOperation"))
        self.gridLayout.addWidget(self.chkOperation, 14, 1, 1, 3)
        self.cmbOperation = CRBComboBox(ReportOperation)
        self.cmbOperation.setObjectName(_fromUtf8("cmbOperation"))
        self.gridLayout.addWidget(self.cmbOperation, 14, 4, 1, 5)
        self.lstOperation = CRBListBox(ReportOperation)
        self.lstOperation.setObjectName(_fromUtf8("lstOperation"))
        self.gridLayout.addWidget(self.lstOperation, 16, 1, 1, 8)
        self.buttonBox = QtGui.QDialogButtonBox(ReportOperation)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 19, 8, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 8, 1, 1)
        self.label = QtGui.QLabel(ReportOperation)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 12, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ReportOperation)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 8, 1, 1, 1)
        self.btnOrgStructure = QtGui.QRadioButton(ReportOperation)
        self.btnOrgStructure.setObjectName(_fromUtf8("btnOrgStructure"))
        self.gridLayout.addWidget(self.btnOrgStructure, 8, 8, 1, 1)
        self.lblAge = QtGui.QLabel(ReportOperation)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout.addWidget(self.lblAge, 2, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_3 = QtGui.QLabel(ReportOperation)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.edtAgeFrom = QtGui.QSpinBox(ReportOperation)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeFrom.sizePolicy().hasHeightForWidth())
        self.edtAgeFrom.setSizePolicy(sizePolicy)
        self.edtAgeFrom.setMaximum(150)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self.horizontalLayout.addWidget(self.edtAgeFrom)
        self.lblAgeTo = QtGui.QLabel(ReportOperation)
        self.lblAgeTo.setObjectName(_fromUtf8("lblAgeTo"))
        self.horizontalLayout.addWidget(self.lblAgeTo)
        self.edtAgeTo = QtGui.QSpinBox(ReportOperation)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeTo.sizePolicy().hasHeightForWidth())
        self.edtAgeTo.setSizePolicy(sizePolicy)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self.horizontalLayout.addWidget(self.edtAgeTo)
        self.lblAgeYears = QtGui.QLabel(ReportOperation)
        self.lblAgeYears.setObjectName(_fromUtf8("lblAgeYears"))
        self.horizontalLayout.addWidget(self.lblAgeYears)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 5, 1, 4)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 17, 2, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblAge.setBuddy(self.edtAgeFrom)
        self.lblAgeTo.setBuddy(self.edtAgeTo)
        self.lblAgeYears.setBuddy(self.edtAgeTo)

        self.retranslateUi(ReportOperation)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportOperation.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportOperation.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportOperation)

    def retranslateUi(self, ReportOperation):
        ReportOperation.setWindowTitle(_translate("ReportOperation", "Dialog", None))
        self.btnPerson.setText(_translate("ReportOperation", "Врачам", None))
        self.lblBegDate.setText(_translate("ReportOperation", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportOperation", "Дата окончания периода", None))
        self.chkOrgStructure.setText(_translate("ReportOperation", "Подразделение", None))
        self.chkOperation.setText(_translate("ReportOperation", "Операция", None))
        self.label.setText(_translate("ReportOperation", "Врач", None))
        self.label_2.setText(_translate("ReportOperation", "Отчет по", None))
        self.btnOrgStructure.setText(_translate("ReportOperation", "Подразделениям", None))
        self.lblAge.setText(_translate("ReportOperation", "Во&зраст", None))
        self.label_3.setText(_translate("ReportOperation", "c", None))
        self.lblAgeTo.setText(_translate("ReportOperation", "по", None))
        self.lblAgeYears.setText(_translate("ReportOperation", "лет", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
from library.crbcombobox import CRBComboBox
