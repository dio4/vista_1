# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPNDClientsRegistrySetup.ui'
#
# Created: Sun Dec 01 10:45:41 2013
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_ReportPNDClientsRegistrySetupDialog(object):
    def setupUi(self, ReportPNDClientsRegistrySetupDialog):
        ReportPNDClientsRegistrySetupDialog.setObjectName(_fromUtf8("ReportPNDClientsRegistrySetupDialog"))
        ReportPNDClientsRegistrySetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportPNDClientsRegistrySetupDialog.resize(396, 246)
        ReportPNDClientsRegistrySetupDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ReportPNDClientsRegistrySetupDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.frmAge = QtGui.QFrame(ReportPNDClientsRegistrySetupDialog)
        self.frmAge.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAge.setFrameShadow(QtGui.QFrame.Raised)
        self.frmAge.setObjectName(_fromUtf8("frmAge"))
        self._2 = QtGui.QHBoxLayout(self.frmAge)
        self._2.setSpacing(4)
        self._2.setMargin(0)
        self._2.setObjectName(_fromUtf8("_2"))
        self.edtAgeFrom = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeFrom.sizePolicy().hasHeightForWidth())
        self.edtAgeFrom.setSizePolicy(sizePolicy)
        self.edtAgeFrom.setMaximum(150)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self._2.addWidget(self.edtAgeFrom)
        self.lblAgeTo = QtGui.QLabel(self.frmAge)
        self.lblAgeTo.setObjectName(_fromUtf8("lblAgeTo"))
        self._2.addWidget(self.lblAgeTo)
        self.edtAgeTo = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeTo.sizePolicy().hasHeightForWidth())
        self.edtAgeTo.setSizePolicy(sizePolicy)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self._2.addWidget(self.edtAgeTo)
        self.lblAgeYears = QtGui.QLabel(self.frmAge)
        self.lblAgeYears.setObjectName(_fromUtf8("lblAgeYears"))
        self._2.addWidget(self.lblAgeYears)
        spacerItem = QtGui.QSpacerItem(21, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self._2.addItem(spacerItem)
        self.gridlayout.addWidget(self.frmAge, 5, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 0, 2, 1, 1)
        self.lblSex = QtGui.QLabel(ReportPNDClientsRegistrySetupDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridlayout.addWidget(self.lblSex, 4, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportPNDClientsRegistrySetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridlayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportPNDClientsRegistrySetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridlayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 1, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportPNDClientsRegistrySetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridlayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem3, 9, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportPNDClientsRegistrySetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 10, 0, 1, 3)
        self.cmbSex = QtGui.QComboBox(ReportPNDClientsRegistrySetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSex.sizePolicy().hasHeightForWidth())
        self.cmbSex.setSizePolicy(sizePolicy)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbSex, 4, 1, 1, 1)
        self.lblAge = QtGui.QLabel(ReportPNDClientsRegistrySetupDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridlayout.addWidget(self.lblAge, 5, 0, 1, 1)
        self.lblAttachType = QtGui.QLabel(ReportPNDClientsRegistrySetupDialog)
        self.lblAttachType.setObjectName(_fromUtf8("lblAttachType"))
        self.gridlayout.addWidget(self.lblAttachType, 6, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportPNDClientsRegistrySetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridlayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportPNDClientsRegistrySetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridlayout.addWidget(self.cmbOrgStructure, 6, 1, 1, 2)
        self.lblSocStatusClass = QtGui.QLabel(ReportPNDClientsRegistrySetupDialog)
        self.lblSocStatusClass.setObjectName(_fromUtf8("lblSocStatusClass"))
        self.gridlayout.addWidget(self.lblSocStatusClass, 7, 0, 1, 1)
        self.cmbSocStatusClass = CSocStatusComboBox(ReportPNDClientsRegistrySetupDialog)
        self.cmbSocStatusClass.setObjectName(_fromUtf8("cmbSocStatusClass"))
        self.gridlayout.addWidget(self.cmbSocStatusClass, 7, 1, 1, 2)
        self.lblEventType = QtGui.QLabel(ReportPNDClientsRegistrySetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridlayout.addWidget(self.lblEventType, 8, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportPNDClientsRegistrySetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridlayout.addWidget(self.cmbEventType, 8, 1, 1, 2)
        self.lblAgeTo.setBuddy(self.edtAgeTo)
        self.lblAgeYears.setBuddy(self.edtAgeTo)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblAge.setBuddy(self.edtAgeFrom)
        self.lblAttachType.setBuddy(self.cmbOrgStructure)
        self.lblSocStatusClass.setBuddy(self.cmbSocStatusClass)
        self.lblEventType.setBuddy(self.cmbEventType)

        self.retranslateUi(ReportPNDClientsRegistrySetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportPNDClientsRegistrySetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportPNDClientsRegistrySetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportPNDClientsRegistrySetupDialog)
        ReportPNDClientsRegistrySetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportPNDClientsRegistrySetupDialog.setTabOrder(self.edtEndDate, self.cmbSex)
        ReportPNDClientsRegistrySetupDialog.setTabOrder(self.cmbSex, self.edtAgeFrom)
        ReportPNDClientsRegistrySetupDialog.setTabOrder(self.edtAgeFrom, self.edtAgeTo)
        ReportPNDClientsRegistrySetupDialog.setTabOrder(self.edtAgeTo, self.cmbOrgStructure)
        ReportPNDClientsRegistrySetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbSocStatusClass)
        ReportPNDClientsRegistrySetupDialog.setTabOrder(self.cmbSocStatusClass, self.cmbEventType)
        ReportPNDClientsRegistrySetupDialog.setTabOrder(self.cmbEventType, self.buttonBox)

    def retranslateUi(self, ReportPNDClientsRegistrySetupDialog):
        ReportPNDClientsRegistrySetupDialog.setWindowTitle(_translate("ReportPNDClientsRegistrySetupDialog", "параметры отчёта", None))
        self.lblAgeTo.setText(_translate("ReportPNDClientsRegistrySetupDialog", "по", None))
        self.lblAgeYears.setText(_translate("ReportPNDClientsRegistrySetupDialog", "лет", None))
        self.lblSex.setText(_translate("ReportPNDClientsRegistrySetupDialog", "По&л", None))
        self.lblBegDate.setText(_translate("ReportPNDClientsRegistrySetupDialog", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportPNDClientsRegistrySetupDialog", "Дата &окончания периода", None))
        self.cmbSex.setItemText(1, _translate("ReportPNDClientsRegistrySetupDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("ReportPNDClientsRegistrySetupDialog", "Ж", None))
        self.lblAge.setText(_translate("ReportPNDClientsRegistrySetupDialog", "Во&зраст с", None))
        self.lblAttachType.setText(_translate("ReportPNDClientsRegistrySetupDialog", "Подразделение", None))
        self.lblSocStatusClass.setText(_translate("ReportPNDClientsRegistrySetupDialog", "Социальный статус", None))
        self.lblEventType.setText(_translate("ReportPNDClientsRegistrySetupDialog", "Тип обращения", None))

from library.crbcombobox import CRBComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from Registry.SocStatusComboBox import CSocStatusComboBox