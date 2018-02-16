# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportInfoSourceSetup.ui'
#
# Created: Mon Jan 19 19:18:15 2015
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

class Ui_ReportInfoSourceSetupDialog(object):
    def setupUi(self, ReportInfoSourceSetupDialog):
        ReportInfoSourceSetupDialog.setObjectName(_fromUtf8("ReportInfoSourceSetupDialog"))
        ReportInfoSourceSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportInfoSourceSetupDialog.resize(396, 162)
        ReportInfoSourceSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportInfoSourceSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportInfoSourceSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 4)
        self.chkGrouping = QtGui.QCheckBox(ReportInfoSourceSetupDialog)
        self.chkGrouping.setChecked(True)
        self.chkGrouping.setObjectName(_fromUtf8("chkGrouping"))
        self.gridLayout.addWidget(self.chkGrouping, 2, 0, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportInfoSourceSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(ReportInfoSourceSetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(ReportInfoSourceSetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportInfoSourceSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportInfoSourceSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportInfoSourceSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportInfoSourceSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportInfoSourceSetupDialog)

    def retranslateUi(self, ReportInfoSourceSetupDialog):
        ReportInfoSourceSetupDialog.setWindowTitle(_translate("ReportInfoSourceSetupDialog", "параметры отчёта", None))
        self.chkGrouping.setText(_translate("ReportInfoSourceSetupDialog", "Группировка пациентов по источникам информации", None))
        self.lblBegDate.setText(_translate("ReportInfoSourceSetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportInfoSourceSetupDialog", "Дата окончания периода", None))

