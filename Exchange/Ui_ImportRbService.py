# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportRbService.ui'
#
# Created: Fri Jun 15 12:16:07 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportRbService(object):
    def setupUi(self, ImportRbService):
        ImportRbService.setObjectName(_fromUtf8("ImportRbService"))
        ImportRbService.resize(475, 429)
        self.gridlayout = QtGui.QGridLayout(ImportRbService)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(ImportRbService)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(ImportRbService)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.hboxlayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportRbService)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.hboxlayout.addWidget(self.btnSelectFile)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.progressBar = CProgressBar(ImportRbService)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 1, 0, 1, 1)
        self.statusLabel = QtGui.QLabel(ImportRbService)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridlayout.addWidget(self.statusLabel, 5, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 6, 0, 1, 1)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.btnImport = QtGui.QPushButton(ImportRbService)
        self.btnImport.setEnabled(False)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout1.addWidget(self.btnImport)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.btnAbort = QtGui.QPushButton(ImportRbService)
        self.btnAbort.setEnabled(False)
        self.btnAbort.setObjectName(_fromUtf8("btnAbort"))
        self.hboxlayout1.addWidget(self.btnAbort)
        self.btnClose = QtGui.QPushButton(ImportRbService)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout1.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout1, 7, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ImportRbService)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridlayout.addWidget(self.logBrowser, 4, 0, 1, 1)
        self.chkFullLog = QtGui.QCheckBox(ImportRbService)
        self.chkFullLog.setObjectName(_fromUtf8("chkFullLog"))
        self.gridlayout.addWidget(self.chkFullLog, 3, 0, 1, 1)
        self.chkCompareOnlyByCode = QtGui.QCheckBox(ImportRbService)
        self.chkCompareOnlyByCode.setObjectName(_fromUtf8("chkCompareOnlyByCode"))
        self.gridlayout.addWidget(self.chkCompareOnlyByCode, 2, 0, 1, 1)

        self.retranslateUi(ImportRbService)
        QtCore.QMetaObject.connectSlotsByName(ImportRbService)

    def retranslateUi(self, ImportRbService):
        ImportRbService.setWindowTitle(QtGui.QApplication.translate("ImportRbService", "Импорт справочника \"Услуги\"", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportRbService", "Загрузить из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("ImportRbService", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("ImportRbService", "Начать импорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAbort.setText(QtGui.QApplication.translate("ImportRbService", "Прервать", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("ImportRbService", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.chkFullLog.setText(QtGui.QApplication.translate("ImportRbService", "Подробный отчет", None, QtGui.QApplication.UnicodeUTF8))
        self.chkCompareOnlyByCode.setText(QtGui.QApplication.translate("ImportRbService", "Поиск совпадений только по коду", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportRbService = QtGui.QDialog()
    ui = Ui_ImportRbService()
    ui.setupUi(ImportRbService)
    ImportRbService.show()
    sys.exit(app.exec_())

