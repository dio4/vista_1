# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ReportAnalyticalTable.ui'
#
# Created: Tue Oct 13 15:26:52 2015
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

class Ui_ReportAnalyticalTable(object):
    def setupUi(self, ReportAnalyticalTable):
        ReportAnalyticalTable.setObjectName(_fromUtf8("ReportAnalyticalTable"))
        ReportAnalyticalTable.resize(967, 1015)
        self.gridLayout = QtGui.QGridLayout(ReportAnalyticalTable)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDiagType = QtGui.QLabel(ReportAnalyticalTable)
        self.lblDiagType.setObjectName(_fromUtf8("lblDiagType"))
        self.gridLayout.addWidget(self.lblDiagType, 4, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportAnalyticalTable)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lstEventType = CRBListBox(ReportAnalyticalTable)
        self.lstEventType.setObjectName(_fromUtf8("lstEventType"))
        self.gridLayout.addWidget(self.lstEventType, 7, 0, 1, 5)
        self.cmbResult = QtGui.QComboBox(ReportAnalyticalTable)
        self.cmbResult.setObjectName(_fromUtf8("cmbResult"))
        self.cmbResult.addItem(_fromUtf8(""))
        self.cmbResult.addItem(_fromUtf8(""))
        self.cmbResult.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbResult, 10, 1, 1, 4)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 4, 1, 1)
        self.lblMES = QtGui.QLabel(ReportAnalyticalTable)
        self.lblMES.setObjectName(_fromUtf8("lblMES"))
        self.gridLayout.addWidget(self.lblMES, 3, 0, 1, 1)
        self.lstOrgStructure = CRBListBox(ReportAnalyticalTable)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridLayout.addWidget(self.lstOrgStructure, 9, 0, 1, 5)
        self.lstFinance = CRBListBox(ReportAnalyticalTable)
        self.lstFinance.setObjectName(_fromUtf8("lstFinance"))
        self.gridLayout.addWidget(self.lstFinance, 12, 0, 1, 5)
        self.edtMESFrom = QtGui.QLineEdit(ReportAnalyticalTable)
        self.edtMESFrom.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMESFrom.sizePolicy().hasHeightForWidth())
        self.edtMESFrom.setSizePolicy(sizePolicy)
        self.edtMESFrom.setMaximumSize(QtCore.QSize(80, 16777215))
        self.edtMESFrom.setObjectName(_fromUtf8("edtMESFrom"))
        self.gridLayout.addWidget(self.edtMESFrom, 3, 2, 1, 1)
        self.edtMESTo = QtGui.QLineEdit(ReportAnalyticalTable)
        self.edtMESTo.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMESTo.sizePolicy().hasHeightForWidth())
        self.edtMESTo.setSizePolicy(sizePolicy)
        self.edtMESTo.setMaximumSize(QtCore.QSize(80, 16777215))
        self.edtMESTo.setObjectName(_fromUtf8("edtMESTo"))
        self.gridLayout.addWidget(self.edtMESTo, 3, 3, 1, 1)
        self.cmbMES = QtGui.QComboBox(ReportAnalyticalTable)
        self.cmbMES.setObjectName(_fromUtf8("cmbMES"))
        self.cmbMES.addItem(_fromUtf8(""))
        self.cmbMES.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbMES, 3, 1, 1, 1)
        self.edtBegDate = CDateEdit(ReportAnalyticalTable)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.chkFinanceMulti = QtGui.QCheckBox(ReportAnalyticalTable)
        self.chkFinanceMulti.setObjectName(_fromUtf8("chkFinanceMulti"))
        self.gridLayout.addWidget(self.chkFinanceMulti, 11, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportAnalyticalTable)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.cmbDiagnosisType = CRBComboBox(ReportAnalyticalTable)
        self.cmbDiagnosisType.setEnabled(True)
        self.cmbDiagnosisType.setObjectName(_fromUtf8("cmbDiagnosisType"))
        self.gridLayout.addWidget(self.cmbDiagnosisType, 4, 1, 1, 4)
        self.chkOrgStructureMulti = QtGui.QCheckBox(ReportAnalyticalTable)
        self.chkOrgStructureMulti.setObjectName(_fromUtf8("chkOrgStructureMulti"))
        self.gridLayout.addWidget(self.chkOrgStructureMulti, 8, 0, 1, 1)
        self.chkEventTypeMulti = QtGui.QCheckBox(ReportAnalyticalTable)
        self.chkEventTypeMulti.setObjectName(_fromUtf8("chkEventTypeMulti"))
        self.gridLayout.addWidget(self.chkEventTypeMulti, 5, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAnalyticalTable)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 15, 4, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportAnalyticalTable)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 8, 1, 1, 4)
        self.cmbFinance = CRBComboBox(ReportAnalyticalTable)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 11, 1, 1, 4)
        self.edtEndDate = CDateEdit(ReportAnalyticalTable)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.cmbEventType = CRBComboBox(ReportAnalyticalTable)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 5, 1, 1, 4)
        self.label = QtGui.QLabel(ReportAnalyticalTable)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 10, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 4, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblMKB = QtGui.QLabel(ReportAnalyticalTable)
        self.lblMKB.setObjectName(_fromUtf8("lblMKB"))
        self.horizontalLayout.addWidget(self.lblMKB)
        self.cmbMKBFilter = QtGui.QComboBox(ReportAnalyticalTable)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbMKBFilter.sizePolicy().hasHeightForWidth())
        self.cmbMKBFilter.setSizePolicy(sizePolicy)
        self.cmbMKBFilter.setObjectName(_fromUtf8("cmbMKBFilter"))
        self.cmbMKBFilter.addItem(_fromUtf8(""))
        self.cmbMKBFilter.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.cmbMKBFilter)
        self.edtMKBFrom = CICDCodeEdit(ReportAnalyticalTable)
        self.edtMKBFrom.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMKBFrom.sizePolicy().hasHeightForWidth())
        self.edtMKBFrom.setSizePolicy(sizePolicy)
        self.edtMKBFrom.setMaximumSize(QtCore.QSize(40, 16777215))
        self.edtMKBFrom.setMaxLength(6)
        self.edtMKBFrom.setObjectName(_fromUtf8("edtMKBFrom"))
        self.horizontalLayout.addWidget(self.edtMKBFrom)
        self.edtMKBTo = CICDCodeEdit(ReportAnalyticalTable)
        self.edtMKBTo.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMKBTo.sizePolicy().hasHeightForWidth())
        self.edtMKBTo.setSizePolicy(sizePolicy)
        self.edtMKBTo.setMaximumSize(QtCore.QSize(40, 16777215))
        self.edtMKBTo.setMaxLength(6)
        self.edtMKBTo.setObjectName(_fromUtf8("edtMKBTo"))
        self.horizontalLayout.addWidget(self.edtMKBTo)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 5)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 0, 4, 1, 1)
        self.groupBox = QtGui.QGroupBox(ReportAnalyticalTable)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.chkSetTime = QtGui.QCheckBox(self.groupBox)
        self.chkSetTime.setChecked(True)
        self.chkSetTime.setObjectName(_fromUtf8("chkSetTime"))
        self.gridLayout_2.addWidget(self.chkSetTime, 10, 2, 1, 1)
        self.chkExecDate = QtGui.QCheckBox(self.groupBox)
        self.chkExecDate.setChecked(True)
        self.chkExecDate.setObjectName(_fromUtf8("chkExecDate"))
        self.gridLayout_2.addWidget(self.chkExecDate, 11, 2, 1, 1)
        self.chkReceived = QtGui.QCheckBox(self.groupBox)
        self.chkReceived.setChecked(True)
        self.chkReceived.setObjectName(_fromUtf8("chkReceived"))
        self.gridLayout_2.addWidget(self.chkReceived, 0, 3, 1, 1)
        self.chkExecTime = QtGui.QCheckBox(self.groupBox)
        self.chkExecTime.setChecked(True)
        self.chkExecTime.setObjectName(_fromUtf8("chkExecTime"))
        self.gridLayout_2.addWidget(self.chkExecTime, 12, 2, 1, 1)
        self.chkArea = QtGui.QCheckBox(self.groupBox)
        self.chkArea.setChecked(True)
        self.chkArea.setObjectName(_fromUtf8("chkArea"))
        self.gridLayout_2.addWidget(self.chkArea, 10, 3, 1, 1)
        self.chkName = QtGui.QCheckBox(self.groupBox)
        self.chkName.setChecked(True)
        self.chkName.setObjectName(_fromUtf8("chkName"))
        self.gridLayout_2.addWidget(self.chkName, 3, 2, 1, 1)
        self.chkTime = QtGui.QCheckBox(self.groupBox)
        self.chkTime.setChecked(True)
        self.chkTime.setObjectName(_fromUtf8("chkTime"))
        self.gridLayout_2.addWidget(self.chkTime, 5, 2, 1, 1)
        self.chkStatus = QtGui.QCheckBox(self.groupBox)
        self.chkStatus.setChecked(True)
        self.chkStatus.setObjectName(_fromUtf8("chkStatus"))
        self.gridLayout_2.addWidget(self.chkStatus, 2, 2, 1, 1)
        self.chkActionPerson = QtGui.QCheckBox(self.groupBox)
        self.chkActionPerson.setChecked(True)
        self.chkActionPerson.setObjectName(_fromUtf8("chkActionPerson"))
        self.gridLayout_2.addWidget(self.chkActionPerson, 4, 2, 1, 1)
        self.chkWork = QtGui.QCheckBox(self.groupBox)
        self.chkWork.setChecked(True)
        self.chkWork.setObjectName(_fromUtf8("chkWork"))
        self.gridLayout_2.addWidget(self.chkWork, 12, 3, 1, 1)
        self.chkInhab = QtGui.QCheckBox(self.groupBox)
        self.chkInhab.setChecked(True)
        self.chkInhab.setObjectName(_fromUtf8("chkInhab"))
        self.gridLayout_2.addWidget(self.chkInhab, 11, 3, 1, 1)
        self.chkSetDate = QtGui.QCheckBox(self.groupBox)
        self.chkSetDate.setChecked(True)
        self.chkSetDate.setObjectName(_fromUtf8("chkSetDate"))
        self.gridLayout_2.addWidget(self.chkSetDate, 8, 2, 1, 1)
        self.chkPrimaryEvent = QtGui.QCheckBox(self.groupBox)
        self.chkPrimaryEvent.setChecked(True)
        self.chkPrimaryEvent.setObjectName(_fromUtf8("chkPrimaryEvent"))
        self.gridLayout_2.addWidget(self.chkPrimaryEvent, 7, 2, 1, 1)
        self.chkDiagnosis = QtGui.QCheckBox(self.groupBox)
        self.chkDiagnosis.setChecked(True)
        self.chkDiagnosis.setObjectName(_fromUtf8("chkDiagnosis"))
        self.gridLayout_2.addWidget(self.chkDiagnosis, 8, 3, 1, 1)
        self.chkOrderEvent = QtGui.QCheckBox(self.groupBox)
        self.chkOrderEvent.setChecked(True)
        self.chkOrderEvent.setObjectName(_fromUtf8("chkOrderEvent"))
        self.gridLayout_2.addWidget(self.chkOrderEvent, 6, 2, 1, 1)
        self.chkPerson = QtGui.QCheckBox(self.groupBox)
        self.chkPerson.setChecked(True)
        self.chkPerson.setObjectName(_fromUtf8("chkPerson"))
        self.gridLayout_2.addWidget(self.chkPerson, 6, 3, 1, 1)
        self.chkOrgStructure = QtGui.QCheckBox(self.groupBox)
        self.chkOrgStructure.setChecked(True)
        self.chkOrgStructure.setObjectName(_fromUtf8("chkOrgStructure"))
        self.gridLayout_2.addWidget(self.chkOrgStructure, 3, 3, 1, 1)
        self.chkReanimation = QtGui.QCheckBox(self.groupBox)
        self.chkReanimation.setChecked(True)
        self.chkReanimation.setObjectName(_fromUtf8("chkReanimation"))
        self.gridLayout_2.addWidget(self.chkReanimation, 5, 3, 1, 1)
        self.chkOrganization = QtGui.QCheckBox(self.groupBox)
        self.chkOrganization.setChecked(True)
        self.chkOrganization.setObjectName(_fromUtf8("chkOrganization"))
        self.gridLayout_2.addWidget(self.chkOrganization, 7, 3, 1, 1)
        self.chkProfile = QtGui.QCheckBox(self.groupBox)
        self.chkProfile.setChecked(True)
        self.chkProfile.setObjectName(_fromUtf8("chkProfile"))
        self.gridLayout_2.addWidget(self.chkProfile, 4, 3, 1, 1)
        self.chkResult = QtGui.QCheckBox(self.groupBox)
        self.chkResult.setChecked(True)
        self.chkResult.setObjectName(_fromUtf8("chkResult"))
        self.gridLayout_2.addWidget(self.chkResult, 2, 3, 1, 1)
        self.chkMES = QtGui.QCheckBox(self.groupBox)
        self.chkMES.setChecked(True)
        self.chkMES.setObjectName(_fromUtf8("chkMES"))
        self.gridLayout_2.addWidget(self.chkMES, 12, 0, 1, 1)
        self.chkAge = QtGui.QCheckBox(self.groupBox)
        self.chkAge.setChecked(True)
        self.chkAge.setObjectName(_fromUtf8("chkAge"))
        self.gridLayout_2.addWidget(self.chkAge, 6, 0, 1, 1)
        self.chkPolicy = QtGui.QCheckBox(self.groupBox)
        self.chkPolicy.setChecked(True)
        self.chkPolicy.setObjectName(_fromUtf8("chkPolicy"))
        self.gridLayout_2.addWidget(self.chkPolicy, 8, 0, 1, 1)
        self.chkMKB = QtGui.QCheckBox(self.groupBox)
        self.chkMKB.setChecked(True)
        self.chkMKB.setObjectName(_fromUtf8("chkMKB"))
        self.gridLayout_2.addWidget(self.chkMKB, 10, 0, 1, 1)
        self.chkFinance = QtGui.QCheckBox(self.groupBox)
        self.chkFinance.setChecked(True)
        self.chkFinance.setObjectName(_fromUtf8("chkFinance"))
        self.gridLayout_2.addWidget(self.chkFinance, 7, 0, 1, 1)
        self.chkFinishedMKB = QtGui.QCheckBox(self.groupBox)
        self.chkFinishedMKB.setChecked(True)
        self.chkFinishedMKB.setObjectName(_fromUtf8("chkFinishedMKB"))
        self.gridLayout_2.addWidget(self.chkFinishedMKB, 11, 0, 1, 1)
        self.chkCode = QtGui.QCheckBox(self.groupBox)
        self.chkCode.setChecked(True)
        self.chkCode.setObjectName(_fromUtf8("chkCode"))
        self.gridLayout_2.addWidget(self.chkCode, 0, 2, 1, 1)
        self.chkSex = QtGui.QCheckBox(self.groupBox)
        self.chkSex.setChecked(True)
        self.chkSex.setObjectName(_fromUtf8("chkSex"))
        self.gridLayout_2.addWidget(self.chkSex, 5, 0, 1, 1)
        self.chkExternalId = QtGui.QCheckBox(self.groupBox)
        self.chkExternalId.setChecked(True)
        self.chkExternalId.setObjectName(_fromUtf8("chkExternalId"))
        self.gridLayout_2.addWidget(self.chkExternalId, 0, 0, 1, 1)
        self.chkFirstName = QtGui.QCheckBox(self.groupBox)
        self.chkFirstName.setChecked(True)
        self.chkFirstName.setObjectName(_fromUtf8("chkFirstName"))
        self.gridLayout_2.addWidget(self.chkFirstName, 3, 0, 1, 1)
        self.chkPatrName = QtGui.QCheckBox(self.groupBox)
        self.chkPatrName.setChecked(True)
        self.chkPatrName.setObjectName(_fromUtf8("chkPatrName"))
        self.gridLayout_2.addWidget(self.chkPatrName, 4, 0, 1, 1)
        self.chkLastName = QtGui.QCheckBox(self.groupBox)
        self.chkLastName.setChecked(True)
        self.chkLastName.setObjectName(_fromUtf8("chkLastName"))
        self.gridLayout_2.addWidget(self.chkLastName, 2, 0, 1, 1)
        self.chkBirthDate = QtGui.QCheckBox(self.groupBox)
        self.chkBirthDate.setChecked(True)
        self.chkBirthDate.setObjectName(_fromUtf8("chkBirthDate"))
        self.gridLayout_2.addWidget(self.chkBirthDate, 13, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 13, 0, 1, 5)
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem4, 14, 4, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblMES.setBuddy(self.cmbMES)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblMKB.setBuddy(self.cmbMKBFilter)

        self.retranslateUi(ReportAnalyticalTable)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAnalyticalTable.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAnalyticalTable.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAnalyticalTable)

    def retranslateUi(self, ReportAnalyticalTable):
        ReportAnalyticalTable.setWindowTitle(_translate("ReportAnalyticalTable", "Dialog", None))
        self.lblDiagType.setText(_translate("ReportAnalyticalTable", "Тип диагноза", None))
        self.lblEndDate.setText(_translate("ReportAnalyticalTable", "Дата &окончания периода", None))
        self.cmbResult.setItemText(0, _translate("ReportAnalyticalTable", "не задано", None))
        self.cmbResult.setItemText(1, _translate("ReportAnalyticalTable", "умер", None))
        self.cmbResult.setItemText(2, _translate("ReportAnalyticalTable", "выписан", None))
        self.lblMES.setText(_translate("ReportAnalyticalTable", "Коды МЭС", None))
        self.cmbMES.setItemText(0, _translate("ReportAnalyticalTable", "Игнор.", None))
        self.cmbMES.setItemText(1, _translate("ReportAnalyticalTable", "Интервал", None))
        self.chkFinanceMulti.setText(_translate("ReportAnalyticalTable", "Тип финансирования", None))
        self.lblBegDate.setText(_translate("ReportAnalyticalTable", "Дата &начала периода", None))
        self.chkOrgStructureMulti.setText(_translate("ReportAnalyticalTable", "Подразделение", None))
        self.chkEventTypeMulti.setText(_translate("ReportAnalyticalTable", "Тип обращения", None))
        self.label.setText(_translate("ReportAnalyticalTable", "Результат события", None))
        self.lblMKB.setText(_translate("ReportAnalyticalTable", "Коды диагнозов по &МКБ", None))
        self.cmbMKBFilter.setItemText(0, _translate("ReportAnalyticalTable", "Игнор.", None))
        self.cmbMKBFilter.setItemText(1, _translate("ReportAnalyticalTable", "Интервал", None))
        self.edtMKBFrom.setInputMask(_translate("ReportAnalyticalTable", "a00.00; ", None))
        self.edtMKBFrom.setText(_translate("ReportAnalyticalTable", "A.", None))
        self.edtMKBTo.setInputMask(_translate("ReportAnalyticalTable", "a00.00; ", None))
        self.edtMKBTo.setText(_translate("ReportAnalyticalTable", "Z99.9", None))
        self.groupBox.setTitle(_translate("ReportAnalyticalTable", "Отчет строится по столбцам", None))
        self.chkSetTime.setText(_translate("ReportAnalyticalTable", "Время поступления", None))
        self.chkExecDate.setText(_translate("ReportAnalyticalTable", "Дата выбытия", None))
        self.chkReceived.setText(_translate("ReportAnalyticalTable", "Время доставки с момента получения травмы/заболевания", None))
        self.chkExecTime.setText(_translate("ReportAnalyticalTable", "Время выбытия", None))
        self.chkArea.setText(_translate("ReportAnalyticalTable", "Район", None))
        self.chkName.setText(_translate("ReportAnalyticalTable", "Наименование услуги", None))
        self.chkTime.setText(_translate("ReportAnalyticalTable", "Время оказания услуги  c момена поступления", None))
        self.chkStatus.setText(_translate("ReportAnalyticalTable", "Статус оплаты", None))
        self.chkActionPerson.setText(_translate("ReportAnalyticalTable", "Исполнитель в услуге", None))
        self.chkWork.setText(_translate("ReportAnalyticalTable", "Занятость", None))
        self.chkInhab.setText(_translate("ReportAnalyticalTable", "Житель", None))
        self.chkSetDate.setText(_translate("ReportAnalyticalTable", "Дата поступления", None))
        self.chkPrimaryEvent.setText(_translate("ReportAnalyticalTable", "Первично/повторно", None))
        self.chkDiagnosis.setText(_translate("ReportAnalyticalTable", "Диагноз направителя", None))
        self.chkOrderEvent.setText(_translate("ReportAnalyticalTable", "Порядок поступления", None))
        self.chkPerson.setText(_translate("ReportAnalyticalTable", "Лечащий врач", None))
        self.chkOrgStructure.setText(_translate("ReportAnalyticalTable", "Отделение, из которого выбыл", None))
        self.chkReanimation.setText(_translate("ReportAnalyticalTable", "Нахождение в реанимации", None))
        self.chkOrganization.setText(_translate("ReportAnalyticalTable", "Кем направлен", None))
        self.chkProfile.setText(_translate("ReportAnalyticalTable", "Профиль", None))
        self.chkResult.setText(_translate("ReportAnalyticalTable", "Исход", None))
        self.chkMES.setText(_translate("ReportAnalyticalTable", "Стандарт", None))
        self.chkAge.setText(_translate("ReportAnalyticalTable", "Возраст", None))
        self.chkPolicy.setText(_translate("ReportAnalyticalTable", "Серия и номер полиса", None))
        self.chkMKB.setText(_translate("ReportAnalyticalTable", "Диагноз", None))
        self.chkFinance.setText(_translate("ReportAnalyticalTable", "Тип финансирования", None))
        self.chkFinishedMKB.setText(_translate("ReportAnalyticalTable", "Заключительный диагноз", None))
        self.chkCode.setText(_translate("ReportAnalyticalTable", "Код услуги", None))
        self.chkSex.setText(_translate("ReportAnalyticalTable", "Пол", None))
        self.chkExternalId.setText(_translate("ReportAnalyticalTable", "№ истории болезни", None))
        self.chkFirstName.setText(_translate("ReportAnalyticalTable", "Имя", None))
        self.chkPatrName.setText(_translate("ReportAnalyticalTable", "Отчество", None))
        self.chkLastName.setText(_translate("ReportAnalyticalTable", "Фамилия", None))
        self.chkBirthDate.setText(_translate("ReportAnalyticalTable", "Дата рождения", None))

from library.RBListBox import CRBListBox
from library.crbcombobox import CRBComboBox
from library.ICDCodeEdit import CICDCodeEdit
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
