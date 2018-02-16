# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Registry\MIACExchange\MIACExchangeSetup.ui'
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

class Ui_MIACExchangeSetupDialog(object):
    def setupUi(self, MIACExchangeSetupDialog):
        MIACExchangeSetupDialog.setObjectName(_fromUtf8("MIACExchangeSetupDialog"))
        MIACExchangeSetupDialog.resize(376, 132)
        self.gridlayout = QtGui.QGridLayout(MIACExchangeSetupDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblAddress = QtGui.QLabel(MIACExchangeSetupDialog)
        self.lblAddress.setObjectName(_fromUtf8("lblAddress"))
        self.gridlayout.addWidget(self.lblAddress, 0, 0, 1, 1)
        self.edtAddress = QtGui.QLineEdit(MIACExchangeSetupDialog)
        self.edtAddress.setObjectName(_fromUtf8("edtAddress"))
        self.gridlayout.addWidget(self.edtAddress, 0, 1, 1, 2)
        self.lblPostBoxName = QtGui.QLabel(MIACExchangeSetupDialog)
        self.lblPostBoxName.setObjectName(_fromUtf8("lblPostBoxName"))
        self.gridlayout.addWidget(self.lblPostBoxName, 1, 0, 1, 1)
        self.edtPostBoxName = QtGui.QLineEdit(MIACExchangeSetupDialog)
        self.edtPostBoxName.setObjectName(_fromUtf8("edtPostBoxName"))
        self.gridlayout.addWidget(self.edtPostBoxName, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 151, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 4, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(MIACExchangeSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 5, 0, 1, 3)
        self.chkCompress = QtGui.QCheckBox(MIACExchangeSetupDialog)
        self.chkCompress.setObjectName(_fromUtf8("chkCompress"))
        self.gridlayout.addWidget(self.chkCompress, 2, 1, 1, 2)
        self.chkSendByDefault = QtGui.QCheckBox(MIACExchangeSetupDialog)
        self.chkSendByDefault.setObjectName(_fromUtf8("chkSendByDefault"))
        self.gridlayout.addWidget(self.chkSendByDefault, 3, 1, 1, 2)
        self.lblAddress.setBuddy(self.edtAddress)
        self.lblPostBoxName.setBuddy(self.edtPostBoxName)

        self.retranslateUi(MIACExchangeSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MIACExchangeSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), MIACExchangeSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(MIACExchangeSetupDialog)
        MIACExchangeSetupDialog.setTabOrder(self.edtAddress, self.edtPostBoxName)
        MIACExchangeSetupDialog.setTabOrder(self.edtPostBoxName, self.chkCompress)
        MIACExchangeSetupDialog.setTabOrder(self.chkCompress, self.chkSendByDefault)
        MIACExchangeSetupDialog.setTabOrder(self.chkSendByDefault, self.buttonBox)

    def retranslateUi(self, MIACExchangeSetupDialog):
        MIACExchangeSetupDialog.setWindowTitle(QtGui.QApplication.translate("MIACExchangeSetupDialog", "Настройки соединения с МИАЦ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAddress.setText(QtGui.QApplication.translate("MIACExchangeSetupDialog", "&Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPostBoxName.setText(QtGui.QApplication.translate("MIACExchangeSetupDialog", "&Папка", None, QtGui.QApplication.UnicodeUTF8))
        self.chkCompress.setText(QtGui.QApplication.translate("MIACExchangeSetupDialog", "Сжимать данные", None, QtGui.QApplication.UnicodeUTF8))
        self.chkSendByDefault.setText(QtGui.QApplication.translate("MIACExchangeSetupDialog", "По умолчанию передавать данные ", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MIACExchangeSetupDialog = QtGui.QDialog()
    ui = Ui_MIACExchangeSetupDialog()
    ui.setupUi(MIACExchangeSetupDialog)
    MIACExchangeSetupDialog.show()
    sys.exit(app.exec_())

