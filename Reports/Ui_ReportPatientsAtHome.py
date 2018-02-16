# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPatientsAtHome.ui'
#
# Created: Tue Mar 11 17:59:58 2014
#      by: PyQt4 UI code generator 4.10
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

class Ui_ReportPatientAtHome(object):
    def setupUi(self, ReportPatientAtHome):
        ReportPatientAtHome.setObjectName(_fromUtf8("ReportPatientAtHome"))
        ReportPatientAtHome.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportPatientAtHome.resize(425, 392)
        ReportPatientAtHome.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ReportPatientAtHome)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.cmbEventType = CRBComboBox(ReportPatientAtHome)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridlayout.addWidget(self.cmbEventType, 2, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportPatientAtHome)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridlayout.addWidget(self.lblOrgStructure, 7, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.label_2 = QtGui.QLabel(ReportPatientAtHome)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridlayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportPatientAtHome)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridlayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportPatientAtHome)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridlayout.addWidget(self.cmbOrgStructure, 7, 1, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportPatientAtHome)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridlayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportPatientAtHome)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbPerson, 8, 1, 1, 2)
        self.lblRowGrouping = QtGui.QLabel(ReportPatientAtHome)
        self.lblRowGrouping.setObjectName(_fromUtf8("lblRowGrouping"))
        self.gridlayout.addWidget(self.lblRowGrouping, 10, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportPatientAtHome)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridlayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.edtBegDate = CDateEdit(ReportPatientAtHome)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridlayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportPatientAtHome)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 14, 0, 1, 3)
        self.cmbSex = QtGui.QComboBox(ReportPatientAtHome)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSex.sizePolicy().hasHeightForWidth())
        self.cmbSex.setSizePolicy(sizePolicy)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbSex, 9, 1, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportPatientAtHome)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridlayout.addWidget(self.lblPerson, 8, 0, 1, 1)
        self.cmbRowGrouping = QtGui.QComboBox(ReportPatientAtHome)
        self.cmbRowGrouping.setObjectName(_fromUtf8("cmbRowGrouping"))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbRowGrouping, 10, 1, 1, 2)
        self.label = QtGui.QLabel(ReportPatientAtHome)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 2, 0, 1, 1)
        self.lblSex = QtGui.QLabel(ReportPatientAtHome)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridlayout.addWidget(self.lblSex, 9, 0, 1, 1)
        self.label_3 = QtGui.QLabel(ReportPatientAtHome)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridlayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.cmbSocStatusClass = CSocStatusComboBox(ReportPatientAtHome)
        self.cmbSocStatusClass.setObjectName(_fromUtf8("cmbSocStatusClass"))
        self.gridlayout.addWidget(self.cmbSocStatusClass, 3, 1, 1, 2)
        self.cmbSocStatusType = CRBComboBox(ReportPatientAtHome)
        self.cmbSocStatusType.setObjectName(_fromUtf8("cmbSocStatusType"))
        self.gridlayout.addWidget(self.cmbSocStatusType, 4, 1, 1, 2)
        self.chkGroup = QtGui.QCheckBox(ReportPatientAtHome)
        self.chkGroup.setObjectName(_fromUtf8("chkGroup"))
        self.gridlayout.addWidget(self.chkGroup, 11, 1, 1, 1)
        self.chkRegAddress = QtGui.QCheckBox(ReportPatientAtHome)
        self.chkRegAddress.setObjectName(_fromUtf8("chkRegAddress"))
        self.gridlayout.addWidget(self.chkRegAddress, 12, 1, 1, 1)
        self.chkAddress = QtGui.QCheckBox(ReportPatientAtHome)
        self.chkAddress.setObjectName(_fromUtf8("chkAddress"))
        self.gridlayout.addWidget(self.chkAddress, 13, 1, 1, 1)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblRowGrouping.setBuddy(self.cmbRowGrouping)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblSex.setBuddy(self.cmbSex)

        self.retranslateUi(ReportPatientAtHome)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportPatientAtHome.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportPatientAtHome.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportPatientAtHome)
        ReportPatientAtHome.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportPatientAtHome.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        ReportPatientAtHome.setTabOrder(self.cmbOrgStructure, self.cmbPerson)
        ReportPatientAtHome.setTabOrder(self.cmbPerson, self.cmbSex)
        ReportPatientAtHome.setTabOrder(self.cmbSex, self.cmbRowGrouping)
        ReportPatientAtHome.setTabOrder(self.cmbRowGrouping, self.buttonBox)

    def retranslateUi(self, ReportPatientAtHome):
        ReportPatientAtHome.setWindowTitle(_translate("ReportPatientAtHome", "параметры отчёта", None))
        self.lblOrgStructure.setText(_translate("ReportPatientAtHome", "&Подразделение", None))
        self.label_2.setText(_translate("ReportPatientAtHome", "Тип соц. статуса", None))
        self.lblBegDate.setText(_translate("ReportPatientAtHome", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportPatientAtHome", "Дата &окончания периода", None))
        self.cmbPerson.setItemText(0, _translate("ReportPatientAtHome", "Врач", None))
        self.lblRowGrouping.setText(_translate("ReportPatientAtHome", "&Строки по", None))
        self.cmbSex.setItemText(1, _translate("ReportPatientAtHome", "М", None))
        self.cmbSex.setItemText(2, _translate("ReportPatientAtHome", "Ж", None))
        self.lblPerson.setText(_translate("ReportPatientAtHome", "&Врач", None))
        self.cmbRowGrouping.setItemText(0, _translate("ReportPatientAtHome", "Датам", None))
        self.cmbRowGrouping.setItemText(1, _translate("ReportPatientAtHome", "Врачам", None))
        self.cmbRowGrouping.setItemText(2, _translate("ReportPatientAtHome", "Подразделениям", None))
        self.cmbRowGrouping.setItemText(3, _translate("ReportPatientAtHome", "Специальности", None))
        self.cmbRowGrouping.setItemText(4, _translate("ReportPatientAtHome", "Должности", None))
        self.cmbRowGrouping.setItemText(5, _translate("ReportPatientAtHome", "Пациентам", None))
        self.label.setText(_translate("ReportPatientAtHome", "Тип события", None))
        self.lblSex.setText(_translate("ReportPatientAtHome", "По&л", None))
        self.label_3.setText(_translate("ReportPatientAtHome", "Класс соц. статуса", None))
        self.chkGroup.setText(_translate("ReportPatientAtHome", "Группировать по отделениям", None))
        self.chkRegAddress.setText(_translate("ReportPatientAtHome", "Выводить адрес регистрации", None))
        self.chkAddress.setText(_translate("ReportPatientAtHome", "Выводить адрес проживания", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from Registry.SocStatusComboBox import CSocStatusComboBox
