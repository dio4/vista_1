# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportLocationCard.ui'
#
# Created: Mon Oct 27 13:06:37 2014
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

class Ui_ReportLocationCard(object):
    def setupUi(self, ReportLocationCard):
        ReportLocationCard.setObjectName(_fromUtf8("ReportLocationCard"))
        ReportLocationCard.resize(400, 119)
        self.gridLayout = QtGui.QGridLayout(ReportLocationCard)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportLocationCard)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportLocationCard)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(137, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportLocationCard)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportLocationCard)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(137, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.lblLocationCardType = QtGui.QLabel(ReportLocationCard)
        self.lblLocationCardType.setObjectName(_fromUtf8("lblLocationCardType"))
        self.gridLayout.addWidget(self.lblLocationCardType, 2, 0, 1, 1)
        self.cmbLocationCardType = CRBComboBox(ReportLocationCard)
        self.cmbLocationCardType.setObjectName(_fromUtf8("cmbLocationCardType"))
        self.cmbLocationCardType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbLocationCardType, 2, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportLocationCard)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportLocationCard)
        self.cmbLocationCardType.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportLocationCard.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportLocationCard.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportLocationCard)

    def retranslateUi(self, ReportLocationCard):
        ReportLocationCard.setWindowTitle(_translate("ReportLocationCard", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportLocationCard", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportLocationCard", "Дата &окончания периода", None))
        self.lblLocationCardType.setText(_translate("ReportLocationCard", "Место нахождния рег.карты", None))
        self.cmbLocationCardType.setItemText(0, _translate("ReportLocationCard", "Новый элемент", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
