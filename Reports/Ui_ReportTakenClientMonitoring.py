# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportTakenClientMonitoring.ui'
#
# Created: Wed Jul 09 19:51:43 2014
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

class Ui_ReportTakenClientMonitoring(object):
    def setupUi(self, ReportTakenClientMonitoring):
        ReportTakenClientMonitoring.setObjectName(_fromUtf8("ReportTakenClientMonitoring"))
        ReportTakenClientMonitoring.resize(398, 93)
        self.gridLayout = QtGui.QGridLayout(ReportTakenClientMonitoring)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(ReportTakenClientMonitoring)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportTakenClientMonitoring)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportTakenClientMonitoring)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportTakenClientMonitoring)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportTakenClientMonitoring)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 2, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportTakenClientMonitoring)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportTakenClientMonitoring.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportTakenClientMonitoring.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportTakenClientMonitoring)

    def retranslateUi(self, ReportTakenClientMonitoring):
        ReportTakenClientMonitoring.setWindowTitle(_translate("ReportTakenClientMonitoring", "Dialog", None))
        self.lblEndDate.setText(_translate("ReportTakenClientMonitoring", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportTakenClientMonitoring", "Дата &начала периода", None))

from library.DateEdit import CDateEdit
