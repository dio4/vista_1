# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportMKB.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_ImportMKB(object):
    def setupUi(self, ImportMKB):
        ImportMKB.setObjectName(_fromUtf8("ImportMKB"))
        ImportMKB.resize(533, 284)
        self.gridLayout = QtGui.QGridLayout(ImportMKB)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnImport = QtGui.QPushButton(ImportMKB)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.horizontalLayout.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ImportMKB)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 2)
        self._2 = QtGui.QHBoxLayout()
        self._2.setMargin(0)
        self._2.setSpacing(6)
        self._2.setObjectName(_fromUtf8("_2"))
        self.lblLoadFrom = QtGui.QLabel(ImportMKB)
        self.lblLoadFrom.setObjectName(_fromUtf8("lblLoadFrom"))
        self._2.addWidget(self.lblLoadFrom)
        self.edtFileName = QtGui.QLineEdit(ImportMKB)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self._2.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportMKB)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self._2.addWidget(self.btnSelectFile)
        self.gridLayout.addLayout(self._2, 0, 0, 1, 2)
        self.logBrowser = QtGui.QTextBrowser(ImportMKB)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 2, 0, 1, 2)
        self.progressBar = CProgressBar(ImportMKB)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 2)

        self.retranslateUi(ImportMKB)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ImportMKB.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImportMKB.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportMKB)

    def retranslateUi(self, ImportMKB):
        ImportMKB.setWindowTitle(_translate("ImportMKB", "Импорт МКБ", None))
        self.btnImport.setText(_translate("ImportMKB", "Импорт", None))
        self.lblLoadFrom.setText(_translate("ImportMKB", "Загрузить из", None))
        self.btnSelectFile.setText(_translate("ImportMKB", "...", None))

from library.ProgressBar import CProgressBar
