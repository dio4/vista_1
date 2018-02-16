# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPrimarySecondary.ui'
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

class Ui_SetupDialog(object):
    def setupUi(self, SetupDialog):
        SetupDialog.setObjectName(_fromUtf8("SetupDialog"))
        SetupDialog.resize(600, 400)
        self.gridLayout = QtGui.QGridLayout(SetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(SetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(SetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lblEventType = QtGui.QLabel(SetupDialog)
        self.lblEventType.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 2, 0, 1, 1)
        self.lstEventTypes = CRBListBox(SetupDialog)
        self.lstEventTypes.setObjectName(_fromUtf8("lstEventTypes"))
        self.gridLayout.addWidget(self.lstEventTypes, 2, 1, 1, 7)
        self.lblOrgStructure = QtGui.QLabel(SetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 3, 0, 1, 1)
        self.lblAge = QtGui.QLabel(SetupDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout.addWidget(self.lblAge, 4, 0, 1, 1)
        self.edtAgeFrom = QtGui.QSpinBox(SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeFrom.sizePolicy().hasHeightForWidth())
        self.edtAgeFrom.setSizePolicy(sizePolicy)
        self.edtAgeFrom.setSuffix(_fromUtf8(""))
        self.edtAgeFrom.setMaximum(150)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self.gridLayout.addWidget(self.edtAgeFrom, 4, 2, 1, 2)
        self.lblAgeTo = QtGui.QLabel(SetupDialog)
        self.lblAgeTo.setObjectName(_fromUtf8("lblAgeTo"))
        self.gridLayout.addWidget(self.lblAgeTo, 4, 4, 1, 1)
        self.edtAgeTo = QtGui.QSpinBox(SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeTo.sizePolicy().hasHeightForWidth())
        self.edtAgeTo.setSizePolicy(sizePolicy)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setProperty("value", 150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self.gridLayout.addWidget(self.edtAgeTo, 4, 5, 1, 1)
        self.lblAgeYears = QtGui.QLabel(SetupDialog)
        self.lblAgeYears.setObjectName(_fromUtf8("lblAgeYears"))
        self.gridLayout.addWidget(self.lblAgeYears, 4, 6, 1, 1)
        spacerItem = QtGui.QSpacerItem(196, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 4, 7, 1, 1)
        self.lblSex = QtGui.QLabel(SetupDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout.addWidget(self.lblSex, 5, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 7, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(SetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 1, 1, 7)
        self.lblAgeFrom = QtGui.QLabel(SetupDialog)
        self.lblAgeFrom.setObjectName(_fromUtf8("lblAgeFrom"))
        self.gridLayout.addWidget(self.lblAgeFrom, 4, 1, 1, 1)
        self.cmbSex = QtGui.QComboBox(SetupDialog)
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
        self.gridLayout.addWidget(self.cmbSex, 5, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 5, 1, 3)
        self.edtBegDate = CDateEdit(SetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 4)
        self.edtEndDate = CDateEdit(SetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 4)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblEventType.setBuddy(self.lstEventTypes)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblAge.setBuddy(self.edtAgeFrom)
        self.lblAgeTo.setBuddy(self.edtAgeTo)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblAgeFrom.setBuddy(self.edtAgeFrom)

        self.retranslateUi(SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SetupDialog)
        SetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        SetupDialog.setTabOrder(self.edtEndDate, self.lstEventTypes)
        SetupDialog.setTabOrder(self.lstEventTypes, self.cmbOrgStructure)
        SetupDialog.setTabOrder(self.cmbOrgStructure, self.edtAgeFrom)
        SetupDialog.setTabOrder(self.edtAgeFrom, self.edtAgeTo)
        SetupDialog.setTabOrder(self.edtAgeTo, self.cmbSex)
        SetupDialog.setTabOrder(self.cmbSex, self.buttonBox)

    def retranslateUi(self, SetupDialog):
        SetupDialog.setWindowTitle(_translate("SetupDialog", "Dialog", None))
        self.lblBegDate.setText(_translate("SetupDialog", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("SetupDialog", "Дата &окончания периода", None))
        self.lblEventType.setText(_translate("SetupDialog", "&Тип обращения", None))
        self.lblOrgStructure.setText(_translate("SetupDialog", "&Подразделение", None))
        self.lblAge.setText(_translate("SetupDialog", "Во&зраст", None))
        self.lblAgeTo.setText(_translate("SetupDialog", "по", None))
        self.lblAgeYears.setText(_translate("SetupDialog", "лет", None))
        self.lblSex.setText(_translate("SetupDialog", "По&л", None))
        self.lblAgeFrom.setText(_translate("SetupDialog", "с", None))
        self.cmbSex.setItemText(1, _translate("SetupDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("SetupDialog", "Ж", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
