# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CardPinRequestDialog.ui'
#
# Created: Wed Mar 19 11:01:49 2014
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_CardPinRequestDialog(object):
    def setupUi(self, CardPinRequestDialog):
        CardPinRequestDialog.setObjectName(_fromUtf8("CardPinRequestDialog"))
        CardPinRequestDialog.resize(300, 250)
        self.gridLayout = QtGui.QGridLayout(CardPinRequestDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gbCardInfo = QtGui.QGroupBox(CardPinRequestDialog)
        self.gbCardInfo.setObjectName(_fromUtf8("gbCardInfo"))
        self.verticalLayout = QtGui.QVBoxLayout(self.gbCardInfo)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tbCardInfo = QtGui.QTextBrowser(self.gbCardInfo)
        self.tbCardInfo.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tbCardInfo.setObjectName(_fromUtf8("tbCardInfo"))
        self.verticalLayout.addWidget(self.tbCardInfo)
        self.gridLayout.addWidget(self.gbCardInfo, 0, 0, 1, 4)
        self.edtPinCode = QtGui.QLineEdit(CardPinRequestDialog)
        self.edtPinCode.setMaximumSize(QtCore.QSize(70, 16777215))
        self.edtPinCode.setMaxLength(8)
        self.edtPinCode.setEchoMode(QtGui.QLineEdit.Password)
        self.edtPinCode.setObjectName(_fromUtf8("edtPinCode"))
        self.gridLayout.addWidget(self.edtPinCode, 1, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 0, 1, 1)
        self.lblPinCode = QtGui.QLabel(CardPinRequestDialog)
        self.lblPinCode.setObjectName(_fromUtf8("lblPinCode"))
        self.gridLayout.addWidget(self.lblPinCode, 1, 1, 1, 1)
        self.lblAttempts = QtGui.QLabel(CardPinRequestDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblAttempts.setFont(font)
        self.lblAttempts.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);"))
        self.lblAttempts.setText(_fromUtf8(""))
        self.lblAttempts.setAlignment(QtCore.Qt.AlignCenter)
        self.lblAttempts.setObjectName(_fromUtf8("lblAttempts"))
        self.gridLayout.addWidget(self.lblAttempts, 2, 0, 1, 4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.bCancel = QtGui.QPushButton(CardPinRequestDialog)
        self.bCancel.setFocusPolicy(QtCore.Qt.NoFocus)
        self.bCancel.setObjectName(_fromUtf8("bCancel"))
        self.horizontalLayout.addWidget(self.bCancel)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 4)
        self.lblPinCode.setBuddy(self.edtPinCode)

        self.retranslateUi(CardPinRequestDialog)
        QtCore.QObject.connect(self.bCancel, QtCore.SIGNAL(_fromUtf8("clicked()")), CardPinRequestDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CardPinRequestDialog)

    def retranslateUi(self, CardPinRequestDialog):
        CardPinRequestDialog.setWindowTitle(_translate("CardPinRequestDialog", "Запрос ПИН-кода", None))
        self.gbCardInfo.setTitle(_translate("CardPinRequestDialog", "Информация по карте", None))
        self.lblPinCode.setText(_translate("CardPinRequestDialog", "ПИН-код", None))
        self.bCancel.setText(_translate("CardPinRequestDialog", "Отмена", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    CardPinRequestDialog = QtGui.QDialog()
    ui = Ui_CardPinRequestDialog()
    ui.setupUi(CardPinRequestDialog)
    CardPinRequestDialog.show()
    sys.exit(app.exec_())

