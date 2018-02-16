# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportR46XMLPage1.ui'
#
# Created: Wed Feb 04 00:45:57 2015
#      by: PyQt4 UI code generator 4.11.2
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

class Ui_ExportPage1(object):
    def setupUi(self, ExportPage1):
        ExportPage1.setObjectName(_fromUtf8("ExportPage1"))
        ExportPage1.resize(508, 436)
        self.verticalLayout = QtGui.QVBoxLayout(ExportPage1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lblServiceInfoFileName = QtGui.QLabel(ExportPage1)
        self.lblServiceInfoFileName.setObjectName(_fromUtf8("lblServiceInfoFileName"))
        self.verticalLayout.addWidget(self.lblServiceInfoFileName)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.edtServiceInfoFileName = QtGui.QLineEdit(ExportPage1)
        self.edtServiceInfoFileName.setObjectName(_fromUtf8("edtServiceInfoFileName"))
        self.horizontalLayout.addWidget(self.edtServiceInfoFileName)
        self.btnSelectServiceInfoFileName = QtGui.QToolButton(ExportPage1)
        self.btnSelectServiceInfoFileName.setObjectName(_fromUtf8("btnSelectServiceInfoFileName"))
        self.horizontalLayout.addWidget(self.btnSelectServiceInfoFileName)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.lblRegistryNumber = QtGui.QLabel(ExportPage1)
        self.lblRegistryNumber.setObjectName(_fromUtf8("lblRegistryNumber"))
        self.horizontalLayout_5.addWidget(self.lblRegistryNumber)
        self.edtRegistryNumber = QtGui.QSpinBox(ExportPage1)
        self.edtRegistryNumber.setObjectName(_fromUtf8("edtRegistryNumber"))
        self.horizontalLayout_5.addWidget(self.edtRegistryNumber)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.lblExportType = QtGui.QLabel(ExportPage1)
        self.lblExportType.setEnabled(False)
        self.lblExportType.setObjectName(_fromUtf8("lblExportType"))
        self.horizontalLayout_3.addWidget(self.lblExportType)
        self.cmbExportType = QtGui.QComboBox(ExportPage1)
        self.cmbExportType.setEnabled(False)
        self.cmbExportType.setObjectName(_fromUtf8("cmbExportType"))
        self.cmbExportType.addItem(_fromUtf8(""))
        self.cmbExportType.addItem(_fromUtf8(""))
        self.cmbExportType.addItem(_fromUtf8(""))
        self.horizontalLayout_3.addWidget(self.cmbExportType)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.chkGroupByService = QtGui.QCheckBox(ExportPage1)
        self.chkGroupByService.setObjectName(_fromUtf8("chkGroupByService"))
        self.verticalLayout.addWidget(self.chkGroupByService)
        self.chkVerboseLog = QtGui.QCheckBox(ExportPage1)
        self.chkVerboseLog.setObjectName(_fromUtf8("chkVerboseLog"))
        self.verticalLayout.addWidget(self.chkVerboseLog)
        self.chkIgnoreErrors = QtGui.QCheckBox(ExportPage1)
        self.chkIgnoreErrors.setObjectName(_fromUtf8("chkIgnoreErrors"))
        self.verticalLayout.addWidget(self.chkIgnoreErrors)
        self.grbSMO = QtGui.QGroupBox(ExportPage1)
        self.grbSMO.setObjectName(_fromUtf8("grbSMO"))
        self.gridLayout = QtGui.QGridLayout(self.grbSMO)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lbl85001 = QtGui.QLabel(self.grbSMO)
        self.lbl85001.setObjectName(_fromUtf8("lbl85001"))
        self.gridLayout.addWidget(self.lbl85001, 0, 0, 1, 1)
        self.lbl85002 = QtGui.QLabel(self.grbSMO)
        self.lbl85002.setObjectName(_fromUtf8("lbl85002"))
        self.gridLayout.addWidget(self.lbl85002, 1, 0, 1, 1)
        self.lbl85003 = QtGui.QLabel(self.grbSMO)
        self.lbl85003.setObjectName(_fromUtf8("lbl85003"))
        self.gridLayout.addWidget(self.lbl85003, 2, 0, 1, 1)
        self.edt85001 = QtGui.QLineEdit(self.grbSMO)
        self.edt85001.setObjectName(_fromUtf8("edt85001"))
        self.gridLayout.addWidget(self.edt85001, 0, 1, 1, 1)
        self.edt85002 = QtGui.QLineEdit(self.grbSMO)
        self.edt85002.setObjectName(_fromUtf8("edt85002"))
        self.gridLayout.addWidget(self.edt85002, 1, 1, 1, 1)
        self.edt85003 = QtGui.QLineEdit(self.grbSMO)
        self.edt85003.setObjectName(_fromUtf8("edt85003"))
        self.gridLayout.addWidget(self.edt85003, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.grbSMO)
        self.logBrowser = QtGui.QTextBrowser(ExportPage1)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.verticalLayout.addWidget(self.logBrowser)
        self.progressBar = CProgressBar(ExportPage1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.verticalLayout.addWidget(self.progressBar)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.btnExport = QtGui.QPushButton(ExportPage1)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.horizontalLayout_2.addWidget(self.btnExport)
        self.btnCancel = QtGui.QPushButton(ExportPage1)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.horizontalLayout_2.addWidget(self.btnCancel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(ExportPage1)
        QtCore.QMetaObject.connectSlotsByName(ExportPage1)

    def retranslateUi(self, ExportPage1):
        ExportPage1.setWindowTitle(_translate("ExportPage1", "Form", None))
        self.lblServiceInfoFileName.setText(_translate("ExportPage1", "Имя файла с информацией о предварительном реестре", None))
        self.btnSelectServiceInfoFileName.setText(_translate("ExportPage1", "...", None))
        self.lblRegistryNumber.setText(_translate("ExportPage1", "Порядковый номер реестра", None))
        self.lblExportType.setText(_translate("ExportPage1", "Тип экспорта", None))
        self.cmbExportType.setItemText(0, _translate("ExportPage1", "ТФОМС", None))
        self.cmbExportType.setItemText(1, _translate("ExportPage1", "Внутритерриториальные 2012", None))
        self.cmbExportType.setItemText(2, _translate("ExportPage1", "Иногородние 2011.11", None))
        self.chkGroupByService.setText(_translate("ExportPage1", "Группировать по профилям оплаты", None))
        self.chkVerboseLog.setText(_translate("ExportPage1", "Подробный отчет", None))
        self.chkIgnoreErrors.setText(_translate("ExportPage1", "Игнорировать ошибки", None))
        self.grbSMO.setTitle(_translate("ExportPage1", "Количество денег по страховой", None))
        self.lbl85001.setText(_translate("ExportPage1", "85001", None))
        self.lbl85002.setText(_translate("ExportPage1", "85002", None))
        self.lbl85003.setText(_translate("ExportPage1", "85003", None))
        self.btnExport.setText(_translate("ExportPage1", "экспорт", None))
        self.btnCancel.setText(_translate("ExportPage1", "прервать", None))

from library.ProgressBar import CProgressBar
