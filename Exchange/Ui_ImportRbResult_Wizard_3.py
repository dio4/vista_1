# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportRbResult_Wizard_3.ui'
#
# Created: Fri Jun 15 12:15:23 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportRbResult_Wizard_3(object):
    def setupUi(self, ImportRbResult_Wizard_3):
        ImportRbResult_Wizard_3.setObjectName(_fromUtf8("ImportRbResult_Wizard_3"))
        ImportRbResult_Wizard_3.resize(475, 429)
        self.gridlayout = QtGui.QGridLayout(ImportRbResult_Wizard_3)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.progressBar = CProgressBar(ImportRbResult_Wizard_3)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 0, 0, 1, 1)
        self.statusLabel = QtGui.QLabel(ImportRbResult_Wizard_3)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridlayout.addWidget(self.statusLabel, 3, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ImportRbResult_Wizard_3)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridlayout.addWidget(self.logBrowser, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnAbort = QtGui.QPushButton(ImportRbResult_Wizard_3)
        self.btnAbort.setObjectName(_fromUtf8("btnAbort"))
        self.horizontalLayout.addWidget(self.btnAbort)
        self.gridlayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.retranslateUi(ImportRbResult_Wizard_3)
        QtCore.QMetaObject.connectSlotsByName(ImportRbResult_Wizard_3)

    def retranslateUi(self, ImportRbResult_Wizard_3):
        ImportRbResult_Wizard_3.setWindowTitle(QtGui.QApplication.translate("ImportRbResult_Wizard_3", "Импорт типов событий", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAbort.setText(QtGui.QApplication.translate("ImportRbResult_Wizard_3", "Прервать", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportRbResult_Wizard_3 = QtGui.QDialog()
    ui = Ui_ImportRbResult_Wizard_3()
    ui.setupUi(ImportRbResult_Wizard_3)
    ImportRbResult_Wizard_3.show()
    sys.exit(app.exec_())

