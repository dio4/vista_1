# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NonPaidEventsSetupdialog.ui'
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

class Ui_NonPaidEventsSetupDialog(object):
    def setupUi(self, NonPaidEventsSetupDialog):
        NonPaidEventsSetupDialog.setObjectName(_fromUtf8("NonPaidEventsSetupDialog"))
        NonPaidEventsSetupDialog.resize(407, 204)
        self.gridLayout = QtGui.QGridLayout(NonPaidEventsSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEndDate = QtGui.QLabel(NonPaidEventsSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 0, 0, 1, 1)
        self.cmbContract = CContractComboBox(NonPaidEventsSetupDialog)
        self.cmbContract.setObjectName(_fromUtf8("cmbContract"))
        self.gridLayout.addWidget(self.cmbContract, 2, 1, 1, 1)
        self.lblContract = QtGui.QLabel(NonPaidEventsSetupDialog)
        self.lblContract.setObjectName(_fromUtf8("lblContract"))
        self.gridLayout.addWidget(self.lblContract, 2, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(NonPaidEventsSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 1, 0, 1, 1)
        self.endDate = CDateEdit(NonPaidEventsSetupDialog)
        self.endDate.setObjectName(_fromUtf8("endDate"))
        self.gridLayout.addWidget(self.endDate, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(NonPaidEventsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 2)
        self.begDate = CDateEdit(NonPaidEventsSetupDialog)
        self.begDate.setObjectName(_fromUtf8("begDate"))
        self.gridLayout.addWidget(self.begDate, 0, 1, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(NonPaidEventsSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 5, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(NonPaidEventsSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 5, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 1, 1, 1)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(NonPaidEventsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NonPaidEventsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NonPaidEventsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NonPaidEventsSetupDialog)
        NonPaidEventsSetupDialog.setTabOrder(self.begDate, self.buttonBox)

    def retranslateUi(self, NonPaidEventsSetupDialog):
        NonPaidEventsSetupDialog.setWindowTitle(_translate("NonPaidEventsSetupDialog", "Неоплаченные события", None))
        self.lblEndDate.setText(_translate("NonPaidEventsSetupDialog", "Дата начала", None))
        self.lblContract.setText(_translate("NonPaidEventsSetupDialog", "Договор", None))
        self.lblBegDate.setText(_translate("NonPaidEventsSetupDialog", "Дата окончания", None))
        self.lblOrgStructure.setText(_translate("NonPaidEventsSetupDialog", "&Подразделение", None))

from Accounting.ContractComboBox import CContractComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
