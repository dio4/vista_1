# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StationaryF007Setup.ui'
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

class Ui_StationaryF007SetupDialog(object):
    def setupUi(self, StationaryF007SetupDialog):
        StationaryF007SetupDialog.setObjectName(_fromUtf8("StationaryF007SetupDialog"))
        StationaryF007SetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        StationaryF007SetupDialog.resize(671, 448)
        StationaryF007SetupDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(StationaryF007SetupDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 2, 1, 1, 1)
        self.lblProfileBed = QtGui.QLabel(StationaryF007SetupDialog)
        self.lblProfileBed.setObjectName(_fromUtf8("lblProfileBed"))
        self.gridlayout.addWidget(self.lblProfileBed, 4, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(StationaryF007SetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridlayout.addWidget(self.lblEndDate, 0, 0, 1, 1)
        self.edtBegTime = QtGui.QTimeEdit(StationaryF007SetupDialog)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridlayout.addWidget(self.edtBegTime, 1, 2, 1, 1)
        self.edtEndDate = CDateEdit(StationaryF007SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridlayout.addWidget(self.edtEndDate, 0, 2, 1, 1)
        self.chkIsHideBeds = QtGui.QCheckBox(StationaryF007SetupDialog)
        self.chkIsHideBeds.setObjectName(_fromUtf8("chkIsHideBeds"))
        self.gridlayout.addWidget(self.chkIsHideBeds, 5, 0, 1, 4)
        self.cmbProfileBed = CRBComboBox(StationaryF007SetupDialog)
        self.cmbProfileBed.setObjectName(_fromUtf8("cmbProfileBed"))
        self.gridlayout.addWidget(self.cmbProfileBed, 4, 2, 1, 2)
        self.lstOrgStructure = CRBListBox(StationaryF007SetupDialog)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridlayout.addWidget(self.lstOrgStructure, 2, 2, 1, 2)
        self.chkDetailOrgStructure = QtGui.QCheckBox(StationaryF007SetupDialog)
        self.chkDetailOrgStructure.setObjectName(_fromUtf8("chkDetailOrgStructure"))
        self.gridlayout.addWidget(self.chkDetailOrgStructure, 6, 0, 1, 4)
        self.lblSchedule = QtGui.QLabel(StationaryF007SetupDialog)
        self.lblSchedule.setObjectName(_fromUtf8("lblSchedule"))
        self.gridlayout.addWidget(self.lblSchedule, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(StationaryF007SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 7, 0, 1, 4)
        self.lblOrgStructure = QtGui.QLabel(StationaryF007SetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridlayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.lblBegTime = QtGui.QLabel(StationaryF007SetupDialog)
        self.lblBegTime.setObjectName(_fromUtf8("lblBegTime"))
        self.gridlayout.addWidget(self.lblBegTime, 1, 0, 1, 1)
        self.cmbSchedule = QtGui.QComboBox(StationaryF007SetupDialog)
        self.cmbSchedule.setObjectName(_fromUtf8("cmbSchedule"))
        self.cmbSchedule.addItem(_fromUtf8(""))
        self.cmbSchedule.addItem(_fromUtf8(""))
        self.cmbSchedule.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbSchedule, 3, 2, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 0, 3, 1, 1)
        self.lblProfileBed.setBuddy(self.cmbProfileBed)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblSchedule.setBuddy(self.cmbSchedule)
        self.lblBegTime.setBuddy(self.edtBegTime)

        self.retranslateUi(StationaryF007SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StationaryF007SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StationaryF007SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StationaryF007SetupDialog)
        StationaryF007SetupDialog.setTabOrder(self.edtEndDate, self.edtBegTime)
        StationaryF007SetupDialog.setTabOrder(self.edtBegTime, self.cmbSchedule)
        StationaryF007SetupDialog.setTabOrder(self.cmbSchedule, self.cmbProfileBed)
        StationaryF007SetupDialog.setTabOrder(self.cmbProfileBed, self.chkIsHideBeds)
        StationaryF007SetupDialog.setTabOrder(self.chkIsHideBeds, self.chkDetailOrgStructure)
        StationaryF007SetupDialog.setTabOrder(self.chkDetailOrgStructure, self.buttonBox)

    def retranslateUi(self, StationaryF007SetupDialog):
        StationaryF007SetupDialog.setWindowTitle(_translate("StationaryF007SetupDialog", "параметры отчёта", None))
        self.lblProfileBed.setText(_translate("StationaryF007SetupDialog", "&Профиль койки", None))
        self.lblEndDate.setText(_translate("StationaryF007SetupDialog", "Текущий &день", None))
        self.edtBegTime.setDisplayFormat(_translate("StationaryF007SetupDialog", "HH:mm", None))
        self.edtEndDate.setDisplayFormat(_translate("StationaryF007SetupDialog", "dd.MM.yyyy", None))
        self.chkIsHideBeds.setText(_translate("StationaryF007SetupDialog", "Скрывать данные по койкам", None))
        self.chkDetailOrgStructure.setText(_translate("StationaryF007SetupDialog", "Группировать по подразделениям", None))
        self.lblSchedule.setText(_translate("StationaryF007SetupDialog", "&Режим койки", None))
        self.lblOrgStructure.setText(_translate("StationaryF007SetupDialog", "&Подразделение", None))
        self.lblBegTime.setText(_translate("StationaryF007SetupDialog", "&Время начала суток", None))
        self.cmbSchedule.setItemText(0, _translate("StationaryF007SetupDialog", "Не учитывать", None))
        self.cmbSchedule.setItemText(1, _translate("StationaryF007SetupDialog", "Круглосуточные", None))
        self.cmbSchedule.setItemText(2, _translate("StationaryF007SetupDialog", "Не круглосуточные", None))

from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
from library.crbcombobox import CRBComboBox
