# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Accounting\AccountEditDialog.ui'
#
# Created: Fri Jun 15 12:14:58 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_AccountEditDialog(object):
    def setupUi(self, AccountEditDialog):
        AccountEditDialog.setObjectName(_fromUtf8("AccountEditDialog"))
        AccountEditDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        AccountEditDialog.resize(330, 111)
        AccountEditDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(AccountEditDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.buttonBox = QtGui.QDialogButtonBox(AccountEditDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 4, 0, 1, 3)
        self.edtDate = CDateEdit(AccountEditDialog)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridlayout.addWidget(self.edtDate, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(71, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 1, 2, 1, 1)
        self.lblDate = QtGui.QLabel(AccountEditDialog)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridlayout.addWidget(self.lblDate, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.edtNumber = QtGui.QLineEdit(AccountEditDialog)
        self.edtNumber.setObjectName(_fromUtf8("edtNumber"))
        self.gridlayout.addWidget(self.edtNumber, 0, 1, 1, 2)
        self.lblNumber = QtGui.QLabel(AccountEditDialog)
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.gridlayout.addWidget(self.lblNumber, 0, 0, 1, 1)
        self.label = QtGui.QLabel(AccountEditDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 2, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 2, 2, 1, 1)
        self.edtExposeDate = CDateEdit(AccountEditDialog)
        self.edtExposeDate.setObjectName(_fromUtf8("edtExposeDate"))
        self.gridlayout.addWidget(self.edtExposeDate, 2, 1, 1, 1)
        self.lblDate.setBuddy(self.edtDate)
        self.lblNumber.setBuddy(self.edtNumber)
        self.label.setBuddy(self.edtExposeDate)

        self.retranslateUi(AccountEditDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AccountEditDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AccountEditDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AccountEditDialog)
        AccountEditDialog.setTabOrder(self.edtNumber, self.edtDate)
        AccountEditDialog.setTabOrder(self.edtDate, self.edtExposeDate)
        AccountEditDialog.setTabOrder(self.edtExposeDate, self.buttonBox)

    def retranslateUi(self, AccountEditDialog):
        AccountEditDialog.setWindowTitle(QtGui.QApplication.translate("AccountEditDialog", "Счет", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDate.setText(QtGui.QApplication.translate("AccountEditDialog", "&Дата", None, QtGui.QApplication.UnicodeUTF8))
        self.lblNumber.setText(QtGui.QApplication.translate("AccountEditDialog", "&Номер", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AccountEditDialog", "Дата &выставления", None, QtGui.QApplication.UnicodeUTF8))

from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    AccountEditDialog = QtGui.QDialog()
    ui = Ui_AccountEditDialog()
    ui.setupUi(AccountEditDialog)
    AccountEditDialog.show()
    sys.exit(app.exec_())

