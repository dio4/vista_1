# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportCrimea.ui'
#
# Created: Wed Dec 17 00:22:17 2014
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

class Ui_ImportCrimea(object):
    def setupUi(self, ImportCrimea):
        ImportCrimea.setObjectName(_fromUtf8("ImportCrimea"))
        ImportCrimea.resize(400, 227)
        self.gridLayout_2 = QtGui.QGridLayout(ImportCrimea)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(ImportCrimea)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.edtFilePath = QtGui.QLineEdit(ImportCrimea)
        self.edtFilePath.setObjectName(_fromUtf8("edtFilePath"))
        self.horizontalLayout.addWidget(self.edtFilePath)
        self.btnOpenFile = QtGui.QToolButton(ImportCrimea)
        self.btnOpenFile.setObjectName(_fromUtf8("btnOpenFile"))
        self.horizontalLayout.addWidget(self.btnOpenFile)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 4)
        self.progressBar = CProgressBar(ImportCrimea)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout_2.addWidget(self.progressBar, 3, 0, 1, 4)
        self.lblProgressBar = QtGui.QLabel(ImportCrimea)
        self.lblProgressBar.setText(_fromUtf8(""))
        self.lblProgressBar.setObjectName(_fromUtf8("lblProgressBar"))
        self.gridLayout_2.addWidget(self.lblProgressBar, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ImportCrimea)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 6, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 5, 1, 1, 3)

        self.retranslateUi(ImportCrimea)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ImportCrimea.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImportCrimea.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportCrimea)

    def retranslateUi(self, ImportCrimea):
        ImportCrimea.setWindowTitle(_translate("ImportCrimea", "Dialog", None))
        self.label.setText(_translate("ImportCrimea", "Путь к файлу:", None))
        self.btnOpenFile.setText(_translate("ImportCrimea", "...", None))

from library.ProgressBar import CProgressBar
