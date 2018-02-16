# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Reports\ReportFromLogger.ui'
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

class Ui_ReportFromLogger(object):
    def setupUi(self, ReportFromLogger):
        ReportFromLogger.setObjectName(_fromUtf8("ReportFromLogger"))
        ReportFromLogger.resize(400, 122)
        self.gridLayout = QtGui.QGridLayout(ReportFromLogger)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportFromLogger)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportFromLogger)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 4)
        self.lblEndDate = QtGui.QLabel(ReportFromLogger)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        self.edtBegDate = CDateEdit(ReportFromLogger)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportFromLogger)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.chkPersonDetail = QtGui.QCheckBox(ReportFromLogger)
        self.chkPersonDetail.setObjectName(_fromUtf8("chkPersonDetail"))
        self.gridLayout.addWidget(self.chkPersonDetail, 3, 0, 1, 2)
        self.chkGroup = QtGui.QCheckBox(ReportFromLogger)
        self.chkGroup.setEnabled(False)
        self.chkGroup.setObjectName(_fromUtf8("chkGroup"))
        self.gridLayout.addWidget(self.chkGroup, 3, 2, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportFromLogger)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportFromLogger.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportFromLogger.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportFromLogger)

    def retranslateUi(self, ReportFromLogger):
        ReportFromLogger.setWindowTitle(_translate("ReportFromLogger", "Dialog", None))
        self.lblEndDate.setText(_translate("ReportFromLogger", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportFromLogger", "Дата &начала периода", None))
        self.chkPersonDetail.setText(_translate("ReportFromLogger", "Детализировать по пользователю", None))
        self.chkGroup.setText(_translate("ReportFromLogger", "Группировать отчеты", None))

from library.DateEdit import CDateEdit
