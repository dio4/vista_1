# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportRbUnit_Wizard_1.ui'
#
# Created: Fri Jun 15 12:16:02 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportRbUnit_Wizard_1(object):
    def setupUi(self, ImportRbUnit_Wizard_1):
        ImportRbUnit_Wizard_1.setObjectName(_fromUtf8("ImportRbUnit_Wizard_1"))
        ImportRbUnit_Wizard_1.resize(475, 429)
        self.gridlayout = QtGui.QGridLayout(ImportRbUnit_Wizard_1)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(ImportRbUnit_Wizard_1)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(ImportRbUnit_Wizard_1)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.hboxlayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportRbUnit_Wizard_1)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.hboxlayout.addWidget(self.btnSelectFile)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.progressBar = CProgressBar(ImportRbUnit_Wizard_1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 1, 0, 1, 1)
        self.statusLabel = QtGui.QLabel(ImportRbUnit_Wizard_1)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridlayout.addWidget(self.statusLabel, 4, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ImportRbUnit_Wizard_1)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridlayout.addWidget(self.logBrowser, 3, 0, 1, 1)
        self.chkFullLog = QtGui.QCheckBox(ImportRbUnit_Wizard_1)
        self.chkFullLog.setObjectName(_fromUtf8("chkFullLog"))
        self.gridlayout.addWidget(self.chkFullLog, 2, 0, 1, 1)

        self.retranslateUi(ImportRbUnit_Wizard_1)
        QtCore.QMetaObject.connectSlotsByName(ImportRbUnit_Wizard_1)

    def retranslateUi(self, ImportRbUnit_Wizard_1):
        ImportRbUnit_Wizard_1.setWindowTitle(QtGui.QApplication.translate("ImportRbUnit_Wizard_1", "Импорт cправочника \"Результаты События\" ", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportRbUnit_Wizard_1", "Загрузить из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("ImportRbUnit_Wizard_1", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.chkFullLog.setText(QtGui.QApplication.translate("ImportRbUnit_Wizard_1", "Подробный отчет", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportRbUnit_Wizard_1 = QtGui.QDialog()
    ui = Ui_ImportRbUnit_Wizard_1()
    ui.setupUi(ImportRbUnit_Wizard_1)
    ImportRbUnit_Wizard_1.show()
    sys.exit(app.exec_())

