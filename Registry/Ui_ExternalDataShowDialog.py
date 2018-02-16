# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExternalDataShowDialog.ui'
#
# Created: Mon Apr 21 22:20:32 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_ExternalDataShowDialog(object):
    def setupUi(self, ExternalDataShowDialog):
        ExternalDataShowDialog.setObjectName(_fromUtf8("ExternalDataShowDialog"))
        ExternalDataShowDialog.resize(400, 400)
        self.verticalLayout = QtGui.QVBoxLayout(ExternalDataShowDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gbCardData = QtGui.QGroupBox(ExternalDataShowDialog)
        self.gbCardData.setObjectName(_fromUtf8("gbCardData"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.gbCardData)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tbCardData = QtGui.QTextBrowser(self.gbCardData)
        self.tbCardData.setObjectName(_fromUtf8("tbCardData"))
        self.verticalLayout_2.addWidget(self.tbCardData)
        self.verticalLayout.addWidget(self.gbCardData)
        self.bbMain = QtGui.QDialogButtonBox(ExternalDataShowDialog)
        self.bbMain.setOrientation(QtCore.Qt.Horizontal)
        self.bbMain.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.bbMain.setObjectName(_fromUtf8("bbMain"))
        self.verticalLayout.addWidget(self.bbMain)

        self.retranslateUi(ExternalDataShowDialog)
        QtCore.QObject.connect(self.bbMain, QtCore.SIGNAL(_fromUtf8("accepted()")), ExternalDataShowDialog.accept)
        QtCore.QObject.connect(self.bbMain, QtCore.SIGNAL(_fromUtf8("rejected()")), ExternalDataShowDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ExternalDataShowDialog)

    def retranslateUi(self, ExternalDataShowDialog):
        ExternalDataShowDialog.setWindowTitle(_translate("ExternalDataShowDialog", "Информация", None))
        self.gbCardData.setTitle(_translate("ExternalDataShowDialog", "Информация", None))

