# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportStandart.ui'
#
# Created: Wed Apr 08 17:34:13 2015
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

class Ui_ReportStandart(object):
    def setupUi(self, ReportStandart):
        ReportStandart.setObjectName(_fromUtf8("ReportStandart"))
        ReportStandart.resize(400, 459)
        self.gridLayout = QtGui.QGridLayout(ReportStandart)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtEndDate = CDateEdit(ReportStandart)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportStandart)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 11, 0, 1, 6)
        self.lblEndDate = QtGui.QLabel(ReportStandart)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        self.label_2 = QtGui.QLabel(ReportStandart)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 2)
        self.edtBegDate = CDateEdit(ReportStandart)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportStandart)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.cmbHospitalization = QtGui.QComboBox(ReportStandart)
        self.cmbHospitalization.setObjectName(_fromUtf8("cmbHospitalization"))
        self.cmbHospitalization.addItem(_fromUtf8(""))
        self.cmbHospitalization.addItem(_fromUtf8(""))
        self.cmbHospitalization.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbHospitalization, 2, 2, 1, 4)
        self.cmbOrgStructure = COrgStructureComboBox(ReportStandart)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 7, 2, 1, 4)
        self.lblOrgStructure = QtGui.QLabel(ReportStandart)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 7, 0, 1, 2)
        self.cmbInsurerFilterDialog = CInsurerComboBox(ReportStandart)
        self.cmbInsurerFilterDialog.setObjectName(_fromUtf8("cmbInsurerFilterDialog"))
        self.gridLayout.addWidget(self.cmbInsurerFilterDialog, 6, 2, 1, 4)
        self.label = QtGui.QLabel(ReportStandart)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 6, 0, 1, 2)
        self.cmbStandart = CMESComboBox(ReportStandart)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbStandart.sizePolicy().hasHeightForWidth())
        self.cmbStandart.setSizePolicy(sizePolicy)
        self.cmbStandart.setObjectName(_fromUtf8("cmbStandart"))
        self.gridLayout.addWidget(self.cmbStandart, 4, 2, 1, 4)
        self.lblPerson = QtGui.QLabel(ReportStandart)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 8, 0, 1, 2)
        self.cmbPerson = CPersonComboBoxEx(ReportStandart)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbPerson, 8, 2, 1, 4)
        self.chkStandart = QtGui.QCheckBox(ReportStandart)
        self.chkStandart.setObjectName(_fromUtf8("chkStandart"))
        self.gridLayout.addWidget(self.chkStandart, 4, 0, 1, 2)
        self.lstStandart = CRBListBox(ReportStandart)
        self.lstStandart.setObjectName(_fromUtf8("lstStandart"))
        self.gridLayout.addWidget(self.lstStandart, 5, 0, 1, 6)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 10, 0, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportStandart)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportStandart.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportStandart.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportStandart)

    def retranslateUi(self, ReportStandart):
        ReportStandart.setWindowTitle(_translate("ReportStandart", "Dialog", None))
        self.lblEndDate.setText(_translate("ReportStandart", "Дата &окончания периода", None))
        self.label_2.setText(_translate("ReportStandart", "Тип госпитализации", None))
        self.lblBegDate.setText(_translate("ReportStandart", "Дата &начала периода", None))
        self.cmbHospitalization.setItemText(0, _translate("ReportStandart", "не задано", None))
        self.cmbHospitalization.setItemText(1, _translate("ReportStandart", "Круглосуточная", None))
        self.cmbHospitalization.setItemText(2, _translate("ReportStandart", "Дневная", None))
        self.lblOrgStructure.setText(_translate("ReportStandart", "Подразделение", None))
        self.label.setText(_translate("ReportStandart", "Страховая организация", None))
        self.lblPerson.setText(_translate("ReportStandart", "Врач", None))
        self.cmbPerson.setItemText(0, _translate("ReportStandart", "Врач", None))
        self.chkStandart.setText(_translate("ReportStandart", "Стандарт", None))

from Orgs.OrgComboBox import CInsurerComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.RBListBox import CRBListBox
from library.DateEdit import CDateEdit
from library.MES.MESComboBox import CMESComboBox
