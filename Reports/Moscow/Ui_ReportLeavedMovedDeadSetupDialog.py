# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportLeavedMovedDeadSetupDialog.ui'
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

class Ui_ReportLeavedMovedDeadSetupDialog(object):
    def setupUi(self, ReportLeavedMovedDeadSetupDialog):
        ReportLeavedMovedDeadSetupDialog.setObjectName(_fromUtf8("ReportLeavedMovedDeadSetupDialog"))
        ReportLeavedMovedDeadSetupDialog.resize(640, 450)
        self.gridLayout_4 = QtGui.QGridLayout(ReportLeavedMovedDeadSetupDialog)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.rbByLeavedDate = QtGui.QRadioButton(ReportLeavedMovedDeadSetupDialog)
        self.rbByLeavedDate.setChecked(True)
        self.rbByLeavedDate.setObjectName(_fromUtf8("rbByLeavedDate"))
        self.gridLayout_4.addWidget(self.rbByLeavedDate, 0, 0, 1, 1)
        self.stkFilterDate = QtGui.QStackedWidget(ReportLeavedMovedDeadSetupDialog)
        self.stkFilterDate.setFrameShape(QtGui.QFrame.StyledPanel)
        self.stkFilterDate.setObjectName(_fromUtf8("stkFilterDate"))
        self.pgLeavedDate = QtGui.QWidget()
        self.pgLeavedDate.setObjectName(_fromUtf8("pgLeavedDate"))
        self.gridLayout_3 = QtGui.QGridLayout(self.pgLeavedDate)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.edtLeavedDate = CDateEdit(self.pgLeavedDate)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtLeavedDate.sizePolicy().hasHeightForWidth())
        self.edtLeavedDate.setSizePolicy(sizePolicy)
        self.edtLeavedDate.setCalendarPopup(True)
        self.edtLeavedDate.setObjectName(_fromUtf8("edtLeavedDate"))
        self.gridLayout_3.addWidget(self.edtLeavedDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(158, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 0, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem1, 1, 1, 1, 1)
        self.label = QtGui.QLabel(self.pgLeavedDate)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.stkFilterDate.addWidget(self.pgLeavedDate)
        self.pgPeriod = QtGui.QWidget()
        self.pgPeriod.setObjectName(_fromUtf8("pgPeriod"))
        self.gridLayout_2 = QtGui.QGridLayout(self.pgPeriod)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblLeavedEndDate = QtGui.QLabel(self.pgPeriod)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblLeavedEndDate.sizePolicy().hasHeightForWidth())
        self.lblLeavedEndDate.setSizePolicy(sizePolicy)
        self.lblLeavedEndDate.setObjectName(_fromUtf8("lblLeavedEndDate"))
        self.gridLayout_2.addWidget(self.lblLeavedEndDate, 1, 3, 1, 1)
        self.chkByReceivedDate = QtGui.QCheckBox(self.pgPeriod)
        self.chkByReceivedDate.setObjectName(_fromUtf8("chkByReceivedDate"))
        self.gridLayout_2.addWidget(self.chkByReceivedDate, 0, 0, 1, 1)
        self.chkByLeavedDate = QtGui.QCheckBox(self.pgPeriod)
        self.chkByLeavedDate.setChecked(True)
        self.chkByLeavedDate.setObjectName(_fromUtf8("chkByLeavedDate"))
        self.gridLayout_2.addWidget(self.chkByLeavedDate, 1, 0, 1, 1)
        self.edtLeavedBegDate = CDateEdit(self.pgPeriod)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtLeavedBegDate.sizePolicy().hasHeightForWidth())
        self.edtLeavedBegDate.setSizePolicy(sizePolicy)
        self.edtLeavedBegDate.setCalendarPopup(True)
        self.edtLeavedBegDate.setObjectName(_fromUtf8("edtLeavedBegDate"))
        self.gridLayout_2.addWidget(self.edtLeavedBegDate, 1, 2, 1, 1)
        self.edtReceivedBegDate = CDateEdit(self.pgPeriod)
        self.edtReceivedBegDate.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtReceivedBegDate.sizePolicy().hasHeightForWidth())
        self.edtReceivedBegDate.setSizePolicy(sizePolicy)
        self.edtReceivedBegDate.setCalendarPopup(True)
        self.edtReceivedBegDate.setObjectName(_fromUtf8("edtReceivedBegDate"))
        self.gridLayout_2.addWidget(self.edtReceivedBegDate, 0, 2, 1, 1)
        self.edtReceivedEndDate = CDateEdit(self.pgPeriod)
        self.edtReceivedEndDate.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtReceivedEndDate.sizePolicy().hasHeightForWidth())
        self.edtReceivedEndDate.setSizePolicy(sizePolicy)
        self.edtReceivedEndDate.setCalendarPopup(True)
        self.edtReceivedEndDate.setObjectName(_fromUtf8("edtReceivedEndDate"))
        self.gridLayout_2.addWidget(self.edtReceivedEndDate, 0, 4, 1, 1)
        self.lblReceivedEndDate = QtGui.QLabel(self.pgPeriod)
        self.lblReceivedEndDate.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblReceivedEndDate.sizePolicy().hasHeightForWidth())
        self.lblReceivedEndDate.setSizePolicy(sizePolicy)
        self.lblReceivedEndDate.setObjectName(_fromUtf8("lblReceivedEndDate"))
        self.gridLayout_2.addWidget(self.lblReceivedEndDate, 0, 3, 1, 1)
        self.edtLeavedEndDate = CDateEdit(self.pgPeriod)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtLeavedEndDate.sizePolicy().hasHeightForWidth())
        self.edtLeavedEndDate.setSizePolicy(sizePolicy)
        self.edtLeavedEndDate.setCalendarPopup(True)
        self.edtLeavedEndDate.setObjectName(_fromUtf8("edtLeavedEndDate"))
        self.gridLayout_2.addWidget(self.edtLeavedEndDate, 1, 4, 1, 1)
        self.lblReceivedBegDate = QtGui.QLabel(self.pgPeriod)
        self.lblReceivedBegDate.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblReceivedBegDate.sizePolicy().hasHeightForWidth())
        self.lblReceivedBegDate.setSizePolicy(sizePolicy)
        self.lblReceivedBegDate.setObjectName(_fromUtf8("lblReceivedBegDate"))
        self.gridLayout_2.addWidget(self.lblReceivedBegDate, 0, 1, 1, 1)
        self.lblLeavedBegDate = QtGui.QLabel(self.pgPeriod)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblLeavedBegDate.sizePolicy().hasHeightForWidth())
        self.lblLeavedBegDate.setSizePolicy(sizePolicy)
        self.lblLeavedBegDate.setObjectName(_fromUtf8("lblLeavedBegDate"))
        self.gridLayout_2.addWidget(self.lblLeavedBegDate, 1, 1, 1, 1)
        self.stkFilterDate.addWidget(self.pgPeriod)
        self.gridLayout_4.addWidget(self.stkFilterDate, 0, 1, 2, 2)
        self.rbByPeriod = QtGui.QRadioButton(ReportLeavedMovedDeadSetupDialog)
        self.rbByPeriod.setObjectName(_fromUtf8("rbByPeriod"))
        self.gridLayout_4.addWidget(self.rbByPeriod, 1, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportLeavedMovedDeadSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOrgStructure.sizePolicy().hasHeightForWidth())
        self.lblOrgStructure.setSizePolicy(sizePolicy)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout_4.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(ReportLeavedMovedDeadSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkDeliveredTime = QtGui.QCheckBox(self.groupBox)
        self.chkDeliveredTime.setObjectName(_fromUtf8("chkDeliveredTime"))
        self.gridLayout.addWidget(self.chkDeliveredTime, 1, 1, 1, 1)
        self.chkDiagnosis = QtGui.QCheckBox(self.groupBox)
        self.chkDiagnosis.setObjectName(_fromUtf8("chkDiagnosis"))
        self.gridLayout.addWidget(self.chkDiagnosis, 2, 2, 1, 1)
        self.chkOperations = QtGui.QCheckBox(self.groupBox)
        self.chkOperations.setObjectName(_fromUtf8("chkOperations"))
        self.gridLayout.addWidget(self.chkOperations, 7, 2, 1, 1)
        self.chkTrauma = QtGui.QCheckBox(self.groupBox)
        self.chkTrauma.setObjectName(_fromUtf8("chkTrauma"))
        self.gridLayout.addWidget(self.chkTrauma, 4, 2, 1, 1)
        self.chkStatus = QtGui.QCheckBox(self.groupBox)
        self.chkStatus.setObjectName(_fromUtf8("chkStatus"))
        self.gridLayout.addWidget(self.chkStatus, 1, 2, 1, 1)
        self.chkResult = QtGui.QCheckBox(self.groupBox)
        self.chkResult.setObjectName(_fromUtf8("chkResult"))
        self.gridLayout.addWidget(self.chkResult, 0, 2, 1, 1)
        self.chkExternalId = QtGui.QCheckBox(self.groupBox)
        self.chkExternalId.setChecked(True)
        self.chkExternalId.setObjectName(_fromUtf8("chkExternalId"))
        self.gridLayout.addWidget(self.chkExternalId, 0, 0, 1, 1)
        self.chkDeliveredBy = QtGui.QCheckBox(self.groupBox)
        self.chkDeliveredBy.setObjectName(_fromUtf8("chkDeliveredBy"))
        self.gridLayout.addWidget(self.chkDeliveredBy, 0, 1, 1, 1)
        self.chkBedDays = QtGui.QCheckBox(self.groupBox)
        self.chkBedDays.setObjectName(_fromUtf8("chkBedDays"))
        self.gridLayout.addWidget(self.chkBedDays, 6, 2, 1, 1)
        self.chkAutopsyDiagnosis = QtGui.QCheckBox(self.groupBox)
        self.chkAutopsyDiagnosis.setObjectName(_fromUtf8("chkAutopsyDiagnosis"))
        self.gridLayout.addWidget(self.chkAutopsyDiagnosis, 3, 2, 1, 1)
        self.chkName = QtGui.QCheckBox(self.groupBox)
        self.chkName.setChecked(True)
        self.chkName.setObjectName(_fromUtf8("chkName"))
        self.gridLayout.addWidget(self.chkName, 1, 0, 1, 1)
        self.chkEventOrder = QtGui.QCheckBox(self.groupBox)
        self.chkEventOrder.setObjectName(_fromUtf8("chkEventOrder"))
        self.gridLayout.addWidget(self.chkEventOrder, 2, 1, 1, 1)
        self.chkLeavedDate = QtGui.QCheckBox(self.groupBox)
        self.chkLeavedDate.setChecked(True)
        self.chkLeavedDate.setObjectName(_fromUtf8("chkLeavedDate"))
        self.gridLayout.addWidget(self.chkLeavedDate, 5, 2, 1, 1)
        self.chkBirthDate = QtGui.QCheckBox(self.groupBox)
        self.chkBirthDate.setObjectName(_fromUtf8("chkBirthDate"))
        self.gridLayout.addWidget(self.chkBirthDate, 2, 0, 1, 1)
        self.chkSex = QtGui.QCheckBox(self.groupBox)
        self.chkSex.setObjectName(_fromUtf8("chkSex"))
        self.gridLayout.addWidget(self.chkSex, 3, 0, 1, 1)
        self.chkSocStatus = QtGui.QCheckBox(self.groupBox)
        self.chkSocStatus.setObjectName(_fromUtf8("chkSocStatus"))
        self.gridLayout.addWidget(self.chkSocStatus, 4, 0, 1, 1)
        self.chkBenefits = QtGui.QCheckBox(self.groupBox)
        self.chkBenefits.setObjectName(_fromUtf8("chkBenefits"))
        self.gridLayout.addWidget(self.chkBenefits, 5, 0, 1, 1)
        self.chkRegAddress = QtGui.QCheckBox(self.groupBox)
        self.chkRegAddress.setObjectName(_fromUtf8("chkRegAddress"))
        self.gridLayout.addWidget(self.chkRegAddress, 6, 0, 1, 1)
        self.chkBegDate = QtGui.QCheckBox(self.groupBox)
        self.chkBegDate.setChecked(True)
        self.chkBegDate.setObjectName(_fromUtf8("chkBegDate"))
        self.gridLayout.addWidget(self.chkBegDate, 3, 1, 1, 1)
        self.chkPrimary = QtGui.QCheckBox(self.groupBox)
        self.chkPrimary.setObjectName(_fromUtf8("chkPrimary"))
        self.gridLayout.addWidget(self.chkPrimary, 4, 1, 1, 1)
        self.chkOrgStructure = QtGui.QCheckBox(self.groupBox)
        self.chkOrgStructure.setChecked(True)
        self.chkOrgStructure.setObjectName(_fromUtf8("chkOrgStructure"))
        self.gridLayout.addWidget(self.chkOrgStructure, 5, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 3, 0, 1, 3)
        spacerItem2 = QtGui.QSpacerItem(20, 38, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem2, 4, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportLeavedMovedDeadSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_4.addWidget(self.buttonBox, 5, 2, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportLeavedMovedDeadSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout_4.addWidget(self.cmbOrgStructure, 2, 1, 1, 2)
        self.label.setBuddy(self.edtLeavedDate)
        self.lblLeavedEndDate.setBuddy(self.edtLeavedEndDate)
        self.lblReceivedEndDate.setBuddy(self.edtReceivedEndDate)
        self.lblReceivedBegDate.setBuddy(self.edtReceivedBegDate)
        self.lblLeavedBegDate.setBuddy(self.edtLeavedBegDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(ReportLeavedMovedDeadSetupDialog)
        self.stkFilterDate.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportLeavedMovedDeadSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportLeavedMovedDeadSetupDialog.reject)
        QtCore.QObject.connect(self.chkByLeavedDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblLeavedBegDate.setEnabled)
        QtCore.QObject.connect(self.chkByLeavedDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtLeavedBegDate.setEnabled)
        QtCore.QObject.connect(self.chkByLeavedDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblLeavedEndDate.setEnabled)
        QtCore.QObject.connect(self.chkByLeavedDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtLeavedEndDate.setEnabled)
        QtCore.QObject.connect(self.chkByReceivedDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblReceivedBegDate.setEnabled)
        QtCore.QObject.connect(self.chkByReceivedDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtReceivedBegDate.setEnabled)
        QtCore.QObject.connect(self.chkByReceivedDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblReceivedEndDate.setEnabled)
        QtCore.QObject.connect(self.chkByReceivedDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtReceivedEndDate.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ReportLeavedMovedDeadSetupDialog)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.rbByLeavedDate, self.edtLeavedDate)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.edtLeavedDate, self.rbByPeriod)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.rbByPeriod, self.cmbOrgStructure)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.cmbOrgStructure, self.chkExternalId)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkExternalId, self.chkName)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkName, self.chkBirthDate)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkBirthDate, self.chkDeliveredBy)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkDeliveredBy, self.chkDeliveredTime)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkDeliveredTime, self.chkEventOrder)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkEventOrder, self.chkResult)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkResult, self.chkStatus)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkStatus, self.chkDiagnosis)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkDiagnosis, self.chkTrauma)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkTrauma, self.chkLeavedDate)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkLeavedDate, self.chkBedDays)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkBedDays, self.chkOperations)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkOperations, self.buttonBox)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.buttonBox, self.edtReceivedEndDate)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.edtReceivedEndDate, self.chkByReceivedDate)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkByReceivedDate, self.edtLeavedEndDate)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.edtLeavedEndDate, self.edtLeavedBegDate)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.edtLeavedBegDate, self.chkByLeavedDate)
        ReportLeavedMovedDeadSetupDialog.setTabOrder(self.chkByLeavedDate, self.edtReceivedBegDate)

    def retranslateUi(self, ReportLeavedMovedDeadSetupDialog):
        ReportLeavedMovedDeadSetupDialog.setWindowTitle(_translate("ReportLeavedMovedDeadSetupDialog", "Параметры отчёта", None))
        self.rbByLeavedDate.setText(_translate("ReportLeavedMovedDeadSetupDialog", "По дате &выписки", None))
        self.label.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Дата &выписки:", None))
        self.lblLeavedEndDate.setText(_translate("ReportLeavedMovedDeadSetupDialog", "по", None))
        self.chkByReceivedDate.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Дата &поступления:", None))
        self.chkByLeavedDate.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Дата &выписки:", None))
        self.lblReceivedEndDate.setText(_translate("ReportLeavedMovedDeadSetupDialog", "по", None))
        self.lblReceivedBegDate.setText(_translate("ReportLeavedMovedDeadSetupDialog", "с", None))
        self.lblLeavedBegDate.setText(_translate("ReportLeavedMovedDeadSetupDialog", "с", None))
        self.rbByPeriod.setText(_translate("ReportLeavedMovedDeadSetupDialog", "За &период", None))
        self.lblOrgStructure.setText(_translate("ReportLeavedMovedDeadSetupDialog", "&Отделение", None))
        self.groupBox.setTitle(_translate("ReportLeavedMovedDeadSetupDialog", "Выводить в отчёт", None))
        self.chkDeliveredTime.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Срок", None))
        self.chkDiagnosis.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Диагноз клинический", None))
        self.chkOperations.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Операции", None))
        self.chkTrauma.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Травма, обстоятельства", None))
        self.chkStatus.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Состояние", None))
        self.chkResult.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Исход", None))
        self.chkExternalId.setText(_translate("ReportLeavedMovedDeadSetupDialog", "№ ИБ", None))
        self.chkDeliveredBy.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Направлен", None))
        self.chkBedDays.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Койко-дней", None))
        self.chkAutopsyDiagnosis.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Диагноз патологоанатомический", None))
        self.chkName.setText(_translate("ReportLeavedMovedDeadSetupDialog", "ФИО", None))
        self.chkEventOrder.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Вид поступления", None))
        self.chkLeavedDate.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Дата выписки", None))
        self.chkBirthDate.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Дата рождения", None))
        self.chkSex.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Пол", None))
        self.chkSocStatus.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Социальный статус", None))
        self.chkBenefits.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Категория", None))
        self.chkRegAddress.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Постоянная регистрация", None))
        self.chkBegDate.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Дата, время постпуления", None))
        self.chkPrimary.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Повторно", None))
        self.chkOrgStructure.setText(_translate("ReportLeavedMovedDeadSetupDialog", "Отделение поступления", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
