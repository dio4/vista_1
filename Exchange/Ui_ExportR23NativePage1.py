# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportR23NativePage1.ui'
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

class Ui_ExportR23NativePage1(object):
    def setupUi(self, ExportR23NativePage1):
        ExportR23NativePage1.setObjectName(_fromUtf8("ExportR23NativePage1"))
        ExportR23NativePage1.resize(727, 456)
        self.gridlayout = QtGui.QGridLayout(ExportR23NativePage1)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.cmbPayMethod = QtGui.QComboBox(ExportR23NativePage1)
        self.cmbPayMethod.setObjectName(_fromUtf8("cmbPayMethod"))
        self.cmbPayMethod.addItem(_fromUtf8(""))
        self.cmbPayMethod.addItem(_fromUtf8(""))
        self.cmbPayMethod.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbPayMethod, 4, 1, 1, 2)
        self.edtRegistryNumber = QtGui.QSpinBox(ExportR23NativePage1)
        self.edtRegistryNumber.setMaximum(99999)
        self.edtRegistryNumber.setObjectName(_fromUtf8("edtRegistryNumber"))
        self.gridlayout.addWidget(self.edtRegistryNumber, 1, 1, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnExport = QtGui.QPushButton(ExportR23NativePage1)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.horizontalLayout.addWidget(self.btnExport)
        self.btnCancel = QtGui.QPushButton(ExportR23NativePage1)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.horizontalLayout.addWidget(self.btnCancel)
        self.gridlayout.addLayout(self.horizontalLayout, 14, 0, 1, 3)
        self.cmbAccountType = CRBComboBox(ExportR23NativePage1)
        self.cmbAccountType.setObjectName(_fromUtf8("cmbAccountType"))
        self.gridlayout.addWidget(self.cmbAccountType, 2, 1, 1, 2)
        self.lblRegistryNumber = QtGui.QLabel(ExportR23NativePage1)
        self.lblRegistryNumber.setObjectName(_fromUtf8("lblRegistryNumber"))
        self.gridlayout.addWidget(self.lblRegistryNumber, 1, 0, 1, 1)
        self.chkIgnoreErrors = QtGui.QCheckBox(ExportR23NativePage1)
        self.chkIgnoreErrors.setObjectName(_fromUtf8("chkIgnoreErrors"))
        self.gridlayout.addWidget(self.chkIgnoreErrors, 10, 0, 1, 1)
        self.lblAccountType = QtGui.QLabel(ExportR23NativePage1)
        self.lblAccountType.setObjectName(_fromUtf8("lblAccountType"))
        self.gridlayout.addWidget(self.lblAccountType, 2, 0, 1, 1)
        self.chkPreliminaryInvoice = QtGui.QCheckBox(ExportR23NativePage1)
        self.chkPreliminaryInvoice.setObjectName(_fromUtf8("chkPreliminaryInvoice"))
        self.gridlayout.addWidget(self.chkPreliminaryInvoice, 3, 1, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ExportR23NativePage1)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridlayout.addWidget(self.logBrowser, 11, 0, 1, 3)
        self.chkVerboseLog = QtGui.QCheckBox(ExportR23NativePage1)
        self.chkVerboseLog.setObjectName(_fromUtf8("chkVerboseLog"))
        self.gridlayout.addWidget(self.chkVerboseLog, 9, 0, 1, 1)
        self.lblPayMethod = QtGui.QLabel(ExportR23NativePage1)
        self.lblPayMethod.setObjectName(_fromUtf8("lblPayMethod"))
        self.gridlayout.addWidget(self.lblPayMethod, 4, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 13, 0, 1, 3)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem2, 0, 0, 1, 3)
        self.progressBar = CProgressBar(ExportR23NativePage1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 12, 0, 1, 3)
        self.lblOrgStructureCode = QtGui.QLabel(ExportR23NativePage1)
        self.lblOrgStructureCode.setObjectName(_fromUtf8("lblOrgStructureCode"))
        self.gridlayout.addWidget(self.lblOrgStructureCode, 5, 0, 1, 1)
        self.edtOrgStructureCode = QtGui.QLineEdit(ExportR23NativePage1)
        self.edtOrgStructureCode.setObjectName(_fromUtf8("edtOrgStructureCode"))
        self.gridlayout.addWidget(self.edtOrgStructureCode, 5, 1, 1, 2)
        self.chkUpdateAccountNumber = QtGui.QCheckBox(ExportR23NativePage1)
        self.chkUpdateAccountNumber.setObjectName(_fromUtf8("chkUpdateAccountNumber"))
        self.gridlayout.addWidget(self.chkUpdateAccountNumber, 9, 1, 1, 1)
        self.lblDats = QtGui.QLabel(ExportR23NativePage1)
        self.lblDats.setObjectName(_fromUtf8("lblDats"))
        self.gridlayout.addWidget(self.lblDats, 6, 0, 1, 1)
        self.lblDatps = QtGui.QLabel(ExportR23NativePage1)
        self.lblDatps.setObjectName(_fromUtf8("lblDatps"))
        self.gridlayout.addWidget(self.lblDatps, 7, 0, 1, 1)
        self.edtDats = CDateEdit(ExportR23NativePage1)
        self.edtDats.setObjectName(_fromUtf8("edtDats"))
        self.gridlayout.addWidget(self.edtDats, 6, 1, 1, 1)
        self.edtDatps = CDateEdit(ExportR23NativePage1)
        self.edtDatps.setObjectName(_fromUtf8("edtDatps"))
        self.gridlayout.addWidget(self.edtDatps, 7, 1, 1, 1)
        self.chkGenInvoice = QtGui.QCheckBox(ExportR23NativePage1)
        self.chkGenInvoice.setObjectName(_fromUtf8("chkGenInvoice"))
        self.gridlayout.addWidget(self.chkGenInvoice, 10, 1, 1, 1)
        self.lblRegistryNumber.setBuddy(self.edtRegistryNumber)
        self.lblAccountType.setBuddy(self.cmbAccountType)
        self.lblPayMethod.setBuddy(self.cmbPayMethod)
        self.lblOrgStructureCode.setBuddy(self.edtOrgStructureCode)

        self.retranslateUi(ExportR23NativePage1)
        QtCore.QMetaObject.connectSlotsByName(ExportR23NativePage1)
        ExportR23NativePage1.setTabOrder(self.edtRegistryNumber, self.cmbAccountType)
        ExportR23NativePage1.setTabOrder(self.cmbAccountType, self.cmbPayMethod)
        ExportR23NativePage1.setTabOrder(self.cmbPayMethod, self.edtOrgStructureCode)
        ExportR23NativePage1.setTabOrder(self.edtOrgStructureCode, self.chkVerboseLog)
        ExportR23NativePage1.setTabOrder(self.chkVerboseLog, self.chkIgnoreErrors)
        ExportR23NativePage1.setTabOrder(self.chkIgnoreErrors, self.logBrowser)
        ExportR23NativePage1.setTabOrder(self.logBrowser, self.btnExport)
        ExportR23NativePage1.setTabOrder(self.btnExport, self.btnCancel)

    def retranslateUi(self, ExportR23NativePage1):
        ExportR23NativePage1.setWindowTitle(_translate("ExportR23NativePage1", "Form", None))
        self.cmbPayMethod.setItemText(0, _translate("ExportR23NativePage1", "посещение, койко-день", None))
        self.cmbPayMethod.setItemText(1, _translate("ExportR23NativePage1", "простая, сложная и комплексная", None))
        self.cmbPayMethod.setItemText(2, _translate("ExportR23NativePage1", "законченный случай лечения", None))
        self.btnExport.setText(_translate("ExportR23NativePage1", "экспорт", None))
        self.btnCancel.setText(_translate("ExportR23NativePage1", "прервать", None))
        self.lblRegistryNumber.setText(_translate("ExportR23NativePage1", "Номер реестра счета", None))
        self.chkIgnoreErrors.setText(_translate("ExportR23NativePage1", "Игнорировать ошибки", None))
        self.chkPreliminaryInvoice.setText(_translate("ExportR23NativePage1", "Предварительный счет", None))
        self.lblAccountType.setText(_translate("ExportR23NativePage1", "Тип счета", None))
        self.chkVerboseLog.setText(_translate("ExportR23NativePage1", "Подробный отчет", None))
        self.lblPayMethod.setText(_translate("ExportR23NativePage1", "Метод оплаты", None))
        self.lblOrgStructureCode.setToolTip(_translate("ExportR23NativePage1", "Код подразделения, в которое был направлен пациент из внешней организации", None))
        self.lblOrgStructureCode.setText(_translate("ExportR23NativePage1", "Код подразделения", None))
        self.edtOrgStructureCode.setToolTip(_translate("ExportR23NativePage1", "Код подразделения, в которое был направлен пациент из внешней организации", None))
        self.edtOrgStructureCode.setInputMask(_translate("ExportR23NativePage1", "99999; ", None))
        self.chkUpdateAccountNumber.setText(_translate("ExportR23NativePage1", "Заменить номер счета", None))
        self.lblDats.setToolTip(_translate("ExportR23NativePage1", "Используется для заполнения поля <b>DATS</b>", None))
        self.lblDats.setText(_translate("ExportR23NativePage1", "Дата формирования реестра", None))
        self.lblDatps.setToolTip(_translate("ExportR23NativePage1", "Используется для заполнения поля <b>DATPS</b>", None))
        self.lblDatps.setText(_translate("ExportR23NativePage1", "Дата формирования персонального счета", None))
        self.edtDats.setToolTip(_translate("ExportR23NativePage1", "Используется для заполнения поля <b>DATS</b>", None))
        self.edtDatps.setToolTip(_translate("ExportR23NativePage1", "Используется для заполнения поля <b>DATPS</b>", None))
        self.chkGenInvoice.setText(_translate("ExportR23NativePage1", "Формировать счет-фактуру", None))

from library.DateEdit import CDateEdit
from library.ProgressBar import CProgressBar
from library.crbcombobox import CRBComboBox
