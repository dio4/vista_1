# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportReceivedAndRefusalClients.ui'
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

class Ui_ReportReceivedAndRefusalClientsSetupDialog(object):
    def setupUi(self, ReportReceivedAndRefusalClientsSetupDialog):
        ReportReceivedAndRefusalClientsSetupDialog.setObjectName(_fromUtf8("ReportReceivedAndRefusalClientsSetupDialog"))
        ReportReceivedAndRefusalClientsSetupDialog.resize(587, 594)
        self.gridLayout_2 = QtGui.QGridLayout(ReportReceivedAndRefusalClientsSetupDialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem = QtGui.QSpacerItem(20, 33, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 5, 2, 1, 1)
        self.edtBegTime = QtGui.QTimeEdit(ReportReceivedAndRefusalClientsSetupDialog)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout_2.addWidget(self.edtBegTime, 0, 3, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(ReportReceivedAndRefusalClientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout_2.addWidget(self.edtEndDate, 1, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportReceivedAndRefusalClientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEndDate.sizePolicy().hasHeightForWidth())
        self.lblEndDate.setSizePolicy(sizePolicy)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout_2.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportReceivedAndRefusalClientsSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout_2.addWidget(self.cmbOrgStructure, 2, 2, 1, 2)
        self.edtEndTime = QtGui.QTimeEdit(ReportReceivedAndRefusalClientsSetupDialog)
        self.edtEndTime.setObjectName(_fromUtf8("edtEndTime"))
        self.gridLayout_2.addWidget(self.edtEndTime, 1, 3, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportReceivedAndRefusalClientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblBegDate.sizePolicy().hasHeightForWidth())
        self.lblBegDate.setSizePolicy(sizePolicy)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout_2.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportReceivedAndRefusalClientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout_2.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.lblOrderBy = QtGui.QLabel(ReportReceivedAndRefusalClientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOrderBy.sizePolicy().hasHeightForWidth())
        self.lblOrderBy.setSizePolicy(sizePolicy)
        self.lblOrderBy.setObjectName(_fromUtf8("lblOrderBy"))
        self.gridLayout_2.addWidget(self.lblOrderBy, 3, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportReceivedAndRefusalClientsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOrgStructure.sizePolicy().hasHeightForWidth())
        self.lblOrgStructure.setSizePolicy(sizePolicy)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout_2.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportReceivedAndRefusalClientsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 6, 2, 1, 1)
        self.cmbOrderBy = QtGui.QComboBox(ReportReceivedAndRefusalClientsSetupDialog)
        self.cmbOrderBy.setObjectName(_fromUtf8("cmbOrderBy"))
        self.cmbOrderBy.addItem(_fromUtf8(""))
        self.cmbOrderBy.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.cmbOrderBy, 3, 2, 1, 2)
        self.grpOutputToReport = QtGui.QGroupBox(ReportReceivedAndRefusalClientsSetupDialog)
        self.grpOutputToReport.setFlat(False)
        self.grpOutputToReport.setObjectName(_fromUtf8("grpOutputToReport"))
        self.gridLayout = QtGui.QGridLayout(self.grpOutputToReport)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkReceivedOrgDiagnosis = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkReceivedOrgDiagnosis.setChecked(True)
        self.chkReceivedOrgDiagnosis.setObjectName(_fromUtf8("chkReceivedOrgDiagnosis"))
        self.gridLayout.addWidget(self.chkReceivedOrgDiagnosis, 3, 1, 1, 1)
        self.chkSex = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkSex.setChecked(True)
        self.chkSex.setObjectName(_fromUtf8("chkSex"))
        self.gridLayout.addWidget(self.chkSex, 7, 0, 1, 1)
        self.chkEventOrder = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkEventOrder.setChecked(True)
        self.chkEventOrder.setObjectName(_fromUtf8("chkEventOrder"))
        self.gridLayout.addWidget(self.chkEventOrder, 11, 1, 1, 1)
        self.chkBedProfile = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkBedProfile.setChecked(True)
        self.chkBedProfile.setObjectName(_fromUtf8("chkBedProfile"))
        self.gridLayout.addWidget(self.chkBedProfile, 12, 0, 1, 1)
        self.chkAge = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkAge.setChecked(True)
        self.chkAge.setObjectName(_fromUtf8("chkAge"))
        self.gridLayout.addWidget(self.chkAge, 12, 1, 1, 1)
        self.chkRelegateOrgDiagnosis = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkRelegateOrgDiagnosis.setChecked(True)
        self.chkRelegateOrgDiagnosis.setObjectName(_fromUtf8("chkRelegateOrgDiagnosis"))
        self.gridLayout.addWidget(self.chkRelegateOrgDiagnosis, 7, 1, 1, 1)
        self.chkOtherRelegateOrg = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkOtherRelegateOrg.setChecked(True)
        self.chkOtherRelegateOrg.setObjectName(_fromUtf8("chkOtherRelegateOrg"))
        self.gridLayout.addWidget(self.chkOtherRelegateOrg, 2, 1, 1, 1)
        self.chkLeavedInfo = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkLeavedInfo.setChecked(True)
        self.chkLeavedInfo.setObjectName(_fromUtf8("chkLeavedInfo"))
        self.gridLayout.addWidget(self.chkLeavedInfo, 4, 1, 1, 1)
        self.chkMessageToRelatives = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkMessageToRelatives.setChecked(True)
        self.chkMessageToRelatives.setObjectName(_fromUtf8("chkMessageToRelatives"))
        self.gridLayout.addWidget(self.chkMessageToRelatives, 5, 1, 1, 1)
        self.chkHour = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkHour.setChecked(True)
        self.chkHour.setObjectName(_fromUtf8("chkHour"))
        self.gridLayout.addWidget(self.chkHour, 11, 0, 1, 1)
        self.chkRelegateOrg = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkRelegateOrg.setChecked(True)
        self.chkRelegateOrg.setObjectName(_fromUtf8("chkRelegateOrg"))
        self.gridLayout.addWidget(self.chkRelegateOrg, 0, 1, 1, 1)
        self.chkCompulsoryPolicy = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkCompulsoryPolicy.setChecked(True)
        self.chkCompulsoryPolicy.setObjectName(_fromUtf8("chkCompulsoryPolicy"))
        self.gridLayout.addWidget(self.chkCompulsoryPolicy, 5, 0, 1, 1)
        self.chkRegAddress = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkRegAddress.setChecked(True)
        self.chkRegAddress.setObjectName(_fromUtf8("chkRegAddress"))
        self.gridLayout.addWidget(self.chkRegAddress, 0, 0, 1, 1)
        self.chkNotes = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkNotes.setChecked(True)
        self.chkNotes.setObjectName(_fromUtf8("chkNotes"))
        self.gridLayout.addWidget(self.chkNotes, 6, 1, 1, 1)
        self.chkDeliveredOrg = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkDeliveredOrg.setChecked(True)
        self.chkDeliveredOrg.setObjectName(_fromUtf8("chkDeliveredOrg"))
        self.gridLayout.addWidget(self.chkDeliveredOrg, 1, 1, 1, 1)
        self.chkDocument = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkDocument.setChecked(True)
        self.chkDocument.setObjectName(_fromUtf8("chkDocument"))
        self.gridLayout.addWidget(self.chkDocument, 4, 0, 1, 1)
        self.chkRelations = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkRelations.setChecked(True)
        self.chkRelations.setObjectName(_fromUtf8("chkRelations"))
        self.gridLayout.addWidget(self.chkRelations, 3, 0, 1, 1)
        self.chkContacts = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkContacts.setChecked(True)
        self.chkContacts.setObjectName(_fromUtf8("chkContacts"))
        self.gridLayout.addWidget(self.chkContacts, 2, 0, 1, 1)
        self.chkNotHospitalized = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkNotHospitalized.setChecked(True)
        self.chkNotHospitalized.setObjectName(_fromUtf8("chkNotHospitalized"))
        self.gridLayout.addWidget(self.chkNotHospitalized, 10, 0, 1, 1)
        self.chkVoluntaryPolicy = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkVoluntaryPolicy.setChecked(True)
        self.chkVoluntaryPolicy.setObjectName(_fromUtf8("chkVoluntaryPolicy"))
        self.gridLayout.addWidget(self.chkVoluntaryPolicy, 6, 0, 1, 1)
        self.chkLocAddress = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkLocAddress.setChecked(True)
        self.chkLocAddress.setObjectName(_fromUtf8("chkLocAddress"))
        self.gridLayout.addWidget(self.chkLocAddress, 1, 0, 1, 1)
        self.chkCardNumber = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkCardNumber.setChecked(True)
        self.chkCardNumber.setObjectName(_fromUtf8("chkCardNumber"))
        self.gridLayout.addWidget(self.chkCardNumber, 10, 1, 1, 1)
        self.chkHospitalBedProfile = QtGui.QCheckBox(self.grpOutputToReport)
        self.chkHospitalBedProfile.setChecked(False)
        self.chkHospitalBedProfile.setObjectName(_fromUtf8("chkHospitalBedProfile"))
        self.gridLayout.addWidget(self.chkHospitalBedProfile, 13, 0, 1, 1)
        self.gridLayout_2.addWidget(self.grpOutputToReport, 4, 0, 2, 4)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblOrderBy.setBuddy(self.cmbOrgStructure)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(ReportReceivedAndRefusalClientsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportReceivedAndRefusalClientsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportReceivedAndRefusalClientsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportReceivedAndRefusalClientsSetupDialog)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.edtBegDate, self.edtBegTime)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.edtBegTime, self.edtEndDate)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.edtEndDate, self.edtEndTime)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.edtEndTime, self.cmbOrgStructure)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.cmbOrgStructure, self.chkRegAddress)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkRegAddress, self.chkLocAddress)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkLocAddress, self.chkContacts)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkContacts, self.chkRelations)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkRelations, self.chkDocument)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkDocument, self.chkCompulsoryPolicy)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkCompulsoryPolicy, self.chkVoluntaryPolicy)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkVoluntaryPolicy, self.chkRelegateOrg)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkRelegateOrg, self.chkDeliveredOrg)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkDeliveredOrg, self.chkReceivedOrgDiagnosis)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkReceivedOrgDiagnosis, self.chkLeavedInfo)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkLeavedInfo, self.chkMessageToRelatives)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkMessageToRelatives, self.chkNotes)
        ReportReceivedAndRefusalClientsSetupDialog.setTabOrder(self.chkNotes, self.buttonBox)

    def retranslateUi(self, ReportReceivedAndRefusalClientsSetupDialog):
        ReportReceivedAndRefusalClientsSetupDialog.setWindowTitle(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Dialog", None))
        self.edtBegTime.setDisplayFormat(_translate("ReportReceivedAndRefusalClientsSetupDialog", "HH:mm", None))
        self.lblEndDate.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Дата &окончания периода", None))
        self.edtEndTime.setDisplayFormat(_translate("ReportReceivedAndRefusalClientsSetupDialog", "HH:mm", None))
        self.lblBegDate.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Дата &начала периода", None))
        self.lblOrderBy.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "&Сортировать по", None))
        self.lblOrgStructure.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "&Подразделение", None))
        self.cmbOrderBy.setItemText(0, _translate("ReportReceivedAndRefusalClientsSetupDialog", "ФИО пациента", None))
        self.cmbOrderBy.setItemText(1, _translate("ReportReceivedAndRefusalClientsSetupDialog", "времени поступления в стационар", None))
        self.grpOutputToReport.setTitle(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Выводить в отчёт", None))
        self.chkReceivedOrgDiagnosis.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Диагноз приемного отделения", None))
        self.chkSex.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Пол", None))
        self.chkEventOrder.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Порядок наступления", None))
        self.chkBedProfile.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Профиль", None))
        self.chkAge.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Возраст", None))
        self.chkRelegateOrgDiagnosis.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Диагноз направителя", None))
        self.chkOtherRelegateOrg.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Прочие направители", None))
        self.chkLeavedInfo.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Данные о выписке (переводе, смерти)", None))
        self.chkMessageToRelatives.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Сообщено родственникам", None))
        self.chkHour.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Час", None))
        self.chkRelegateOrg.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Кем направлен", None))
        self.chkCompulsoryPolicy.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Полисные данные ОМС", None))
        self.chkRegAddress.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Адрес регистрации", None))
        self.chkNotes.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Примечание", None))
        self.chkDeliveredOrg.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Кем доставлен", None))
        self.chkDocument.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Документ УЛ", None))
        self.chkRelations.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Родственные связи", None))
        self.chkContacts.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Контактные данные", None))
        self.chkNotHospitalized.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Если не был госпитализирован\n"
"(причина и принятые меры)", None))
        self.chkVoluntaryPolicy.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Полисные данные ДМС", None))
        self.chkLocAddress.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Адрес проживания", None))
        self.chkCardNumber.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "№ карты стационарного больного\n"
"(истории родов)", None))
        self.chkHospitalBedProfile.setText(_translate("ReportReceivedAndRefusalClientsSetupDialog", "Профиль койки", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
