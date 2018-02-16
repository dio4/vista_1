# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportRbResult_Wizard_1.ui'
#
# Created: Fri Jun 15 12:15:22 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportRbResult_Wizard_1(object):
    def setupUi(self, ImportRbResult_Wizard_1):
        ImportRbResult_Wizard_1.setObjectName(_fromUtf8("ImportRbResult_Wizard_1"))
        ImportRbResult_Wizard_1.resize(475, 429)
        self.gridlayout = QtGui.QGridLayout(ImportRbResult_Wizard_1)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(ImportRbResult_Wizard_1)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(ImportRbResult_Wizard_1)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.hboxlayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportRbResult_Wizard_1)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.hboxlayout.addWidget(self.btnSelectFile)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.progressBar = CProgressBar(ImportRbResult_Wizard_1)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 2, 0, 1, 1)
        self.statusLabel = QtGui.QLabel(ImportRbResult_Wizard_1)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridlayout.addWidget(self.statusLabel, 5, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ImportRbResult_Wizard_1)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridlayout.addWidget(self.logBrowser, 4, 0, 1, 1)
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.groupBox = QtGui.QGroupBox(ImportRbResult_Wizard_1)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.vboxlayout1 = QtGui.QVBoxLayout(self.groupBox)
        self.vboxlayout1.setObjectName(_fromUtf8("vboxlayout1"))
        self.rbAskUser = QtGui.QRadioButton(self.groupBox)
        self.rbAskUser.setEnabled(True)
        self.rbAskUser.setChecked(True)
        self.rbAskUser.setObjectName(_fromUtf8("rbAskUser"))
        self.vboxlayout1.addWidget(self.rbAskUser)
        self.rbUpdate = QtGui.QRadioButton(self.groupBox)
        self.rbUpdate.setChecked(False)
        self.rbUpdate.setObjectName(_fromUtf8("rbUpdate"))
        self.vboxlayout1.addWidget(self.rbUpdate)
        self.rbSkip = QtGui.QRadioButton(self.groupBox)
        self.rbSkip.setObjectName(_fromUtf8("rbSkip"))
        self.vboxlayout1.addWidget(self.rbSkip)
        self.vboxlayout.addWidget(self.groupBox)
        self.gridlayout.addLayout(self.vboxlayout, 1, 0, 1, 1)
        self.chkFullLog = QtGui.QCheckBox(ImportRbResult_Wizard_1)
        self.chkFullLog.setObjectName(_fromUtf8("chkFullLog"))
        self.gridlayout.addWidget(self.chkFullLog, 3, 0, 1, 1)

        self.retranslateUi(ImportRbResult_Wizard_1)
        QtCore.QMetaObject.connectSlotsByName(ImportRbResult_Wizard_1)

    def retranslateUi(self, ImportRbResult_Wizard_1):
        ImportRbResult_Wizard_1.setWindowTitle(QtGui.QApplication.translate("ImportRbResult_Wizard_1", "Импорт cправочника \"Результаты События\" ", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportRbResult_Wizard_1", "Загрузить из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("ImportRbResult_Wizard_1", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ImportRbResult_Wizard_1", "Совпадающие записи", None, QtGui.QApplication.UnicodeUTF8))
        self.rbAskUser.setText(QtGui.QApplication.translate("ImportRbResult_Wizard_1", "Спрашивать действие у пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.rbUpdate.setText(QtGui.QApplication.translate("ImportRbResult_Wizard_1", "Обновлять", None, QtGui.QApplication.UnicodeUTF8))
        self.rbSkip.setText(QtGui.QApplication.translate("ImportRbResult_Wizard_1", "Пропускать", None, QtGui.QApplication.UnicodeUTF8))
        self.chkFullLog.setText(QtGui.QApplication.translate("ImportRbResult_Wizard_1", "Подробный отчет", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportRbResult_Wizard_1 = QtGui.QDialog()
    ui = Ui_ImportRbResult_Wizard_1()
    ui.setupUi(ImportRbResult_Wizard_1)
    ImportRbResult_Wizard_1.show()
    sys.exit(app.exec_())

