# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PreferencesDialog.ui'
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

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName(_fromUtf8("PreferencesDialog"))
        PreferencesDialog.setWindowModality(QtCore.Qt.WindowModal)
        PreferencesDialog.resize(480, 182)
        self.gridLayout_2 = QtGui.QGridLayout(PreferencesDialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnTestConnect = QtGui.QPushButton(PreferencesDialog)
        self.btnTestConnect.setEnabled(False)
        self.btnTestConnect.setObjectName(_fromUtf8("btnTestConnect"))
        self.horizontalLayout.addWidget(self.btnTestConnect)
        self.gridLayout_2.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 3, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblURL = QtGui.QLabel(PreferencesDialog)
        self.lblURL.setObjectName(_fromUtf8("lblURL"))
        self.gridLayout.addWidget(self.lblURL, 0, 0, 1, 1)
        self.edtURL = QtGui.QLineEdit(PreferencesDialog)
        self.edtURL.setObjectName(_fromUtf8("edtURL"))
        self.gridLayout.addWidget(self.edtURL, 0, 1, 1, 1)
        self.label = QtGui.QLabel(PreferencesDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.edtUser = QtGui.QLineEdit(PreferencesDialog)
        self.edtUser.setObjectName(_fromUtf8("edtUser"))
        self.gridLayout.addWidget(self.edtUser, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(PreferencesDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.edtPassword = QtGui.QLineEdit(PreferencesDialog)
        self.edtPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.edtPassword.setObjectName(_fromUtf8("edtPassword"))
        self.gridLayout.addWidget(self.edtPassword, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 4, 0, 1, 1)

        self.retranslateUi(PreferencesDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PreferencesDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PreferencesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)
        PreferencesDialog.setTabOrder(self.edtURL, self.edtUser)
        PreferencesDialog.setTabOrder(self.edtUser, self.edtPassword)
        PreferencesDialog.setTabOrder(self.edtPassword, self.btnTestConnect)
        PreferencesDialog.setTabOrder(self.btnTestConnect, self.buttonBox)

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(_translate("PreferencesDialog", "Настройки", None))
        self.btnTestConnect.setText(_translate("PreferencesDialog", "Проверить соединение", None))
        self.lblURL.setText(_translate("PreferencesDialog", "URL", None))
        self.label.setText(_translate("PreferencesDialog", "Логин", None))
        self.label_2.setText(_translate("PreferencesDialog", "Пароль", None))

