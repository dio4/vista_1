# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportExistingClients.ui'
#
# Created: Wed Apr 29 15:07:53 2015
#      by: PyQt4 UI code generator 4.11.1
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(398, 335)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 1, 1, 1)
        self.lblDays = QtGui.QLabel(Dialog)
        self.lblDays.setObjectName(_fromUtf8("lblDays"))
        self.gridLayout.addWidget(self.lblDays, 4, 0, 1, 1)
        self.cmbEventType = CRBComboBox(Dialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 0, 1, 1, 2)
        self.lstOrgStructure = CRBListBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lstOrgStructure.sizePolicy().hasHeightForWidth())
        self.lstOrgStructure.setSizePolicy(sizePolicy)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridLayout.addWidget(self.lstOrgStructure, 3, 0, 1, 3)
        self.edtDays = QtGui.QLineEdit(Dialog)
        self.edtDays.setObjectName(_fromUtf8("edtDays"))
        self.gridLayout.addWidget(self.edtDays, 4, 1, 1, 1)
        self.lstEventType = CRBListBox(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lstEventType.sizePolicy().hasHeightForWidth())
        self.lstEventType.setSizePolicy(sizePolicy)
        self.lstEventType.setObjectName(_fromUtf8("lstEventType"))
        self.gridLayout.addWidget(self.lstEventType, 1, 0, 1, 3)
        self.chkOrgStructureMulti = QtGui.QCheckBox(Dialog)
        self.chkOrgStructureMulti.setObjectName(_fromUtf8("chkOrgStructureMulti"))
        self.gridLayout.addWidget(self.chkOrgStructureMulti, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.chkEventTypeMulti = QtGui.QCheckBox(Dialog)
        self.chkEventTypeMulti.setObjectName(_fromUtf8("chkEventTypeMulti"))
        self.gridLayout.addWidget(self.chkEventTypeMulti, 0, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(Dialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.lblDays.setText(_translate("Dialog", "Количество койко-дней", None))
        self.chkOrgStructureMulti.setText(_translate("Dialog", "Подразделение", None))
        self.chkEventTypeMulti.setText(_translate("Dialog", "Тип обращения", None))

from library.RBListBox import CRBListBox
from library.crbcombobox import CRBComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
