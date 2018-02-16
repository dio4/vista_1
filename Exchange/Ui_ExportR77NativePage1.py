# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportR77NativePage1.ui'
#
# Created: Fri Jun 15 12:16:29 2012
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
        ExportPage1.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportPage1)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 3)
        self.progressBar = CProgressBar(ExportPage1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 2, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 3, 0, 1, 3)
        self.btnExport = QtGui.QPushButton(ExportPage1)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.gridlayout.addWidget(self.btnExport, 4, 1, 1, 1)
        self.btnCancel = QtGui.QPushButton(ExportPage1)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridlayout.addWidget(self.btnCancel, 4, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 4, 0, 1, 1)
        self.chkGroupByMKB = QtGui.QCheckBox(ExportPage1)
        self.chkGroupByMKB.setObjectName(_fromUtf8("chkGroupByMKB"))
        self.gridlayout.addWidget(self.chkGroupByMKB, 0, 0, 1, 1)

        self.retranslateUi(ExportPage1)
        QtCore.QMetaObject.connectSlotsByName(ExportPage1)

    def retranslateUi(self, ExportPage1):
        ExportPage1.setWindowTitle(QtGui.QApplication.translate("ExportPage1", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("ExportPage1", "экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("ExportPage1", "прервать", None, QtGui.QApplication.UnicodeUTF8))
        self.chkGroupByMKB.setText(QtGui.QApplication.translate("ExportPage1", "группировать по шифру МКБ", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportPage1 = QtGui.QWidget()
    ui = Ui_ExportPage1()
    ui.setupUi(ExportPage1)
    ExportPage1.show()
    sys.exit(app.exec_())

