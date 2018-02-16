# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StationaryF30Setup.ui'
#
# Created: Tue Apr 30 15:40:06 2013
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_StationaryF30SetupDialog(object):
    def setupUi(self, StationaryF30SetupDialog):
        StationaryF30SetupDialog.setObjectName(_fromUtf8("StationaryF30SetupDialog"))
        StationaryF30SetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        StationaryF30SetupDialog.resize(438, 127)
        StationaryF30SetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(StationaryF30SetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbOrgStructure = COrgStructureComboBox(StationaryF30SetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 1, 1, 3)
        self.lblOrgStructure = QtGui.QLabel(StationaryF30SetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 3, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 2)
        self.edtEndDate = CDateEdit(StationaryF30SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(StationaryF30SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 4)
        self.lblEndDate = QtGui.QLabel(StationaryF30SetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 2)
        self.cmbProfileBed = CRBComboBox(StationaryF30SetupDialog)
        self.cmbProfileBed.setObjectName(_fromUtf8("cmbProfileBed"))
        self.gridLayout.addWidget(self.cmbProfileBed, 2, 1, 1, 3)
        self.lblProfilBed = QtGui.QLabel(StationaryF30SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblProfilBed.sizePolicy().hasHeightForWidth())
        self.lblProfilBed.setSizePolicy(sizePolicy)
        self.lblProfilBed.setObjectName(_fromUtf8("lblProfilBed"))
        self.gridLayout.addWidget(self.lblProfilBed, 2, 0, 1, 1)
        self.edtBegDate = CDateEdit(StationaryF30SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(StationaryF30SetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(StationaryF30SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StationaryF30SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StationaryF30SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StationaryF30SetupDialog)
        StationaryF30SetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        StationaryF30SetupDialog.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        StationaryF30SetupDialog.setTabOrder(self.cmbOrgStructure, self.buttonBox)

    def retranslateUi(self, StationaryF30SetupDialog):
        StationaryF30SetupDialog.setWindowTitle(_translate("StationaryF30SetupDialog", "параметры отчёта", None))
        self.lblOrgStructure.setText(_translate("StationaryF30SetupDialog", "&Подразделение", None))
        self.edtEndDate.setDisplayFormat(_translate("StationaryF30SetupDialog", "dd.MM.yyyy", None))
        self.lblEndDate.setText(_translate("StationaryF30SetupDialog", "Дата &окончания периода", None))
        self.lblProfilBed.setText(_translate("StationaryF30SetupDialog", "Профиль койки", None))
        self.edtBegDate.setDisplayFormat(_translate("StationaryF30SetupDialog", "dd.MM.yyyy", None))
        self.lblBegDate.setText(_translate("StationaryF30SetupDialog", "Дата &начала периода", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
