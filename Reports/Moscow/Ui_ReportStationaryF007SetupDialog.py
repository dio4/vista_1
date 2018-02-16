# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportStationaryF007SetupDialog.ui'
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

class Ui_ReportStationaryF007SetupDialog(object):
    def setupUi(self, ReportStationaryF007SetupDialog):
        ReportStationaryF007SetupDialog.setObjectName(_fromUtf8("ReportStationaryF007SetupDialog"))
        ReportStationaryF007SetupDialog.resize(450, 280)
        self.gridLayout = QtGui.QGridLayout(ReportStationaryF007SetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbOrgStructure = COrgStructureComboBox(ReportStationaryF007SetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 1, 1, 2)
        self.lblSchedule = QtGui.QLabel(ReportStationaryF007SetupDialog)
        self.lblSchedule.setObjectName(_fromUtf8("lblSchedule"))
        self.gridLayout.addWidget(self.lblSchedule, 4, 0, 1, 1)
        self.cmbBedSchedule = QtGui.QComboBox(ReportStationaryF007SetupDialog)
        self.cmbBedSchedule.setObjectName(_fromUtf8("cmbBedSchedule"))
        self.cmbBedSchedule.addItem(_fromUtf8(""))
        self.cmbBedSchedule.addItem(_fromUtf8(""))
        self.cmbBedSchedule.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbBedSchedule, 4, 1, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(ReportStationaryF007SetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 3, 0, 1, 1)
        self.lblProfileBed = QtGui.QLabel(ReportStationaryF007SetupDialog)
        self.lblProfileBed.setObjectName(_fromUtf8("lblProfileBed"))
        self.gridLayout.addWidget(self.lblProfileBed, 5, 0, 1, 1)
        self.cmbBedProfile = CRBComboBox(ReportStationaryF007SetupDialog)
        self.cmbBedProfile.setObjectName(_fromUtf8("cmbBedProfile"))
        self.gridLayout.addWidget(self.cmbBedProfile, 5, 1, 1, 2)
        self.chkDetailOrgStructure = QtGui.QCheckBox(ReportStationaryF007SetupDialog)
        self.chkDetailOrgStructure.setObjectName(_fromUtf8("chkDetailOrgStructure"))
        self.gridLayout.addWidget(self.chkDetailOrgStructure, 6, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ReportStationaryF007SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(129, 44, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 1)
        self.edtDate = CDateEdit(ReportStationaryF007SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDate.sizePolicy().hasHeightForWidth())
        self.edtDate.setSizePolicy(sizePolicy)
        self.edtDate.setCalendarPopup(True)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 0, 1, 1, 1)
        self.lblBegTime = QtGui.QLabel(ReportStationaryF007SetupDialog)
        self.lblBegTime.setObjectName(_fromUtf8("lblBegTime"))
        self.gridLayout.addWidget(self.lblBegTime, 1, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportStationaryF007SetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 0, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(192, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 2, 1, 1)
        self.edtBegTime = QtGui.QTimeEdit(ReportStationaryF007SetupDialog)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridLayout.addWidget(self.edtBegTime, 1, 1, 1, 1)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(ReportStationaryF007SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportStationaryF007SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportStationaryF007SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportStationaryF007SetupDialog)

    def retranslateUi(self, ReportStationaryF007SetupDialog):
        ReportStationaryF007SetupDialog.setWindowTitle(_translate("ReportStationaryF007SetupDialog", "Dialog", None))
        self.lblSchedule.setText(_translate("ReportStationaryF007SetupDialog", "Режим койки", None))
        self.cmbBedSchedule.setItemText(0, _translate("ReportStationaryF007SetupDialog", "Не учитывать", None))
        self.cmbBedSchedule.setItemText(1, _translate("ReportStationaryF007SetupDialog", "Круглосуточные", None))
        self.cmbBedSchedule.setItemText(2, _translate("ReportStationaryF007SetupDialog", "Не круглосуточные", None))
        self.lblOrgStructure.setText(_translate("ReportStationaryF007SetupDialog", "&Подразделение", None))
        self.lblProfileBed.setText(_translate("ReportStationaryF007SetupDialog", "Профиль койки", None))
        self.chkDetailOrgStructure.setText(_translate("ReportStationaryF007SetupDialog", "Группировать по подразделениям", None))
        self.edtDate.setDisplayFormat(_translate("ReportStationaryF007SetupDialog", "dd.MM.yyyy", None))
        self.lblBegTime.setText(_translate("ReportStationaryF007SetupDialog", "Время начала суток", None))
        self.lblEndDate.setText(_translate("ReportStationaryF007SetupDialog", "Текущий день", None))
        self.edtBegTime.setDisplayFormat(_translate("ReportStationaryF007SetupDialog", "HH:mm", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
