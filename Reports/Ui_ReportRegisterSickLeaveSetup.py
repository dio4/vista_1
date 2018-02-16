# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportRegisterSickLeaveSetup.ui'
#
# Created: Wed Oct 14 20:41:48 2015
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

class Ui_ReportRegisterSickLeaveSetupDialog(object):
    def setupUi(self, ReportRegisterSickLeaveSetupDialog):
        ReportRegisterSickLeaveSetupDialog.setObjectName(_fromUtf8("ReportRegisterSickLeaveSetupDialog"))
        ReportRegisterSickLeaveSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportRegisterSickLeaveSetupDialog.resize(340, 139)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportRegisterSickLeaveSetupDialog.sizePolicy().hasHeightForWidth())
        ReportRegisterSickLeaveSetupDialog.setSizePolicy(sizePolicy)
        ReportRegisterSickLeaveSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportRegisterSickLeaveSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportRegisterSickLeaveSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportRegisterSickLeaveSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportRegisterSickLeaveSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportRegisterSickLeaveSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportRegisterSickLeaveSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.chkShort = QtGui.QCheckBox(ReportRegisterSickLeaveSetupDialog)
        self.chkShort.setObjectName(_fromUtf8("chkShort"))
        self.gridLayout.addWidget(self.chkShort, 2, 0, 1, 1)
        self.chkWithoutExternal = QtGui.QCheckBox(ReportRegisterSickLeaveSetupDialog)
        self.chkWithoutExternal.setObjectName(_fromUtf8("chkWithoutExternal"))
        self.gridLayout.addWidget(self.chkWithoutExternal, 3, 0, 1, 1)

        self.retranslateUi(ReportRegisterSickLeaveSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportRegisterSickLeaveSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportRegisterSickLeaveSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportRegisterSickLeaveSetupDialog)

    def retranslateUi(self, ReportRegisterSickLeaveSetupDialog):
        ReportRegisterSickLeaveSetupDialog.setWindowTitle(_translate("ReportRegisterSickLeaveSetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportRegisterSickLeaveSetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportRegisterSickLeaveSetupDialog", "Дата окончания периода", None))
        self.chkShort.setText(_translate("ReportRegisterSickLeaveSetupDialog", "Сокращенная форма", None))
        self.chkWithoutExternal.setText(_translate("ReportRegisterSickLeaveSetupDialog", "Без внешних", None))

from library.DateEdit import CDateEdit
