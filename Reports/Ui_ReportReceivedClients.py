# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReceivedClients.ui'
#
# Created: Wed Nov 26 19:22:43 2014
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

class Ui_ReportReceivedClients(object):
    def setupUi(self, ReceivedClients):
        ReceivedClients.setObjectName(_fromUtf8("ReceivedClients"))
        ReceivedClients.setWindowModality(QtCore.Qt.ApplicationModal)
        ReceivedClients.resize(389, 214)
        ReceivedClients.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReceivedClients)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtBegDateTime = QtGui.QDateTimeEdit(ReceivedClients)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDateTime.sizePolicy().hasHeightForWidth())
        self.edtBegDateTime.setSizePolicy(sizePolicy)
        self.edtBegDateTime.setCalendarPopup(True)
        self.edtBegDateTime.setObjectName(_fromUtf8("edtBegDateTime"))
        self.gridLayout.addWidget(self.edtBegDateTime, 0, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 3, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReceivedClients)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 5)
        self.lblOrgStructure = QtGui.QLabel(ReceivedClients)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.edtEndDateTime = QtGui.QDateTimeEdit(ReceivedClients)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDateTime.sizePolicy().hasHeightForWidth())
        self.edtEndDateTime.setSizePolicy(sizePolicy)
        self.edtEndDateTime.setCalendarPopup(True)
        self.edtEndDateTime.setObjectName(_fromUtf8("edtEndDateTime"))
        self.gridLayout.addWidget(self.edtEndDateTime, 1, 1, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReceivedClients)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReceivedClients)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 4)
        self.lblEndDate = QtGui.QLabel(ReceivedClients)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lblProfileBed = QtGui.QLabel(ReceivedClients)
        self.lblProfileBed.setObjectName(_fromUtf8("lblProfileBed"))
        self.gridLayout.addWidget(self.lblProfileBed, 3, 0, 1, 1)
        self.cmbProfileBed = CRBComboBox(ReceivedClients)
        self.cmbProfileBed.setObjectName(_fromUtf8("cmbProfileBed"))
        self.gridLayout.addWidget(self.cmbProfileBed, 3, 1, 1, 4)
        self.retranslateUi(ReceivedClients)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReceivedClients.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReceivedClients.reject)
        QtCore.QMetaObject.connectSlotsByName(ReceivedClients)
        ReceivedClients.setTabOrder(self.edtBegDateTime, self.edtEndDateTime)
        ReceivedClients.setTabOrder(self.edtEndDateTime, self.cmbOrgStructure)
        ReceivedClients.setTabOrder(self.cmbOrgStructure, self.buttonBox)

    def retranslateUi(self, ReceivedClients):
        ReceivedClients.setWindowTitle(_translate("ReceivedClients", "параметры отчёта", None))
        self.lblOrgStructure.setText(_translate("ReceivedClients", "Подразделение", None))
        self.lblBegDate.setText(_translate("ReceivedClients", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReceivedClients", "Дата окончания периода", None))
        self.lblProfileBed.setText(_translate("ReceivedClients", "Профиль койки", None))


from library.crbcombobox import CRBComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
