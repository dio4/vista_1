# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportRD2_Wizard_1.ui'
#
# Created: Fri Jun 15 12:15:14 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportRD2_Wizard_1(object):
    def setupUi(self, ExportRD2_Wizard_1):
        ExportRD2_Wizard_1.setObjectName(_fromUtf8("ExportRD2_Wizard_1"))
        ExportRD2_Wizard_1.resize(526, 456)
        self.gridlayout = QtGui.QGridLayout(ExportRD2_Wizard_1)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.cmbExportFormat = QtGui.QComboBox(ExportRD2_Wizard_1)
        self.cmbExportFormat.setObjectName(_fromUtf8("cmbExportFormat"))
        self.gridlayout.addWidget(self.cmbExportFormat, 0, 0, 1, 1)
        self.checkRAR = QtGui.QCheckBox(ExportRD2_Wizard_1)
        self.checkRAR.setChecked(True)
        self.checkRAR.setObjectName(_fromUtf8("checkRAR"))
        self.gridlayout.addWidget(self.checkRAR, 1, 0, 1, 1)
        self.progressBar = QtGui.QProgressBar(ExportRD2_Wizard_1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 2, 0, 1, 1)
        self.tableWidget = QtGui.QTableWidget(ExportRD2_Wizard_1)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridlayout.addWidget(self.tableWidget, 3, 0, 1, 1)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.btnExport = QtGui.QPushButton(ExportRD2_Wizard_1)
        self.btnExport.setCheckable(False)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.hboxlayout.addWidget(self.btnExport)
        self.btnClose = QtGui.QPushButton(ExportRD2_Wizard_1)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout, 4, 0, 1, 1)

        self.retranslateUi(ExportRD2_Wizard_1)
        QtCore.QMetaObject.connectSlotsByName(ExportRD2_Wizard_1)

    def retranslateUi(self, ExportRD2_Wizard_1):
        ExportRD2_Wizard_1.setWindowTitle(QtGui.QApplication.translate("ExportRD2_Wizard_1", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.checkRAR.setText(QtGui.QApplication.translate("ExportRD2_Wizard_1", "архивировать в RAR", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("ExportRD2_Wizard_1", "начать экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("ExportRD2_Wizard_1", "прервать", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportRD2_Wizard_1 = QtGui.QDialog()
    ui = Ui_ExportRD2_Wizard_1()
    ui.setupUi(ExportRD2_Wizard_1)
    ExportRD2_Wizard_1.show()
    sys.exit(app.exec_())

