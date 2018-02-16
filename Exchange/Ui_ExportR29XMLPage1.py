# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportR29XMLPage1.ui'
#
# Created: Fri Jun 15 12:17:55 2012
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
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblRegistryNumber = QtGui.QLabel(ExportPage1)
        self.lblRegistryNumber.setObjectName(_fromUtf8("lblRegistryNumber"))
        self.horizontalLayout.addWidget(self.lblRegistryNumber)
        self.edtRegistryNumber = QtGui.QSpinBox(ExportPage1)
        self.edtRegistryNumber.setObjectName(_fromUtf8("edtRegistryNumber"))
        self.horizontalLayout.addWidget(self.edtRegistryNumber)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.chkExportTypeBelonging = QtGui.QCheckBox(ExportPage1)
        self.chkExportTypeBelonging.setObjectName(_fromUtf8("chkExportTypeBelonging"))
        self.verticalLayout.addWidget(self.chkExportTypeBelonging)
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
        self.lblRegistryNumber.setText(QtGui.QApplication.translate("ExportPage1", "Порядковый номер", None, QtGui.QApplication.UnicodeUTF8))
        self.chkExportTypeBelonging.setText(QtGui.QApplication.translate("ExportPage1", "Экспорт страховой пренадлежности", None, QtGui.QApplication.UnicodeUTF8))
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

