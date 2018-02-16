# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportR53NativePage1.ui'
#
# Created: Fri Jun 15 12:17:13 2012
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
        ExportPage1.resize(433, 386)
        self.verticalLayout = QtGui.QVBoxLayout(ExportPage1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.lblExportType = QtGui.QLabel(ExportPage1)
        self.lblExportType.setObjectName(_fromUtf8("lblExportType"))
        self.horizontalLayout_3.addWidget(self.lblExportType)
        self.cmbExportType = QtGui.QComboBox(ExportPage1)
        self.cmbExportType.setObjectName(_fromUtf8("cmbExportType"))
        self.cmbExportType.addItem(_fromUtf8(""))
        self.cmbExportType.addItem(_fromUtf8(""))
        self.cmbExportType.addItem(_fromUtf8(""))
        self.cmbExportType.addItem(_fromUtf8(""))
        self.cmbExportType.addItem(_fromUtf8(""))
        self.cmbExportType.addItem(_fromUtf8(""))
        self.horizontalLayout_3.addWidget(self.cmbExportType)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.lblRegistryNumber = QtGui.QLabel(ExportPage1)
        self.lblRegistryNumber.setObjectName(_fromUtf8("lblRegistryNumber"))
        self.horizontalLayout_5.addWidget(self.lblRegistryNumber)
        self.edtRegistryNumber = QtGui.QSpinBox(ExportPage1)
        self.edtRegistryNumber.setObjectName(_fromUtf8("edtRegistryNumber"))
        self.horizontalLayout_5.addWidget(self.edtRegistryNumber)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblInterval = QtGui.QLabel(ExportPage1)
        self.lblInterval.setObjectName(_fromUtf8("lblInterval"))
        self.horizontalLayout.addWidget(self.lblInterval)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lblFrom = QtGui.QLabel(ExportPage1)
        self.lblFrom.setObjectName(_fromUtf8("lblFrom"))
        self.horizontalLayout.addWidget(self.lblFrom)
        self.edtBegDate = CDateEdit(ExportPage1)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.horizontalLayout.addWidget(self.edtBegDate)
        self.lblTo = QtGui.QLabel(ExportPage1)
        self.lblTo.setObjectName(_fromUtf8("lblTo"))
        self.horizontalLayout.addWidget(self.lblTo)
        self.edtEndDate = CDateEdit(ExportPage1)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.horizontalLayout.addWidget(self.edtEndDate)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtGui.QLabel(ExportPage1)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.edtServiceInfoFileName = QtGui.QLineEdit(ExportPage1)
        self.edtServiceInfoFileName.setObjectName(_fromUtf8("edtServiceInfoFileName"))
        self.horizontalLayout_4.addWidget(self.edtServiceInfoFileName)
        self.btnSelectServiceInfoFileName = QtGui.QToolButton(ExportPage1)
        self.btnSelectServiceInfoFileName.setObjectName(_fromUtf8("btnSelectServiceInfoFileName"))
        self.horizontalLayout_4.addWidget(self.btnSelectServiceInfoFileName)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
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
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
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
        self.lblExportType.setText(QtGui.QApplication.translate("ExportPage1", "Тип экспорта", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbExportType.setItemText(0, QtGui.QApplication.translate("ExportPage1", "Иногородние", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbExportType.setItemText(1, QtGui.QApplication.translate("ExportPage1", "Внутри территориальный", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbExportType.setItemText(2, QtGui.QApplication.translate("ExportPage1", "ТФОМС", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbExportType.setItemText(3, QtGui.QApplication.translate("ExportPage1", "ДМС", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbExportType.setItemText(4, QtGui.QApplication.translate("ExportPage1", "Иногородние 2011.10", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbExportType.setItemText(5, QtGui.QApplication.translate("ExportPage1", "Предварительный реестр - служебная информация", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRegistryNumber.setText(QtGui.QApplication.translate("ExportPage1", "Порядковый номер реестра", None, QtGui.QApplication.UnicodeUTF8))
        self.lblInterval.setText(QtGui.QApplication.translate("ExportPage1", "Период", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFrom.setText(QtGui.QApplication.translate("ExportPage1", "с", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTo.setText(QtGui.QApplication.translate("ExportPage1", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ExportPage1", "Имя файла с  информацией о предварительном реестре:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectServiceInfoFileName.setText(QtGui.QApplication.translate("ExportPage1", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.chkGroupByService.setText(QtGui.QApplication.translate("ExportPage1", "Группировать по профилям оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.chkVerboseLog.setText(QtGui.QApplication.translate("ExportPage1", "Подробный отчет", None, QtGui.QApplication.UnicodeUTF8))
        self.chkIgnoreErrors.setText(QtGui.QApplication.translate("ExportPage1", "Игнорировать ошибки", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("ExportPage1", "экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("ExportPage1", "прервать", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar
from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportPage1 = QtGui.QWidget()
    ui = Ui_ExportPage1()
    ui.setupUi(ExportPage1)
    ExportPage1.show()
    sys.exit(app.exec_())

