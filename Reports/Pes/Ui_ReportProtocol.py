# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportProtocol.ui'
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(268, 139)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(Dialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(Dialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.lblEndDate = QtGui.QLabel(Dialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 0, 3, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(Dialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 0, 4, 1, 1)
        self.lblProtocolNum = QtGui.QLabel(Dialog)
        self.lblProtocolNum.setObjectName(_fromUtf8("lblProtocolNum"))
        self.gridLayout.addWidget(self.lblProtocolNum, 1, 0, 1, 2)
        self.cmbProtocolNumber = QtGui.QComboBox(Dialog)
        self.cmbProtocolNumber.setObjectName(_fromUtf8("cmbProtocolNumber"))
        self.gridLayout.addWidget(self.cmbProtocolNumber, 1, 2, 1, 3)
        self.chkOnlyClose = QtGui.QCheckBox(Dialog)
        self.chkOnlyClose.setObjectName(_fromUtf8("chkOnlyClose"))
        self.gridLayout.addWidget(self.chkOnlyClose, 2, 0, 1, 3)
        self.chkGroupByClients = QtGui.QCheckBox(Dialog)
        self.chkGroupByClients.setObjectName(_fromUtf8("chkGroupByClients"))
        self.gridLayout.addWidget(self.chkGroupByClients, 3, 0, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 4)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.lblBegDate.setText(_translate("Dialog", "С:", None))
        self.lblEndDate.setText(_translate("Dialog", "По:", None))
        self.lblProtocolNum.setText(_translate("Dialog", "Номер протокола:", None))
        self.chkOnlyClose.setText(_translate("Dialog", "Только закрытые", None))
        self.chkGroupByClients.setText(_translate("Dialog", "Группировать по пациенам", None))

