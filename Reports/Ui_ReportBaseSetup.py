# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportBaseSetup.ui'
#
# Created: Tue Sep 30 18:44:13 2014
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

class Ui_ReportBaseSetup(object):
    def setupUi(self, ReportBaseSetup):
        ReportBaseSetup.setObjectName(_fromUtf8("ReportBaseSetup"))
        ReportBaseSetup.resize(400, 93)
        self.gridLayout = QtGui.QGridLayout(ReportBaseSetup)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(ReportBaseSetup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportBaseSetup)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportBaseSetup)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.edtEndDate = CDateEdit(ReportBaseSetup)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportBaseSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 2, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportBaseSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportBaseSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportBaseSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportBaseSetup)

    def retranslateUi(self, ReportBaseSetup):
        ReportBaseSetup.setWindowTitle(_translate("ReportBaseSetup", "Dialog", None))
        self.lblEndDate.setText(_translate("ReportBaseSetup", "Дата окончания периода", None))
        self.lblBegDate.setText(_translate("ReportBaseSetup", "Дата начала периода", None))

from library.DateEdit import CDateEdit
