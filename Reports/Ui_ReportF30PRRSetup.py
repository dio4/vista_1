# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportF30PRRSetup.ui'
#
# Created: Wed Sep 11 19:52:47 2013
#      by: PyQt4 UI code generator 4.10
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

class Ui_ReportF30PRRSetupDialog(object):
    def setupUi(self, ReportF30PRRSetupDialog):
        ReportF30PRRSetupDialog.setObjectName(_fromUtf8("ReportF30PRRSetupDialog"))
        ReportF30PRRSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportF30PRRSetupDialog.resize(309, 162)
        ReportF30PRRSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportF30PRRSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 4, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportF30PRRSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 4)
        self.edtEndDate = QtGui.QDateEdit(ReportF30PRRSetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportF30PRRSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 4, 0, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportF30PRRSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 4, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportF30PRRSetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 2)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportF30PRRSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF30PRRSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF30PRRSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF30PRRSetupDialog)
        ReportF30PRRSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportF30PRRSetupDialog.setTabOrder(self.edtEndDate, self.buttonBox)

    def retranslateUi(self, ReportF30PRRSetupDialog):
        ReportF30PRRSetupDialog.setWindowTitle(_translate("ReportF30PRRSetupDialog", "параметры отчёта", None))
        self.lblEndDate.setText(_translate("ReportF30PRRSetupDialog", "Дата окончания периода", None))
        self.lblBegDate.setText(_translate("ReportF30PRRSetupDialog", "Дата начала периода", None))

