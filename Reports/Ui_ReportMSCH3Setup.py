# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportMSCH3Setup.ui'
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

class Ui_ReportMSCH3SetupDialog(object):
    def setupUi(self, ReportMSCH3SetupDialog):
        ReportMSCH3SetupDialog.setObjectName(_fromUtf8("ReportMSCH3SetupDialog"))
        ReportMSCH3SetupDialog.resize(721, 487)
        self.gridLayout = QtGui.QGridLayout(ReportMSCH3SetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportMSCH3SetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.edtBegDate = CDateEdit(ReportMSCH3SetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 2)
        self.edtEndDate = CDateEdit(ReportMSCH3SetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 2, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportMSCH3SetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportMSCH3SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 4)
        self.lstEventTypes = CRBListBox(ReportMSCH3SetupDialog)
        self.lstEventTypes.setObjectName(_fromUtf8("lstEventTypes"))
        self.gridLayout.addWidget(self.lstEventTypes, 3, 2, 1, 2)
        self.lblEventType = QtGui.QLabel(ReportMSCH3SetupDialog)
        self.lblEventType.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 3, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 5, 2, 1, 1)
        self.chkIsWorker = QtGui.QCheckBox(ReportMSCH3SetupDialog)
        self.chkIsWorker.setObjectName(_fromUtf8("chkIsWorker"))
        self.gridLayout.addWidget(self.chkIsWorker, 4, 0, 1, 4)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblEventType.setBuddy(self.lstEventTypes)

        self.retranslateUi(ReportMSCH3SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportMSCH3SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportMSCH3SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportMSCH3SetupDialog)

    def retranslateUi(self, ReportMSCH3SetupDialog):
        ReportMSCH3SetupDialog.setWindowTitle(_translate("ReportMSCH3SetupDialog", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportMSCH3SetupDialog", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportMSCH3SetupDialog", "Дата &окончания периода", None))
        self.lblEventType.setText(_translate("ReportMSCH3SetupDialog", "&Тип обращения", None))
        self.chkIsWorker.setText(_translate("ReportMSCH3SetupDialog", "Сотрудник БЗС", None))

from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
