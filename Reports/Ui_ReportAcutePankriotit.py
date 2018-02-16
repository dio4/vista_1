# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportAcutePankriotit.ui'
#
# Created: Fri Apr 11 01:01:35 2014
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

class Ui_ReportAcutePankriotit(object):
    def setupUi(self, ReportAcutePankriotit):
        ReportAcutePankriotit.setObjectName(_fromUtf8("ReportAcutePankriotit"))
        ReportAcutePankriotit.resize(334, 102)
        self.gridLayout = QtGui.QGridLayout(ReportAcutePankriotit)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtEndDate = CDateEdit(ReportAcutePankriotit)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportAcutePankriotit)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportAcutePankriotit)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAcutePankriotit)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 4)
        self.edtBegDate = CDateEdit(ReportAcutePankriotit)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportAcutePankriotit)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAcutePankriotit.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAcutePankriotit.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAcutePankriotit)

    def retranslateUi(self, ReportAcutePankriotit):
        ReportAcutePankriotit.setWindowTitle(_translate("ReportAcutePankriotit", "Dialog", None))
        self.lblEndDate.setText(_translate("ReportAcutePankriotit", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportAcutePankriotit", "Дата &начала периода", None))

from library.DateEdit import CDateEdit
