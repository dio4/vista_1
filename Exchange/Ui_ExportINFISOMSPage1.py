# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportINFISOMSPage1.ui'
#
# Created: Fri Jun 15 12:15:13 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportINFISOMSPage1(object):
    def setupUi(self, ExportINFISOMSPage1):
        ExportINFISOMSPage1.setObjectName(_fromUtf8("ExportINFISOMSPage1"))
        ExportINFISOMSPage1.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(ExportINFISOMSPage1)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)
        self.progressBar = CProgressBar(ExportINFISOMSPage1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 5)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 1)
        self.lblRepresentativeOutRule = QtGui.QLabel(ExportINFISOMSPage1)
        self.lblRepresentativeOutRule.setObjectName(_fromUtf8("lblRepresentativeOutRule"))
        self.gridLayout.addWidget(self.lblRepresentativeOutRule, 3, 0, 1, 1)
        self.cmbRepresentativeOutRule = QtGui.QComboBox(ExportINFISOMSPage1)
        self.cmbRepresentativeOutRule.setObjectName(_fromUtf8("cmbRepresentativeOutRule"))
        self.cmbRepresentativeOutRule.addItem(_fromUtf8(""))
        self.cmbRepresentativeOutRule.addItem(_fromUtf8(""))
        self.cmbRepresentativeOutRule.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbRepresentativeOutRule, 3, 1, 1, 4)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 4, 0, 1, 3)
        self.btnExport = QtGui.QPushButton(ExportINFISOMSPage1)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.gridLayout.addWidget(self.btnExport, 4, 3, 1, 1)
        self.btnCancel = QtGui.QPushButton(ExportINFISOMSPage1)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridLayout.addWidget(self.btnCancel, 4, 4, 1, 1)

        self.retranslateUi(ExportINFISOMSPage1)
        QtCore.QMetaObject.connectSlotsByName(ExportINFISOMSPage1)

    def retranslateUi(self, ExportINFISOMSPage1):
        ExportINFISOMSPage1.setWindowTitle(QtGui.QApplication.translate("ExportINFISOMSPage1", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRepresentativeOutRule.setText(QtGui.QApplication.translate("ExportINFISOMSPage1", "Данные представителя ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRepresentativeOutRule.setItemText(0, QtGui.QApplication.translate("ExportINFISOMSPage1", "выгружать всегда", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRepresentativeOutRule.setItemText(1, QtGui.QApplication.translate("ExportINFISOMSPage1", "выгружать для иногородних", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRepresentativeOutRule.setItemText(2, QtGui.QApplication.translate("ExportINFISOMSPage1", "не выгружать", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("ExportINFISOMSPage1", "экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("ExportINFISOMSPage1", "прервать", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportINFISOMSPage1 = QtGui.QWidget()
    ui = Ui_ExportINFISOMSPage1()
    ui.setupUi(ExportINFISOMSPage1)
    ExportINFISOMSPage1.show()
    sys.exit(app.exec_())

