# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Login.ui'
#
# Created: Fri Jul 12 19:02:48 2013
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

class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName(_fromUtf8("LoginDialog"))
        LoginDialog.resize(260, 135)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LoginDialog.sizePolicy().hasHeightForWidth())
        LoginDialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(LoginDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkSavePassword = QtGui.QCheckBox(LoginDialog)
        self.chkSavePassword.setObjectName(_fromUtf8("chkSavePassword"))
        self.gridLayout.addWidget(self.chkSavePassword, 4, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(LoginDialog)
        self.buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 3)
        self.edtLogin = QtGui.QLineEdit(LoginDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtLogin.sizePolicy().hasHeightForWidth())
        self.edtLogin.setSizePolicy(sizePolicy)
        self.edtLogin.setObjectName(_fromUtf8("edtLogin"))
        self.gridLayout.addWidget(self.edtLogin, 2, 1, 1, 2)
        self.edtPassword = QtGui.QLineEdit(LoginDialog)
        self.edtPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.edtPassword.setObjectName(_fromUtf8("edtPassword"))
        self.gridLayout.addWidget(self.edtPassword, 3, 1, 1, 2)
        self.lblLogin = QtGui.QLabel(LoginDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblLogin.sizePolicy().hasHeightForWidth())
        self.lblLogin.setSizePolicy(sizePolicy)
        self.lblLogin.setObjectName(_fromUtf8("lblLogin"))
        self.gridLayout.addWidget(self.lblLogin, 2, 0, 1, 1)
        self.lblPassword = QtGui.QLabel(LoginDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPassword.sizePolicy().hasHeightForWidth())
        self.lblPassword.setSizePolicy(sizePolicy)
        self.lblPassword.setObjectName(_fromUtf8("lblPassword"))
        self.gridLayout.addWidget(self.lblPassword, 3, 0, 1, 1)
        self.label = QtGui.QLabel(LoginDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/new/prefix1/logo_ivista.png")))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 3)
        self.lblLogin.setBuddy(self.edtLogin)
        self.lblPassword.setBuddy(self.edtPassword)

        self.retranslateUi(LoginDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LoginDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LoginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)
        LoginDialog.setTabOrder(self.edtLogin, self.edtPassword)

    def retranslateUi(self, LoginDialog):
        LoginDialog.setWindowTitle(_translate("LoginDialog", "Регистрация", None))
        self.chkSavePassword.setToolTip(_translate("LoginDialog", "Последующие подключения к базе данных\n"
"будут производиться без запроса имени и пароля.\n"
"Опция деактивируется при отключении от базы данных \n"
"через меню программы или при изменении настроек подключения.\n"
"(Не безопасно!!!)", None))
        self.chkSavePassword.setText(_translate("LoginDialog", "Сохранить пароль", None))
        self.lblLogin.setText(_translate("LoginDialog", "&Имя", None))
        self.lblPassword.setText(_translate("LoginDialog", "&Пароль", None))

import s11main_rc
