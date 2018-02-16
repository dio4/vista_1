# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportActions.ui'
#
# Created: Fri Jun 15 12:15:16 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportActions(object):
    def setupUi(self, ImportActions):
        ImportActions.setObjectName(_fromUtf8("ImportActions"))
        ImportActions.resize(475, 429)
        self.gridlayout = QtGui.QGridLayout(ImportActions)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(ImportActions)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(ImportActions)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.hboxlayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportActions)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.hboxlayout.addWidget(self.btnSelectFile)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.progressBar = CProgressBar(ImportActions)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 3, 0, 1, 1)
        self.statusLabel = QtGui.QLabel(ImportActions)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridlayout.addWidget(self.statusLabel, 6, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 7, 0, 1, 1)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.btnImport = QtGui.QPushButton(ImportActions)
        self.btnImport.setEnabled(False)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout1.addWidget(self.btnImport)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.btnAbort = QtGui.QPushButton(ImportActions)
        self.btnAbort.setEnabled(False)
        self.btnAbort.setObjectName(_fromUtf8("btnAbort"))
        self.hboxlayout1.addWidget(self.btnAbort)
        self.btnClose = QtGui.QPushButton(ImportActions)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout1.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout1, 8, 0, 1, 1)
        self.logBrowser = QtGui.QTextBrowser(ImportActions)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridlayout.addWidget(self.logBrowser, 5, 0, 1, 1)
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.groupBox = QtGui.QGroupBox(ImportActions)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.vboxlayout1 = QtGui.QVBoxLayout(self.groupBox)
        self.vboxlayout1.setObjectName(_fromUtf8("vboxlayout1"))
        self.rbAskUser = QtGui.QRadioButton(self.groupBox)
        self.rbAskUser.setChecked(True)
        self.rbAskUser.setObjectName(_fromUtf8("rbAskUser"))
        self.vboxlayout1.addWidget(self.rbAskUser)
        self.rbUpdate = QtGui.QRadioButton(self.groupBox)
        self.rbUpdate.setObjectName(_fromUtf8("rbUpdate"))
        self.vboxlayout1.addWidget(self.rbUpdate)
        self.rbSkip = QtGui.QRadioButton(self.groupBox)
        self.rbSkip.setObjectName(_fromUtf8("rbSkip"))
        self.vboxlayout1.addWidget(self.rbSkip)
        self.vboxlayout.addWidget(self.groupBox)
        self.gridlayout.addLayout(self.vboxlayout, 1, 0, 1, 1)
        self.chkFullLog = QtGui.QCheckBox(ImportActions)
        self.chkFullLog.setObjectName(_fromUtf8("chkFullLog"))
        self.gridlayout.addWidget(self.chkFullLog, 4, 0, 1, 1)
        self.chkUseFlatCode = QtGui.QCheckBox(ImportActions)
        self.chkUseFlatCode.setObjectName(_fromUtf8("chkUseFlatCode"))
        self.gridlayout.addWidget(self.chkUseFlatCode, 2, 0, 1, 1)

        self.retranslateUi(ImportActions)
        QtCore.QMetaObject.connectSlotsByName(ImportActions)

    def retranslateUi(self, ImportActions):
        ImportActions.setWindowTitle(QtGui.QApplication.translate("ImportActions", "Импорт типов действий", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportActions", "Загрузить из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("ImportActions", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("ImportActions", "Начать импорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAbort.setText(QtGui.QApplication.translate("ImportActions", "Прервать", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("ImportActions", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ImportActions", "Совпадающие записи", None, QtGui.QApplication.UnicodeUTF8))
        self.rbAskUser.setText(QtGui.QApplication.translate("ImportActions", "Спрашивать действие у пользователя", None, QtGui.QApplication.UnicodeUTF8))
        self.rbUpdate.setText(QtGui.QApplication.translate("ImportActions", "Обновлять", None, QtGui.QApplication.UnicodeUTF8))
        self.rbSkip.setText(QtGui.QApplication.translate("ImportActions", "Пропускать", None, QtGui.QApplication.UnicodeUTF8))
        self.chkFullLog.setText(QtGui.QApplication.translate("ImportActions", "Подробный отчет", None, QtGui.QApplication.UnicodeUTF8))
        self.chkUseFlatCode.setText(QtGui.QApplication.translate("ImportActions", "Использовать \"плоский\" код для сравнения типов действий", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportActions = QtGui.QDialog()
    ui = Ui_ImportActions()
    ui.setupUi(ImportActions)
    ImportActions.show()
    sys.exit(app.exec_())

