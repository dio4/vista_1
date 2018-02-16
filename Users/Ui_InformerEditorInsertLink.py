# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'InformerEditorInsertLink.ui'
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

class Ui_InsertLinkDialog(object):
    def setupUi(self, InsertLinkDialog):
        InsertLinkDialog.setObjectName(_fromUtf8("InsertLinkDialog"))
        InsertLinkDialog.resize(400, 157)
        self.verticalLayout = QtGui.QVBoxLayout(InsertLinkDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lblText = QtGui.QLabel(InsertLinkDialog)
        self.lblText.setObjectName(_fromUtf8("lblText"))
        self.verticalLayout.addWidget(self.lblText)
        self.edtText = QtGui.QLineEdit(InsertLinkDialog)
        self.edtText.setObjectName(_fromUtf8("edtText"))
        self.verticalLayout.addWidget(self.edtText)
        self.lblURL = QtGui.QLabel(InsertLinkDialog)
        self.lblURL.setObjectName(_fromUtf8("lblURL"))
        self.verticalLayout.addWidget(self.lblURL)
        self.edtURL = QtGui.QLineEdit(InsertLinkDialog)
        self.edtURL.setObjectName(_fromUtf8("edtURL"))
        self.verticalLayout.addWidget(self.edtURL)
        self.buttonBox = QtGui.QDialogButtonBox(InsertLinkDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(InsertLinkDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), InsertLinkDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), InsertLinkDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(InsertLinkDialog)

    def retranslateUi(self, InsertLinkDialog):
        InsertLinkDialog.setWindowTitle(_translate("InsertLinkDialog", "Вставить ссылку", None))
        self.lblText.setText(_translate("InsertLinkDialog", "Текст ссылки", None))
        self.lblURL.setText(_translate("InsertLinkDialog", "Адрес ссылки", None))
        self.edtURL.setPlaceholderText(_translate("InsertLinkDialog", "http://example.com/", None))

