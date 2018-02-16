# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportEISOMSPage1.ui'
#
# Created: Mon Jun 16 20:34:40 2014
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

class Ui_ExportEISOMSPage1(object):
    def setupUi(self, ExportEISOMSPage1):
        ExportEISOMSPage1.setObjectName(_fromUtf8("ExportEISOMSPage1"))
        ExportEISOMSPage1.resize(586, 324)
        self.gridLayout = QtGui.QGridLayout(ExportEISOMSPage1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkExportClients = QtGui.QCheckBox(ExportEISOMSPage1)
        self.chkExportClients.setObjectName(_fromUtf8("chkExportClients"))
        self.gridLayout.addWidget(self.chkExportClients, 9, 0, 1, 5)
        self.chkIncludeActions = QtGui.QCheckBox(ExportEISOMSPage1)
        self.chkIncludeActions.setChecked(True)
        self.chkIncludeActions.setObjectName(_fromUtf8("chkIncludeActions"))
        self.gridLayout.addWidget(self.chkIncludeActions, 8, 0, 1, 5)
        self.chkIncludeVisits = QtGui.QCheckBox(ExportEISOMSPage1)
        self.chkIncludeVisits.setChecked(True)
        self.chkIncludeVisits.setObjectName(_fromUtf8("chkIncludeVisits"))
        self.gridLayout.addWidget(self.chkIncludeVisits, 7, 0, 1, 5)
        self.chkIgnoreConfirmation = QtGui.QCheckBox(ExportEISOMSPage1)
        self.chkIgnoreConfirmation.setObjectName(_fromUtf8("chkIgnoreConfirmation"))
        self.gridLayout.addWidget(self.chkIgnoreConfirmation, 3, 0, 1, 5)
        self.btnExport = QtGui.QPushButton(ExportEISOMSPage1)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.gridLayout.addWidget(self.btnExport, 14, 3, 1, 1)
        self.chkSendToMIAC = QtGui.QCheckBox(ExportEISOMSPage1)
        self.chkSendToMIAC.setObjectName(_fromUtf8("chkSendToMIAC"))
        self.gridLayout.addWidget(self.chkSendToMIAC, 2, 0, 1, 5)
        self.lblEisLpuId = QtGui.QLabel(ExportEISOMSPage1)
        self.lblEisLpuId.setObjectName(_fromUtf8("lblEisLpuId"))
        self.gridLayout.addWidget(self.lblEisLpuId, 12, 0, 1, 2)
        self.progressBar = CProgressBar(ExportEISOMSPage1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 0, 0, 1, 5)
        self.edtEisLpuId = QtGui.QLineEdit(ExportEISOMSPage1)
        self.edtEisLpuId.setObjectName(_fromUtf8("edtEisLpuId"))
        self.gridLayout.addWidget(self.edtEisLpuId, 12, 2, 1, 1)
        self.chkIncludeEvents = QtGui.QCheckBox(ExportEISOMSPage1)
        self.chkIncludeEvents.setChecked(True)
        self.chkIncludeEvents.setObjectName(_fromUtf8("chkIncludeEvents"))
        self.gridLayout.addWidget(self.chkIncludeEvents, 6, 0, 1, 5)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 5)
        self.btnCancel = QtGui.QPushButton(ExportEISOMSPage1)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridLayout.addWidget(self.btnCancel, 14, 4, 1, 1)
        self.label = QtGui.QLabel(ExportEISOMSPage1)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 13, 0, 1, 1)
        self.cmbPersonFormat = QtGui.QComboBox(ExportEISOMSPage1)
        self.cmbPersonFormat.setObjectName(_fromUtf8("cmbPersonFormat"))
        self.cmbPersonFormat.addItem(_fromUtf8(""))
        self.cmbPersonFormat.addItem(_fromUtf8(""))
        self.cmbPersonFormat.addItem(_fromUtf8(""))
        self.cmbPersonFormat.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbPersonFormat, 13, 1, 1, 4)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 14, 0, 1, 1)
        self.chkDD = QtGui.QCheckBox(ExportEISOMSPage1)
        self.chkDD.setObjectName(_fromUtf8("chkDD"))
        self.gridLayout.addWidget(self.chkDD, 10, 0, 1, 2)
        self.chkEnableEmptySMPIllhistory = QtGui.QCheckBox(ExportEISOMSPage1)
        self.chkEnableEmptySMPIllhistory.setObjectName(_fromUtf8("chkEnableEmptySMPIllhistory"))
        self.gridLayout.addWidget(self.chkEnableEmptySMPIllhistory, 5, 0, 1, 5)
        self.lblEisLpuId.setBuddy(self.edtEisLpuId)

        self.retranslateUi(ExportEISOMSPage1)
        QtCore.QMetaObject.connectSlotsByName(ExportEISOMSPage1)
        ExportEISOMSPage1.setTabOrder(self.chkSendToMIAC, self.chkIgnoreConfirmation)
        ExportEISOMSPage1.setTabOrder(self.chkIgnoreConfirmation, self.chkIncludeEvents)
        ExportEISOMSPage1.setTabOrder(self.chkIncludeEvents, self.chkIncludeVisits)
        ExportEISOMSPage1.setTabOrder(self.chkIncludeVisits, self.chkIncludeActions)
        ExportEISOMSPage1.setTabOrder(self.chkIncludeActions, self.chkExportClients)
        ExportEISOMSPage1.setTabOrder(self.chkExportClients, self.chkDD)
        ExportEISOMSPage1.setTabOrder(self.chkDD, self.edtEisLpuId)
        ExportEISOMSPage1.setTabOrder(self.edtEisLpuId, self.cmbPersonFormat)
        ExportEISOMSPage1.setTabOrder(self.cmbPersonFormat, self.btnExport)
        ExportEISOMSPage1.setTabOrder(self.btnExport, self.btnCancel)

    def retranslateUi(self, ExportEISOMSPage1):
        ExportEISOMSPage1.setWindowTitle(_translate("ExportEISOMSPage1", "Form", None))
        self.chkExportClients.setText(_translate("ExportEISOMSPage1", "Экспортировать пациентов", None))
        self.chkIncludeActions.setText(_translate("ExportEISOMSPage1", "Включить информацию по действиям", None))
        self.chkIncludeVisits.setText(_translate("ExportEISOMSPage1", "Включить информацию по визитам", None))
        self.chkIgnoreConfirmation.setText(_translate("ExportEISOMSPage1", "Игнорировать подтверждение оплаты или отказа", None))
        self.btnExport.setText(_translate("ExportEISOMSPage1", "экспорт", None))
        self.chkSendToMIAC.setText(_translate("ExportEISOMSPage1", "Передать данные в МИАЦ", None))
        self.lblEisLpuId.setText(_translate("ExportEISOMSPage1", "Идентификатор ЛПУ в ЕИС ОМС", None))
        self.chkIncludeEvents.setText(_translate("ExportEISOMSPage1", "Включить информацию по событиям", None))
        self.btnCancel.setText(_translate("ExportEISOMSPage1", "прервать", None))
        self.label.setText(_translate("ExportEISOMSPage1", "Экспортировать", None))
        self.cmbPersonFormat.setItemText(0, _translate("ExportEISOMSPage1", "ID врача", None))
        self.cmbPersonFormat.setItemText(1, _translate("ExportEISOMSPage1", "Код врача", None))
        self.cmbPersonFormat.setItemText(2, _translate("ExportEISOMSPage1", "Региональный код врача", None))
        self.cmbPersonFormat.setItemText(3, _translate("ExportEISOMSPage1", "Федеральный код врача", None))
        self.chkDD.setText(_translate("ExportEISOMSPage1", "Диспансеризация", None))
        self.chkEnableEmptySMPIllhistory.setToolTip(_translate("ExportEISOMSPage1", "Если номер истории болезни не задан, а ввод пустого номера запрещен, в поле ILLHISTORY попадает внешний идентификатор обращения при наличии, либо идентификатор пациента в системе.", None))
        self.chkEnableEmptySMPIllhistory.setText(_translate("ExportEISOMSPage1", "Разрешить пустой номер истории болезни для обращений СМП", None))

from library.ProgressBar import CProgressBar
