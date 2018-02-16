# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportR74NATIVEPage1.ui'
#
# Created: Fri Jun 15 12:16:20 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportR74NATIVEPage1(object):
    def setupUi(self, ExportR74NATIVEPage1):
        ExportR74NATIVEPage1.setObjectName(_fromUtf8("ExportR74NATIVEPage1"))
        ExportR74NATIVEPage1.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportR74NATIVEPage1)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 0, 0, 1, 3)
        self.progressBar = CProgressBar(ExportR74NATIVEPage1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 1, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 2, 0, 1, 3)
        self.btnExport = QtGui.QPushButton(ExportR74NATIVEPage1)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.gridlayout.addWidget(self.btnExport, 3, 1, 1, 1)
        self.btnCancel = QtGui.QPushButton(ExportR74NATIVEPage1)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.gridlayout.addWidget(self.btnCancel, 3, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 3, 0, 1, 1)

        self.retranslateUi(ExportR74NATIVEPage1)
        QtCore.QMetaObject.connectSlotsByName(ExportR74NATIVEPage1)

    def retranslateUi(self, ExportR74NATIVEPage1):
        ExportR74NATIVEPage1.setWindowTitle(QtGui.QApplication.translate("ExportR74NATIVEPage1", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("ExportR74NATIVEPage1", "экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("ExportR74NATIVEPage1", "прервать", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportR74NATIVEPage1 = QtGui.QWidget()
    ui = Ui_ExportR74NATIVEPage1()
    ui.setupUi(ExportR74NATIVEPage1)
    ExportR74NATIVEPage1.show()
    sys.exit(app.exec_())

