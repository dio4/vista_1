# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportLeavedClients.ui'
#
# Created: Wed Apr 02 21:06:32 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_ReportLeavedClients(object):
    def setupUi(self, ReportLeavedClients):
        ReportLeavedClients.setObjectName(_fromUtf8("ReportLeavedClients"))
        ReportLeavedClients.resize(319, 138)
        self.gridLayout = QtGui.QGridLayout(ReportLeavedClients)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ReportLeavedClients)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(ReportLeavedClients)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 1, 1, 1)
        self.label = QtGui.QLabel(ReportLeavedClients)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportLeavedClients)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ReportLeavedClients)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.retranslateUi(ReportLeavedClients)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportLeavedClients.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportLeavedClients.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportLeavedClients)

    def retranslateUi(self, ReportLeavedClients):
        ReportLeavedClients.setWindowTitle(_translate("ReportLeavedClients", "Dialog", None))
        self.label.setText(_translate("ReportLeavedClients", "Дата начала периода", None))
        self.label_2.setText(_translate("ReportLeavedClients", "Дата окончания периода", None))

