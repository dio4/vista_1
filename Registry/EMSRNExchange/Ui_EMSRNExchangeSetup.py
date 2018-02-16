# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Registry\EMSRNExchange\EMSRNExchangeSetup.ui'
#
# Created: Fri Jun 15 12:15:49 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_EMSRNExchangeSetupDialog(object):
    def setupUi(self, EMSRNExchangeSetupDialog):
        EMSRNExchangeSetupDialog.setObjectName(_fromUtf8("EMSRNExchangeSetupDialog"))
        EMSRNExchangeSetupDialog.resize(376, 130)
        self.gridlayout = QtGui.QGridLayout(EMSRNExchangeSetupDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblAddress = QtGui.QLabel(EMSRNExchangeSetupDialog)
        self.lblAddress.setObjectName(_fromUtf8("lblAddress"))
        self.gridlayout.addWidget(self.lblAddress, 0, 0, 1, 1)
        self.edtAddress = QtGui.QLineEdit(EMSRNExchangeSetupDialog)
        self.edtAddress.setObjectName(_fromUtf8("edtAddress"))
        self.gridlayout.addWidget(self.edtAddress, 0, 1, 1, 2)
        self.lblName = QtGui.QLabel(EMSRNExchangeSetupDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(EMSRNExchangeSetupDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 1, 2, 1, 1)
        self.lblPassword = QtGui.QLabel(EMSRNExchangeSetupDialog)
        self.lblPassword.setObjectName(_fromUtf8("lblPassword"))
        self.gridlayout.addWidget(self.lblPassword, 2, 0, 1, 1)
        self.edtPassword = QtGui.QLineEdit(EMSRNExchangeSetupDialog)
        self.edtPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.edtPassword.setObjectName(_fromUtf8("edtPassword"))
        self.gridlayout.addWidget(self.edtPassword, 2, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 2, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 151, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem2, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(EMSRNExchangeSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 4, 0, 1, 3)
        self.lblAddress.setBuddy(self.edtAddress)
        self.lblName.setBuddy(self.edtName)
        self.lblPassword.setBuddy(self.edtPassword)

        self.retranslateUi(EMSRNExchangeSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EMSRNExchangeSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EMSRNExchangeSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EMSRNExchangeSetupDialog)
        EMSRNExchangeSetupDialog.setTabOrder(self.edtAddress, self.edtName)
        EMSRNExchangeSetupDialog.setTabOrder(self.edtName, self.edtPassword)
        EMSRNExchangeSetupDialog.setTabOrder(self.edtPassword, self.buttonBox)

    def retranslateUi(self, EMSRNExchangeSetupDialog):
        EMSRNExchangeSetupDialog.setWindowTitle(QtGui.QApplication.translate("EMSRNExchangeSetupDialog", "Настройки соединения с ЭМСРН", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAddress.setText(QtGui.QApplication.translate("EMSRNExchangeSetupDialog", "&Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.edtAddress.setText(QtGui.QApplication.translate("EMSRNExchangeSetupDialog", "https://webservice.ktsz.spb.ru:4443/EMSRNExchange.asmx", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("EMSRNExchangeSetupDialog", "&Имя", None, QtGui.QApplication.UnicodeUTF8))
        self.edtName.setText(QtGui.QApplication.translate("EMSRNExchangeSetupDialog", "vista-med", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPassword.setText(QtGui.QApplication.translate("EMSRNExchangeSetupDialog", "&Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.edtPassword.setText(QtGui.QApplication.translate("EMSRNExchangeSetupDialog", "DN24aETm2ilQIeV3tMvH", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    EMSRNExchangeSetupDialog = QtGui.QDialog()
    ui = Ui_EMSRNExchangeSetupDialog()
    ui.setupUi(EMSRNExchangeSetupDialog)
    EMSRNExchangeSetupDialog.show()
    sys.exit(app.exec_())

