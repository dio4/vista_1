# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportAgeSexCompositionLeavedClients.ui'
#
# Created: Fri Nov 28 17:17:02 2014
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

class Ui_ReportAgeSexCompositionLeavedClients(object):
    def setupUi(self, ReportAgeSexCompositionLeavedClients):
        ReportAgeSexCompositionLeavedClients.setObjectName(_fromUtf8("ReportAgeSexCompositionLeavedClients"))
        ReportAgeSexCompositionLeavedClients.resize(404, 220)
        self.gridLayout = QtGui.QGridLayout(ReportAgeSexCompositionLeavedClients)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtBegDate = CDateEdit(ReportAgeSexCompositionLeavedClients)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportAgeSexCompositionLeavedClients)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportAgeSexCompositionLeavedClients)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportAgeSexCompositionLeavedClients)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportAgeSexCompositionLeavedClients)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.lblProfileBed = QtGui.QLabel(ReportAgeSexCompositionLeavedClients)
        self.lblProfileBed.setObjectName(_fromUtf8("lblProfileBed"))
        self.gridLayout.addWidget(self.lblProfileBed, 3, 0, 1, 1)
        self.cmbProfileBed = CRBComboBox(ReportAgeSexCompositionLeavedClients)
        self.cmbProfileBed.setObjectName(_fromUtf8("cmbProfileBed"))
        self.gridLayout.addWidget(self.cmbProfileBed, 3, 1, 1, 2)
        self.lblOrder = QtGui.QLabel(ReportAgeSexCompositionLeavedClients)
        self.lblOrder.setObjectName(_fromUtf8("lblOrder"))
        self.gridLayout.addWidget(self.lblOrder, 4, 0, 1, 1)
        self.cmbOrder = QtGui.QComboBox(ReportAgeSexCompositionLeavedClients)
        self.cmbOrder.setObjectName(_fromUtf8("cmbOrder"))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbOrder, 4, 1, 1, 2)
        self.chkUngroupProfileBeds = QtGui.QCheckBox(ReportAgeSexCompositionLeavedClients)
        self.chkUngroupProfileBeds.setObjectName(_fromUtf8("chkUngroupProfileBeds"))
        self.gridLayout.addWidget(self.chkUngroupProfileBeds, 6, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportAgeSexCompositionLeavedClients)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 2)
        self.lblTypeHosp = QtGui.QLabel(ReportAgeSexCompositionLeavedClients)
        self.lblTypeHosp.setObjectName(_fromUtf8("lblTypeHosp"))
        self.gridLayout.addWidget(self.lblTypeHosp, 5, 0, 1, 1)
        self.cmbTypeHosp = QtGui.QComboBox(ReportAgeSexCompositionLeavedClients)
        self.cmbTypeHosp.setObjectName(_fromUtf8("cmbTypeHosp"))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.cmbTypeHosp.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbTypeHosp, 5, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAgeSexCompositionLeavedClients)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 2, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(ReportAgeSexCompositionLeavedClients)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAgeSexCompositionLeavedClients.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAgeSexCompositionLeavedClients.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAgeSexCompositionLeavedClients)

    def retranslateUi(self, ReportAgeSexCompositionLeavedClients):
        ReportAgeSexCompositionLeavedClients.setWindowTitle(_translate("ReportAgeSexCompositionLeavedClients", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportAgeSexCompositionLeavedClients", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportAgeSexCompositionLeavedClients", "Дата &окончания периода", None))
        self.lblOrgStructure.setText(_translate("ReportAgeSexCompositionLeavedClients", "&Подразделение", None))
        self.lblProfileBed.setText(_translate("ReportAgeSexCompositionLeavedClients", "Профиль койки", None))
        self.lblOrder.setText(_translate("ReportAgeSexCompositionLeavedClients", "Порядок", None))
        self.cmbOrder.setItemText(0, _translate("ReportAgeSexCompositionLeavedClients", "не задано", None))
        self.cmbOrder.setItemText(1, _translate("ReportAgeSexCompositionLeavedClients", "планово", None))
        self.cmbOrder.setItemText(2, _translate("ReportAgeSexCompositionLeavedClients", "экстренно", None))
        self.chkUngroupProfileBeds.setText(_translate("ReportAgeSexCompositionLeavedClients", "не группировать по профилям", None))
        self.lblTypeHosp.setText(_translate("ReportAgeSexCompositionLeavedClients", "Вид госпитализации", None))
        self.cmbTypeHosp.setItemText(0, _translate("ReportAgeSexCompositionLeavedClients", "не задано", None))
        self.cmbTypeHosp.setItemText(1, _translate("ReportAgeSexCompositionLeavedClients", "круглосуточный стационар", None))
        self.cmbTypeHosp.setItemText(2, _translate("ReportAgeSexCompositionLeavedClients", "дневной стационар", None))
        self.cmbTypeHosp.setItemText(3, _translate("ReportAgeSexCompositionLeavedClients", "амбулаторно", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
