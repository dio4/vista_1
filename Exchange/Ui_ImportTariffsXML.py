# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportTariffsXML.ui'
#
# Created: Fri Jun 15 12:16:12 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportTariffsXML(object):
    def setupUi(self, ImportTariffsXML):
        ImportTariffsXML.setObjectName(_fromUtf8("ImportTariffsXML"))
        ImportTariffsXML.resize(475, 429)
        self.gridlayout = QtGui.QGridLayout(ImportTariffsXML)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(4)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(ImportTariffsXML)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(ImportTariffsXML)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.hboxlayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportTariffsXML)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.hboxlayout.addWidget(self.btnSelectFile)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.progressBar = CProgressBar(ImportTariffsXML)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 1, 0, 1, 1)
        self.lblStatus = QtGui.QLabel(ImportTariffsXML)
        self.lblStatus.setText(_fromUtf8(""))
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.gridlayout.addWidget(self.lblStatus, 5, 0, 1, 1)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(4)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.btnImport = QtGui.QPushButton(ImportTariffsXML)
        self.btnImport.setEnabled(False)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout1.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.btnAbort = QtGui.QPushButton(ImportTariffsXML)
        self.btnAbort.setEnabled(False)
        self.btnAbort.setObjectName(_fromUtf8("btnAbort"))
        self.hboxlayout1.addWidget(self.btnAbort)
        self.btnClose = QtGui.QPushButton(ImportTariffsXML)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout1.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout1, 6, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ImportTariffsXML)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridlayout.addWidget(self.logBrowser, 4, 0, 1, 1)
        self.chkFullLog = QtGui.QCheckBox(ImportTariffsXML)
        self.chkFullLog.setObjectName(_fromUtf8("chkFullLog"))
        self.gridlayout.addWidget(self.chkFullLog, 2, 0, 1, 1)
        self.chkUpdateTariff = QtGui.QCheckBox(ImportTariffsXML)
        self.chkUpdateTariff.setObjectName(_fromUtf8("chkUpdateTariff"))
        self.gridlayout.addWidget(self.chkUpdateTariff, 3, 0, 1, 1)

        self.retranslateUi(ImportTariffsXML)
        QtCore.QMetaObject.connectSlotsByName(ImportTariffsXML)
        ImportTariffsXML.setTabOrder(self.edtFileName, self.btnSelectFile)
        ImportTariffsXML.setTabOrder(self.btnSelectFile, self.chkFullLog)
        ImportTariffsXML.setTabOrder(self.chkFullLog, self.chkUpdateTariff)
        ImportTariffsXML.setTabOrder(self.chkUpdateTariff, self.logBrowser)
        ImportTariffsXML.setTabOrder(self.logBrowser, self.btnImport)
        ImportTariffsXML.setTabOrder(self.btnImport, self.btnAbort)
        ImportTariffsXML.setTabOrder(self.btnAbort, self.btnClose)

    def retranslateUi(self, ImportTariffsXML):
        ImportTariffsXML.setWindowTitle(QtGui.QApplication.translate("ImportTariffsXML", "Импорт тарифов для договора", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportTariffsXML", "Загрузить из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("ImportTariffsXML", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("ImportTariffsXML", "Начать импорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAbort.setText(QtGui.QApplication.translate("ImportTariffsXML", "Прервать", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("ImportTariffsXML", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.chkFullLog.setText(QtGui.QApplication.translate("ImportTariffsXML", "Подробный отчет", None, QtGui.QApplication.UnicodeUTF8))
        self.chkUpdateTariff.setText(QtGui.QApplication.translate("ImportTariffsXML", "Обновлять совпадающие тарифы", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportTariffsXML = QtGui.QDialog()
    ui = Ui_ImportTariffsXML()
    ui.setupUi(ImportTariffsXML)
    ImportTariffsXML.show()
    sys.exit(app.exec_())

