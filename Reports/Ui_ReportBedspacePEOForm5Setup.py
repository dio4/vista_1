# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportBedspacePEOForm5Setup.ui'
#
# Created: Thu Jul 16 14:25:07 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_ReportBedspacePEOForm5Setup(object):
    def setupUi(self, ReportBedspacePEOForm5Setup):
        ReportBedspacePEOForm5Setup.setObjectName(_fromUtf8("ReportBedspacePEOForm5Setup"))
        ReportBedspacePEOForm5Setup.resize(398, 125)
        self.gridLayout = QtGui.QGridLayout(ReportBedspacePEOForm5Setup)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(ReportBedspacePEOForm5Setup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportBedspacePEOForm5Setup)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportBedspacePEOForm5Setup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)
        self.lblFinance = QtGui.QLabel(ReportBedspacePEOForm5Setup)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 3, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportBedspacePEOForm5Setup)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 3, 1, 1, 2)
        self.edtEndDate = CDateEdit(ReportBedspacePEOForm5Setup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 1, 1, 1)
        self.edtBegDate = CDateEdit(ReportBedspacePEOForm5Setup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportBedspacePEOForm5Setup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportBedspacePEOForm5Setup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportBedspacePEOForm5Setup.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportBedspacePEOForm5Setup)

    def retranslateUi(self, ReportBedspacePEOForm5Setup):
        ReportBedspacePEOForm5Setup.setWindowTitle(_translate("ReportBedspacePEOForm5Setup", "Dialog", None))
        self.lblEndDate.setText(_translate("ReportBedspacePEOForm5Setup", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportBedspacePEOForm5Setup", "Дата &начала периода", None))
        self.lblFinance.setText(_translate("ReportBedspacePEOForm5Setup", "Тип финансирования", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
