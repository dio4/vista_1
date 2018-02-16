# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'InstantAccountDialog.ui'
#
# Created: Thu Aug 22 16:29:14 2013
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

class Ui_InstantAccountDialog(object):
    def setupUi(self, InstantAccountDialog):
        InstantAccountDialog.setObjectName(_fromUtf8("InstantAccountDialog"))
        InstantAccountDialog.resize(717, 386)
        self.verticalLayout = QtGui.QVBoxLayout(InstantAccountDialog)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = QtGui.QWidget(InstantAccountDialog)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(self.widget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tblAccounts = CTableView(self.splitter)
        self.tblAccounts.setObjectName(_fromUtf8("tblAccounts"))
        self.tblAccountItems = CTableView(self.splitter)
        self.tblAccountItems.setObjectName(_fromUtf8("tblAccountItems"))
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.widget)
        self.groupAccount = QtGui.QGroupBox(InstantAccountDialog)
        self.groupAccount.setObjectName(_fromUtf8("groupAccount"))
        self.hboxlayout = QtGui.QHBoxLayout(self.groupAccount)
        self.hboxlayout.setSpacing(4)
        self.hboxlayout.setMargin(4)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.lblAccountItemsCount = QtGui.QLabel(self.groupAccount)
        self.lblAccountItemsCount.setObjectName(_fromUtf8("lblAccountItemsCount"))
        self.hboxlayout.addWidget(self.lblAccountItemsCount)
        self.edtAccountItemsCount = QtGui.QLineEdit(self.groupAccount)
        self.edtAccountItemsCount.setAlignment(QtCore.Qt.AlignRight)
        self.edtAccountItemsCount.setReadOnly(True)
        self.edtAccountItemsCount.setObjectName(_fromUtf8("edtAccountItemsCount"))
        self.hboxlayout.addWidget(self.edtAccountItemsCount)
        self.lblAccountSum = QtGui.QLabel(self.groupAccount)
        self.lblAccountSum.setObjectName(_fromUtf8("lblAccountSum"))
        self.hboxlayout.addWidget(self.lblAccountSum)
        self.edtAccountItemsSum = QtGui.QLineEdit(self.groupAccount)
        self.edtAccountItemsSum.setAlignment(QtCore.Qt.AlignRight)
        self.edtAccountItemsSum.setReadOnly(True)
        self.edtAccountItemsSum.setObjectName(_fromUtf8("edtAccountItemsSum"))
        self.hboxlayout.addWidget(self.edtAccountItemsSum)
        self.lblAccountPayed = QtGui.QLabel(self.groupAccount)
        self.lblAccountPayed.setObjectName(_fromUtf8("lblAccountPayed"))
        self.hboxlayout.addWidget(self.lblAccountPayed)
        self.edtAccountItemsPayed = QtGui.QLineEdit(self.groupAccount)
        self.edtAccountItemsPayed.setAlignment(QtCore.Qt.AlignRight)
        self.edtAccountItemsPayed.setReadOnly(True)
        self.edtAccountItemsPayed.setObjectName(_fromUtf8("edtAccountItemsPayed"))
        self.hboxlayout.addWidget(self.edtAccountItemsPayed)
        self.lblAccountRejected = QtGui.QLabel(self.groupAccount)
        self.lblAccountRejected.setObjectName(_fromUtf8("lblAccountRejected"))
        self.hboxlayout.addWidget(self.lblAccountRejected)
        self.edtAccountItemsRefused = QtGui.QLineEdit(self.groupAccount)
        self.edtAccountItemsRefused.setAlignment(QtCore.Qt.AlignRight)
        self.edtAccountItemsRefused.setReadOnly(True)
        self.edtAccountItemsRefused.setObjectName(_fromUtf8("edtAccountItemsRefused"))
        self.hboxlayout.addWidget(self.edtAccountItemsRefused)
        self.verticalLayout.addWidget(self.groupAccount)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnECashRegister = QtGui.QPushButton(InstantAccountDialog)
        self.btnECashRegister.setObjectName(_fromUtf8("btnECashRegister"))
        self.horizontalLayout.addWidget(self.btnECashRegister)
        self.buttonBox = QtGui.QDialogButtonBox(InstantAccountDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.lblAccountItemsCount.setBuddy(self.edtAccountItemsCount)
        self.lblAccountSum.setBuddy(self.edtAccountItemsSum)
        self.lblAccountPayed.setBuddy(self.edtAccountItemsPayed)
        self.lblAccountRejected.setBuddy(self.edtAccountItemsRefused)

        self.retranslateUi(InstantAccountDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), InstantAccountDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(InstantAccountDialog)
        InstantAccountDialog.setTabOrder(self.tblAccounts, self.tblAccountItems)
        InstantAccountDialog.setTabOrder(self.tblAccountItems, self.edtAccountItemsCount)
        InstantAccountDialog.setTabOrder(self.edtAccountItemsCount, self.edtAccountItemsSum)
        InstantAccountDialog.setTabOrder(self.edtAccountItemsSum, self.edtAccountItemsPayed)
        InstantAccountDialog.setTabOrder(self.edtAccountItemsPayed, self.edtAccountItemsRefused)

    def retranslateUi(self, InstantAccountDialog):
        InstantAccountDialog.setWindowTitle(_translate("InstantAccountDialog", "Счёт", None))
        self.groupAccount.setTitle(_translate("InstantAccountDialog", "Итого по счету", None))
        self.lblAccountItemsCount.setText(_translate("InstantAccountDialog", "Позиций", None))
        self.lblAccountSum.setText(_translate("InstantAccountDialog", "Выставлено", None))
        self.lblAccountPayed.setText(_translate("InstantAccountDialog", "Оплата", None))
        self.lblAccountRejected.setText(_translate("InstantAccountDialog", "Отказ", None))
        self.btnECashRegister.setText(_translate("InstantAccountDialog", "Касса", None))

from library.TableView import CTableView
