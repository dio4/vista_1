# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExposeStatisticsDialog.ui'
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

class Ui_ExposeStatisticsDialog(object):
    def setupUi(self, ExposeStatisticsDialog):
        ExposeStatisticsDialog.setObjectName(_fromUtf8("ExposeStatisticsDialog"))
        ExposeStatisticsDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ExposeStatisticsDialog.resize(493, 190)
        ExposeStatisticsDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ExposeStatisticsDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        spacerItem = QtGui.QSpacerItem(20, 61, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ExposeStatisticsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.txtStats = QtGui.QTextEdit(ExposeStatisticsDialog)
        self.txtStats.setObjectName(_fromUtf8("txtStats"))
        self.gridlayout.addWidget(self.txtStats, 0, 0, 1, 1)

        self.retranslateUi(ExposeStatisticsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ExposeStatisticsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ExposeStatisticsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ExposeStatisticsDialog)

    def retranslateUi(self, ExposeStatisticsDialog):
        ExposeStatisticsDialog.setWindowTitle(_translate("ExposeStatisticsDialog", "Внимание!", None))

