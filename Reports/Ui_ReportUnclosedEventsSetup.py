# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportUnclosedEventsSetup.ui'
#
# Created: Mon Oct 26 14:22:57 2015
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

class Ui_ReportUnclosedEventsSetupDialog(object):
    def setupUi(self, ReportUnclosedEventsSetupDialog):
        ReportUnclosedEventsSetupDialog.setObjectName(_fromUtf8("ReportUnclosedEventsSetupDialog"))
        ReportUnclosedEventsSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportUnclosedEventsSetupDialog.resize(397, 135)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportUnclosedEventsSetupDialog.sizePolicy().hasHeightForWidth())
        ReportUnclosedEventsSetupDialog.setSizePolicy(sizePolicy)
        ReportUnclosedEventsSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportUnclosedEventsSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportUnclosedEventsSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportUnclosedEventsSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportUnclosedEventsSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportUnclosedEventsSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportUnclosedEventsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 2)
        self.cmbEventType = CRBComboBox(ReportUnclosedEventsSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 3, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportUnclosedEventsSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 3, 0, 1, 1)
        self.lblEventType.setBuddy(self.cmbEventType)

        self.retranslateUi(ReportUnclosedEventsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportUnclosedEventsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportUnclosedEventsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportUnclosedEventsSetupDialog)

    def retranslateUi(self, ReportUnclosedEventsSetupDialog):
        ReportUnclosedEventsSetupDialog.setWindowTitle(_translate("ReportUnclosedEventsSetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportUnclosedEventsSetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportUnclosedEventsSetupDialog", "Дата окончания периода", None))
        self.lblEventType.setText(_translate("ReportUnclosedEventsSetupDialog", "&Тип обращения", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
