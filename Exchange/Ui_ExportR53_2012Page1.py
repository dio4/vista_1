# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportR53_2012Page1.ui'
#
# Created: Fri Jun 15 12:17:56 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportPage1(object):
    def setupUi(self, ExportPage1):
        ExportPage1.setObjectName(_fromUtf8("ExportPage1"))
        ExportPage1.resize(508, 415)
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
        ExportPage1.setWindowTitle(QtGui.QApplication.translate("ExportPage1", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.lblServiceInfoFileName.setText(QtGui.QApplication.translate("ExportPage1", "Имя файла с информацией о предварительном реестре", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectServiceInfoFileName.setText(QtGui.QApplication.translate("ExportPage1", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRegistryNumber.setText(QtGui.QApplication.translate("ExportPage1", "Порядковый номер реестра", None, QtGui.QApplication.UnicodeUTF8))
        self.lblExportType.setText(QtGui.QApplication.translate("ExportPage1", "Тип экспорта", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbExportType.setItemText(0, QtGui.QApplication.translate("ExportPage1", "ТФОМС", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbExportType.setItemText(1, QtGui.QApplication.translate("ExportPage1", "Внутритерриториальные 2012", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbExportType.setItemText(2, QtGui.QApplication.translate("ExportPage1", "Иногородние 2011.11", None, QtGui.QApplication.UnicodeUTF8))
        self.chkGroupByService.setText(QtGui.QApplication.translate("ExportPage1", "Группировать по профилям оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.chkVerboseLog.setText(QtGui.QApplication.translate("ExportPage1", "Подробный отчет", None, QtGui.QApplication.UnicodeUTF8))
        self.chkIgnoreErrors.setText(QtGui.QApplication.translate("ExportPage1", "Игнорировать ошибки", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("ExportPage1", "экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("ExportPage1", "прервать", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportPage1 = QtGui.QWidget()
    ui = Ui_ExportPage1()
    ui.setupUi(ExportPage1)
    ExportPage1.show()
    sys.exit(app.exec_())

