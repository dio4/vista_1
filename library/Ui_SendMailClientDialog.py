# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SendMailClientDialog.ui'
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

class Ui_SendMailClientDialog(object):
    def setupUi(self, SendMailClientDialog):
        SendMailClientDialog.setObjectName(_fromUtf8("SendMailClientDialog"))
        SendMailClientDialog.resize(498, 237)
        self.gridLayout = QtGui.QGridLayout(SendMailClientDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblRecipient = QtGui.QLabel(SendMailClientDialog)
        self.lblRecipient.setObjectName(_fromUtf8("lblRecipient"))
        self.gridLayout.addWidget(self.lblRecipient, 0, 0, 1, 1)
        self.edtRecipient = QtGui.QLineEdit(SendMailClientDialog)
        self.edtRecipient.setObjectName(_fromUtf8("edtRecipient"))
        self.gridLayout.addWidget(self.edtRecipient, 0, 1, 1, 1)
        self.lblText = QtGui.QLabel(SendMailClientDialog)
        self.lblText.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblText.setObjectName(_fromUtf8("lblText"))
        self.gridLayout.addWidget(self.lblText, 1, 0, 1, 1)
        self.edtText = QtGui.QTextEdit(SendMailClientDialog)
        self.edtText.setObjectName(_fromUtf8("edtText"))
        self.gridLayout.addWidget(self.edtText, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(SendMailClientDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)
        self.lblRecipient.setBuddy(self.edtRecipient)
        self.lblText.setBuddy(self.edtText)

        self.retranslateUi(SendMailClientDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SendMailClientDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SendMailClientDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SendMailClientDialog)

    def retranslateUi(self, SendMailClientDialog):
        SendMailClientDialog.setWindowTitle(_translate("SendMailClientDialog", "Dialog", None))
        self.lblRecipient.setText(_translate("SendMailClientDialog", "Кому", None))
        self.lblText.setText(_translate("SendMailClientDialog", "Текст", None))

