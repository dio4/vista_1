# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportResultClientListSetup.ui'
#
# Created: Tue Jan 21 15:52:27 2014
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

class Ui_ReportResultClientListSetup(object):
    def setupUi(self, ReportResultClientListSetup):
        ReportResultClientListSetup.setObjectName(_fromUtf8("ReportResultClientListSetup"))
        ReportResultClientListSetup.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportResultClientListSetup.resize(427, 156)
        ReportResultClientListSetup.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportResultClientListSetup)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportResultClientListSetup)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.edtBegDate = CDateEdit(ReportResultClientListSetup)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 3)
        self.lblEndDate = QtGui.QLabel(ReportResultClientListSetup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        self.edtEndDate = CDateEdit(ReportResultClientListSetup)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 3)
        spacerItem = QtGui.QSpacerItem(84, 22, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 5, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportResultClientListSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 3, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(84, 22, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 5, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 2, 2, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportResultClientListSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportResultClientListSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportResultClientListSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportResultClientListSetup)
        ReportResultClientListSetup.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportResultClientListSetup.setTabOrder(self.edtEndDate, self.buttonBox)

    def retranslateUi(self, ReportResultClientListSetup):
        ReportResultClientListSetup.setWindowTitle(_translate("ReportResultClientListSetup", "Параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportResultClientListSetup", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportResultClientListSetup", "Дата &окончания периода", None))

from library.DateEdit import CDateEdit
