# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportClientInfoSourceSetup.ui'
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

class Ui_ReportClientInfoSourceSetup(object):
    def setupUi(self, ReportClientInfoSourceSetup):
        ReportClientInfoSourceSetup.setObjectName(_fromUtf8("ReportClientInfoSourceSetup"))
        ReportClientInfoSourceSetup.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportClientInfoSourceSetup.resize(438, 248)
        ReportClientInfoSourceSetup.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportClientInfoSourceSetup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lstSource = CRBListBox(ReportClientInfoSourceSetup)
        self.lstSource.setObjectName(_fromUtf8("lstSource"))
        self.gridLayout.addWidget(self.lstSource, 2, 3, 2, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.chkManyEvents = QtGui.QCheckBox(ReportClientInfoSourceSetup)
        self.chkManyEvents.setObjectName(_fromUtf8("chkManyEvents"))
        self.gridLayout.addWidget(self.chkManyEvents, 4, 1, 1, 4)
        self.lblOrgStructure = QtGui.QLabel(ReportClientInfoSourceSetup)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportClientInfoSourceSetup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportClientInfoSourceSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 4)
        self.lblBegDate = QtGui.QLabel(ReportClientInfoSourceSetup)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 1, 1, 1)
        self.edtBegDate = CDateEdit(ReportClientInfoSourceSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 3, 1, 1)
        self.edtEndDate = CDateEdit(ReportClientInfoSourceSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 4, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 2, 2, 2, 1)
        spacerItem3 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 1, 4, 1, 1)
        self.lblOrgStructure.setBuddy(self.lstSource)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportClientInfoSourceSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportClientInfoSourceSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportClientInfoSourceSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportClientInfoSourceSetup)
        ReportClientInfoSourceSetup.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportClientInfoSourceSetup.setTabOrder(self.edtEndDate, self.lstSource)
        ReportClientInfoSourceSetup.setTabOrder(self.lstSource, self.buttonBox)

    def retranslateUi(self, ReportClientInfoSourceSetup):
        ReportClientInfoSourceSetup.setWindowTitle(_translate("ReportClientInfoSourceSetup", "параметры отчёта", None))
        self.chkManyEvents.setText(_translate("ReportClientInfoSourceSetup", "Подсчет по всем событиям", None))
        self.lblOrgStructure.setText(_translate("ReportClientInfoSourceSetup", "Откуда узнали", None))
        self.lblEndDate.setText(_translate("ReportClientInfoSourceSetup", "Дата &окончания периода", None))
        self.lblBegDate.setText(_translate("ReportClientInfoSourceSetup", "Дата &начала периода", None))
        self.edtBegDate.setDisplayFormat(_translate("ReportClientInfoSourceSetup", "dd.MM.yyyy", None))
        self.edtEndDate.setDisplayFormat(_translate("ReportClientInfoSourceSetup", "dd.MM.yyyy", None))

from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
