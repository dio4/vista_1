# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportEvents_Wizard_3.ui'
#
# Created: Fri Jun 15 12:15:20 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportEvents_Wizard_3(object):
    def setupUi(self, ImportEvents_Wizard_3):
        ImportEvents_Wizard_3.setObjectName(_fromUtf8("ImportEvents_Wizard_3"))
        ImportEvents_Wizard_3.resize(475, 429)
        self.gridlayout = QtGui.QGridLayout(ImportEvents_Wizard_3)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.progressBar = CProgressBar(ImportEvents_Wizard_3)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 0, 0, 1, 1)
        self.statusLabel = QtGui.QLabel(ImportEvents_Wizard_3)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridlayout.addWidget(self.statusLabel, 3, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ImportEvents_Wizard_3)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridlayout.addWidget(self.logBrowser, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnAbort = QtGui.QPushButton(ImportEvents_Wizard_3)
        self.btnAbort.setObjectName(_fromUtf8("btnAbort"))
        self.horizontalLayout.addWidget(self.btnAbort)
        self.gridlayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.retranslateUi(ImportEvents_Wizard_3)
        QtCore.QMetaObject.connectSlotsByName(ImportEvents_Wizard_3)

    def retranslateUi(self, ImportEvents_Wizard_3):
        ImportEvents_Wizard_3.setWindowTitle(QtGui.QApplication.translate("ImportEvents_Wizard_3", "Импорт типов событий", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAbort.setText(QtGui.QApplication.translate("ImportEvents_Wizard_3", "Прервать", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportEvents_Wizard_3 = QtGui.QDialog()
    ui = Ui_ImportEvents_Wizard_3()
    ui.setupUi(ImportEvents_Wizard_3)
    ImportEvents_Wizard_3.show()
    sys.exit(app.exec_())

