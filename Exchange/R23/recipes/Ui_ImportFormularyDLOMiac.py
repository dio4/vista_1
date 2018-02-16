# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Exchange\R23\recipes\ImportFormularyDLOMiac.ui'
#
# Created: Thu Sep 03 18:54:32 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ImportFormularyDLOMiacDialog(object):
    def setupUi(self, ImportFormularyDLOMiacDialog):
        ImportFormularyDLOMiacDialog.setObjectName(_fromUtf8("ImportFormularyDLOMiacDialog"))
        ImportFormularyDLOMiacDialog.resize(724, 571)
        self.gridLayout = QtGui.QGridLayout(ImportFormularyDLOMiacDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.statusLabel = QtGui.QLabel(ImportFormularyDLOMiacDialog)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridLayout.addWidget(self.statusLabel, 7, 0, 1, 1)
        self.progressBar = CProgressBar(ImportFormularyDLOMiacDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 5, 0, 1, 1)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.btnImport = QtGui.QPushButton(ImportFormularyDLOMiacDialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.btnClose = QtGui.QPushButton(ImportFormularyDLOMiacDialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.hboxlayout, 9, 0, 1, 2)
        self._2 = QtGui.QHBoxLayout()
        self._2.setSpacing(6)
        self._2.setMargin(0)
        self._2.setObjectName(_fromUtf8("_2"))
        self.lblLoadFrom = QtGui.QLabel(ImportFormularyDLOMiacDialog)
        self.lblLoadFrom.setObjectName(_fromUtf8("lblLoadFrom"))
        self._2.addWidget(self.lblLoadFrom)
        self.edtFileName = QtGui.QLineEdit(ImportFormularyDLOMiacDialog)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self._2.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportFormularyDLOMiacDialog)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self._2.addWidget(self.btnSelectFile)
        self.gridLayout.addLayout(self._2, 1, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.logBrowser = QtGui.QTextBrowser(ImportFormularyDLOMiacDialog)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 8, 0, 1, 2)

        self.retranslateUi(ImportFormularyDLOMiacDialog)
        QtCore.QMetaObject.connectSlotsByName(ImportFormularyDLOMiacDialog)
        ImportFormularyDLOMiacDialog.setTabOrder(self.logBrowser, self.btnImport)
        ImportFormularyDLOMiacDialog.setTabOrder(self.btnImport, self.btnClose)

    def retranslateUi(self, ImportFormularyDLOMiacDialog):
        ImportFormularyDLOMiacDialog.setWindowTitle(_translate("ImportFormularyDLOMiacDialog", "Импорт справочников лекарственных средств из МИАЦ в МИС", None))
        self.btnImport.setText(_translate("ImportFormularyDLOMiacDialog", "Начать Импортирование", None))
        self.btnClose.setText(_translate("ImportFormularyDLOMiacDialog", "Закрыть", None))
        self.lblLoadFrom.setText(_translate("ImportFormularyDLOMiacDialog", "Загрузить из", None))
        self.btnSelectFile.setText(_translate("ImportFormularyDLOMiacDialog", "...", None))

from library.ProgressBar import CProgressBar
