# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ActionsTemplatePrintDialog.ui'
#
# Created: Thu Jul 23 12:53:33 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_ActionsTemplatePrintDialog(object):
    def setupUi(self, ActionsTemplatePrintDialog):
        ActionsTemplatePrintDialog.setObjectName(_fromUtf8("ActionsTemplatePrintDialog"))
        ActionsTemplatePrintDialog.resize(700, 400)
        self.verticalLayout = QtGui.QVBoxLayout(ActionsTemplatePrintDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tblTemplate = CActionTemplatePrintTableView(ActionsTemplatePrintDialog)
        self.tblTemplate.setObjectName(_fromUtf8("tblTemplate"))
        self.verticalLayout.addWidget(self.tblTemplate)
        self.buttonBox = QtGui.QDialogButtonBox(ActionsTemplatePrintDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ActionsTemplatePrintDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ActionsTemplatePrintDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ActionsTemplatePrintDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ActionsTemplatePrintDialog)

    def retranslateUi(self, ActionsTemplatePrintDialog):
        ActionsTemplatePrintDialog.setWindowTitle(_translate("ActionsTemplatePrintDialog", "Выбор шаблона печати", None))

from library.ActionsTemplatePrint import CActionTemplatePrintTableView
