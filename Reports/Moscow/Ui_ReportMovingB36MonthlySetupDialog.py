# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportMovingB36MonthlySetupDialog.ui'
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

class Ui_ReportMovingB36MonthlySetupDialog(object):
    def setupUi(self, ReportMovingB36MonthlySetupDialog):
        ReportMovingB36MonthlySetupDialog.setObjectName(_fromUtf8("ReportMovingB36MonthlySetupDialog"))
        ReportMovingB36MonthlySetupDialog.resize(400, 250)
        self.gridLayout = QtGui.QGridLayout(ReportMovingB36MonthlySetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportMovingB36MonthlySetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportMovingB36MonthlySetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblBegTime = QtGui.QLabel(ReportMovingB36MonthlySetupDialog)
        self.lblBegTime.setObjectName(_fromUtf8("lblBegTime"))
        self.gridLayout.addWidget(self.lblBegTime, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 103, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportMovingB36MonthlySetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportMovingB36MonthlySetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtBegTime = QtGui.QTimeEdit(ReportMovingB36MonthlySetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegTime.sizePolicy().hasHeightForWidth())
        self.edtBegTime.setSizePolicy(sizePolicy)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout.addWidget(self.edtBegTime, 2, 1, 1, 1)
        self.edtBegDate = CDateEdit(ReportMovingB36MonthlySetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 2, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblBegTime.setBuddy(self.edtBegTime)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportMovingB36MonthlySetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportMovingB36MonthlySetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportMovingB36MonthlySetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportMovingB36MonthlySetupDialog)
        ReportMovingB36MonthlySetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportMovingB36MonthlySetupDialog.setTabOrder(self.edtEndDate, self.edtBegTime)
        ReportMovingB36MonthlySetupDialog.setTabOrder(self.edtBegTime, self.buttonBox)

    def retranslateUi(self, ReportMovingB36MonthlySetupDialog):
        ReportMovingB36MonthlySetupDialog.setWindowTitle(_translate("ReportMovingB36MonthlySetupDialog", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportMovingB36MonthlySetupDialog", "Дата &начала периода", None))
        self.lblBegTime.setText(_translate("ReportMovingB36MonthlySetupDialog", "Время &смены суток", None))
        self.lblEndDate.setText(_translate("ReportMovingB36MonthlySetupDialog", "Дата &окончания периода", None))

from library.DateEdit import CDateEdit
