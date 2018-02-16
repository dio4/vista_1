# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StationaryF14Setup.ui'
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

class Ui_StationaryF14SetupDialog(object):
    def setupUi(self, StationaryF14SetupDialog):
        StationaryF14SetupDialog.setObjectName(_fromUtf8("StationaryF14SetupDialog"))
        StationaryF14SetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        StationaryF14SetupDialog.resize(450, 350)
        StationaryF14SetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(StationaryF14SetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(StationaryF14SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 4)
        self.lblOrgStructure = QtGui.QLabel(StationaryF14SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOrgStructure.sizePolicy().hasHeightForWidth())
        self.lblOrgStructure.setSizePolicy(sizePolicy)
        self.lblOrgStructure.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 6, 0, 1, 1)
        self.lblOrder = QtGui.QLabel(StationaryF14SetupDialog)
        self.lblOrder.setObjectName(_fromUtf8("lblOrder"))
        self.gridLayout.addWidget(self.lblOrder, 4, 0, 1, 1)
        self.edtEndDate = CDateEdit(StationaryF14SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.cmbOrder = QtGui.QComboBox(StationaryF14SetupDialog)
        self.cmbOrder.setObjectName(_fromUtf8("cmbOrder"))
        self.gridLayout.addWidget(self.cmbOrder, 4, 1, 1, 3)
        self.lblBegDate = QtGui.QLabel(StationaryF14SetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(StationaryF14SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 2)
        self.lblEndDate = QtGui.QLabel(StationaryF14SetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 8, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 2, 1, 2)
        self.lstOrgStructure = CRBListBox(StationaryF14SetupDialog)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridLayout.addWidget(self.lstOrgStructure, 6, 1, 1, 3)
        self.label = QtGui.QLabel(StationaryF14SetupDialog)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 5, 0, 1, 1)
        self.lstEventType = CRBListBox(StationaryF14SetupDialog)
        self.lstEventType.setObjectName(_fromUtf8("lstEventType"))
        self.gridLayout.addWidget(self.lstEventType, 5, 1, 1, 3)
        self.lblOrgStructure.setBuddy(self.lstOrgStructure)
        self.lblOrder.setBuddy(self.cmbOrder)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.label.setBuddy(self.lstEventType)

        self.retranslateUi(StationaryF14SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StationaryF14SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StationaryF14SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StationaryF14SetupDialog)
        StationaryF14SetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        StationaryF14SetupDialog.setTabOrder(self.edtEndDate, self.cmbOrder)
        StationaryF14SetupDialog.setTabOrder(self.cmbOrder, self.lstEventType)
        StationaryF14SetupDialog.setTabOrder(self.lstEventType, self.lstOrgStructure)
        StationaryF14SetupDialog.setTabOrder(self.lstOrgStructure, self.buttonBox)

    def retranslateUi(self, StationaryF14SetupDialog):
        StationaryF14SetupDialog.setWindowTitle(_translate("StationaryF14SetupDialog", "параметры отчёта", None))
        self.lblOrgStructure.setText(_translate("StationaryF14SetupDialog", "&Подразделение", None))
        self.lblOrder.setText(_translate("StationaryF14SetupDialog", "Порядок", None))
        self.edtEndDate.setDisplayFormat(_translate("StationaryF14SetupDialog", "dd.MM.yyyy", None))
        self.lblBegDate.setText(_translate("StationaryF14SetupDialog", "Дата &начала периода", None))
        self.edtBegDate.setDisplayFormat(_translate("StationaryF14SetupDialog", "dd.MM.yyyy", None))
        self.lblEndDate.setText(_translate("StationaryF14SetupDialog", "Дата &окончания периода", None))
        self.label.setText(_translate("StationaryF14SetupDialog", "Тип обращения", None))

from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
