# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportMovingRVCSetupDialog.ui'
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

class Ui_ReportMovingRVCSetupDialog(object):
    def setupUi(self, ReportMovingRVCSetupDialog):
        ReportMovingRVCSetupDialog.setObjectName(_fromUtf8("ReportMovingRVCSetupDialog"))
        ReportMovingRVCSetupDialog.resize(400, 250)
        self.gridLayout = QtGui.QGridLayout(ReportMovingRVCSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(ReportMovingRVCSetupDialog)
        self.lblEndDate.setText(_fromUtf8(""))
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 3)
        self.edtDate = CDateEdit(ReportMovingRVCSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDate.sizePolicy().hasHeightForWidth())
        self.edtDate.setSizePolicy(sizePolicy)
        self.edtDate.setCalendarPopup(True)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 0, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 4, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportMovingRVCSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportMovingRVCSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 4, 1, 1)
        self.lblBegDate.setBuddy(self.edtDate)

        self.retranslateUi(ReportMovingRVCSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportMovingRVCSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportMovingRVCSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportMovingRVCSetupDialog)

    def retranslateUi(self, ReportMovingRVCSetupDialog):
        ReportMovingRVCSetupDialog.setWindowTitle(_translate("ReportMovingRVCSetupDialog", "Dialog", None))
        self.edtDate.setDisplayFormat(_translate("ReportMovingRVCSetupDialog", "dd.MM.yyyy", None))
        self.lblBegDate.setText(_translate("ReportMovingRVCSetupDialog", "Текущий &день", None))

from library.DateEdit import CDateEdit
