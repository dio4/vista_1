# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HintMessage.ui'
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

class Ui_MessageWindow(object):
    def setupUi(self, MessageWindow):
        MessageWindow.setObjectName(_fromUtf8("MessageWindow"))
        MessageWindow.setWindowModality(QtCore.Qt.WindowModal)
        MessageWindow.resize(196, 56)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MessageWindow.sizePolicy().hasHeightForWidth())
        MessageWindow.setSizePolicy(sizePolicy)
        MessageWindow.setAutoFillBackground(False)
        MessageWindow.setStyleSheet(_fromUtf8("background-color: rgb(38, 223, 6);\n"
"font: 75 italic 10pt \"MS Shell Dlg 2\";"))
        self.gridLayout = QtGui.QGridLayout(MessageWindow)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblTitle = QtGui.QLabel(MessageWindow)
        self.lblTitle.setObjectName(_fromUtf8("lblTitle"))
        self.gridLayout.addWidget(self.lblTitle, 0, 0, 1, 1)
        self.lblMessage = QtGui.QLabel(MessageWindow)
        self.lblMessage.setObjectName(_fromUtf8("lblMessage"))
        self.gridLayout.addWidget(self.lblMessage, 1, 0, 1, 1)

        self.retranslateUi(MessageWindow)
        QtCore.QMetaObject.connectSlotsByName(MessageWindow)

    def retranslateUi(self, MessageWindow):
        MessageWindow.setWindowTitle(_translate("MessageWindow", "Сообщение", None))
        self.lblTitle.setText(_translate("MessageWindow", "Заголовок", None))
        self.lblMessage.setText(_translate("MessageWindow", "Сообщение", None))

