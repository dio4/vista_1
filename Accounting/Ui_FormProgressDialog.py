# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Accounting\FormProgressDialog.ui'
#
# Created: Fri Jun 15 12:15:00 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FormProgressDialog(object):
    def setupUi(self, FormProgressDialog):
        FormProgressDialog.setObjectName(_fromUtf8("FormProgressDialog"))
        FormProgressDialog.resize(649, 142)
        self.gridlayout = QtGui.QGridLayout(FormProgressDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblByContracts = QtGui.QLabel(FormProgressDialog)
        self.lblByContracts.setObjectName(_fromUtf8("lblByContracts"))
        self.gridlayout.addWidget(self.lblByContracts, 0, 0, 1, 1)
        self.prbContracts = QtGui.QProgressBar(FormProgressDialog)
        self.prbContracts.setProperty("value", 24)
        self.prbContracts.setObjectName(_fromUtf8("prbContracts"))
        self.gridlayout.addWidget(self.prbContracts, 1, 0, 1, 3)
        self.lblByContract = QtGui.QLabel(FormProgressDialog)
        self.lblByContract.setObjectName(_fromUtf8("lblByContract"))
        self.gridlayout.addWidget(self.lblByContract, 2, 0, 1, 1)
        self.lblContract = QtGui.QLabel(FormProgressDialog)
        self.lblContract.setObjectName(_fromUtf8("lblContract"))
        self.gridlayout.addWidget(self.lblContract, 2, 1, 1, 2)
        self.prbContract = QtGui.QProgressBar(FormProgressDialog)
        self.prbContract.setProperty("value", 24)
        self.prbContract.setObjectName(_fromUtf8("prbContract"))
        self.gridlayout.addWidget(self.prbContract, 3, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(20, 141, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 4, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(291, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 5, 0, 1, 2)
        self.btnBreak = QtGui.QPushButton(FormProgressDialog)
        self.btnBreak.setObjectName(_fromUtf8("btnBreak"))
        self.gridlayout.addWidget(self.btnBreak, 5, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 0, 1, 1, 2)

        self.retranslateUi(FormProgressDialog)
        QtCore.QMetaObject.connectSlotsByName(FormProgressDialog)

    def retranslateUi(self, FormProgressDialog):
        FormProgressDialog.setWindowTitle(QtGui.QApplication.translate("FormProgressDialog", "Идёт формирование счёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblByContracts.setText(QtGui.QApplication.translate("FormProgressDialog", "Договор", None, QtGui.QApplication.UnicodeUTF8))
        self.prbContracts.setFormat(QtGui.QApplication.translate("FormProgressDialog", "%v", "2223", QtGui.QApplication.UnicodeUTF8))
        self.lblByContract.setText(QtGui.QApplication.translate("FormProgressDialog", "По договору", None, QtGui.QApplication.UnicodeUTF8))
        self.lblContract.setText(QtGui.QApplication.translate("FormProgressDialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.prbContract.setFormat(QtGui.QApplication.translate("FormProgressDialog", "%v", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBreak.setText(QtGui.QApplication.translate("FormProgressDialog", "Прервать", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    FormProgressDialog = QtGui.QDialog()
    ui = Ui_FormProgressDialog()
    ui.setupUi(FormProgressDialog)
    FormProgressDialog.show()
    sys.exit(app.exec_())

