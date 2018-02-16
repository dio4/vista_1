# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\StationaryMESF14DCSetup.ui'
#
# Created: Fri Jun 15 12:17:33 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_StationaryMESF14DCDialog(object):
    def setupUi(self, StationaryMESF14DCDialog):
        StationaryMESF14DCDialog.setObjectName(_fromUtf8("StationaryMESF14DCDialog"))
        StationaryMESF14DCDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        StationaryMESF14DCDialog.resize(438, 267)
        StationaryMESF14DCDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(StationaryMESF14DCDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(StationaryMESF14DCDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(StationaryMESF14DCDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(StationaryMESF14DCDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 2)
        self.lblGroupMES = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblGroupMES.setObjectName(_fromUtf8("lblGroupMES"))
        self.gridLayout.addWidget(self.lblGroupMES, 3, 0, 1, 1)
        self.cmbGroupMES = CRBComboBox(StationaryMESF14DCDialog)
        self.cmbGroupMES.setObjectName(_fromUtf8("cmbGroupMES"))
        self.gridLayout.addWidget(self.cmbGroupMES, 3, 1, 1, 2)
        self.lblMes = QtGui.QLabel(StationaryMESF14DCDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMes.sizePolicy().hasHeightForWidth())
        self.lblMes.setSizePolicy(sizePolicy)
        self.lblMes.setObjectName(_fromUtf8("lblMes"))
        self.gridLayout.addWidget(self.lblMes, 4, 0, 1, 1)
        self.cmbMes = CMESComboBox(StationaryMESF14DCDialog)
        self.cmbMes.setObjectName(_fromUtf8("cmbMes"))
        self.gridLayout.addWidget(self.cmbMes, 4, 1, 1, 2)
        self.lblProfile = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblProfile.setObjectName(_fromUtf8("lblProfile"))
        self.gridLayout.addWidget(self.lblProfile, 5, 0, 1, 1)
        self.cmbFilterProfile = CRBComboBox(StationaryMESF14DCDialog)
        self.cmbFilterProfile.setObjectName(_fromUtf8("cmbFilterProfile"))
        self.gridLayout.addWidget(self.cmbFilterProfile, 5, 1, 1, 2)
        self.lblGroupType = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblGroupType.setObjectName(_fromUtf8("lblGroupType"))
        self.gridLayout.addWidget(self.lblGroupType, 6, 0, 1, 1)
        self.cmbGroupType = QtGui.QComboBox(StationaryMESF14DCDialog)
        self.cmbGroupType.setObjectName(_fromUtf8("cmbGroupType"))
        self.cmbGroupType.addItem(_fromUtf8(""))
        self.cmbGroupType.addItem(_fromUtf8(""))
        self.cmbGroupType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbGroupType, 6, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 7, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(StationaryMESF14DCDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblMes.setBuddy(self.cmbMes)

        self.retranslateUi(StationaryMESF14DCDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StationaryMESF14DCDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StationaryMESF14DCDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StationaryMESF14DCDialog)
        StationaryMESF14DCDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        StationaryMESF14DCDialog.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        StationaryMESF14DCDialog.setTabOrder(self.cmbOrgStructure, self.cmbGroupMES)
        StationaryMESF14DCDialog.setTabOrder(self.cmbGroupMES, self.cmbMes)
        StationaryMESF14DCDialog.setTabOrder(self.cmbMes, self.cmbFilterProfile)
        StationaryMESF14DCDialog.setTabOrder(self.cmbFilterProfile, self.cmbGroupType)
        StationaryMESF14DCDialog.setTabOrder(self.cmbGroupType, self.buttonBox)

    def retranslateUi(self, StationaryMESF14DCDialog):
        StationaryMESF14DCDialog.setWindowTitle(QtGui.QApplication.translate("StationaryMESF14DCDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "Дата &начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.edtBegDate.setDisplayFormat(QtGui.QApplication.translate("StationaryMESF14DCDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "Дата &окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.edtEndDate.setDisplayFormat(QtGui.QApplication.translate("StationaryMESF14DCDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "&Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblGroupMES.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "Группа МЭС", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMes.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "МЭС", None, QtGui.QApplication.UnicodeUTF8))
        self.lblProfile.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "Профиль койки", None, QtGui.QApplication.UnicodeUTF8))
        self.lblGroupType.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "Группировать", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbGroupType.setItemText(0, QtGui.QApplication.translate("StationaryMESF14DCDialog", "Не группировать", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbGroupType.setItemText(1, QtGui.QApplication.translate("StationaryMESF14DCDialog", "По типу события", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbGroupType.setItemText(2, QtGui.QApplication.translate("StationaryMESF14DCDialog", "По типу МЭС", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from library.MES.MESComboBox import CMESComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    StationaryMESF14DCDialog = QtGui.QDialog()
    ui = Ui_StationaryMESF14DCDialog()
    ui.setupUi(StationaryMESF14DCDialog)
    StationaryMESF14DCDialog.show()
    sys.exit(app.exec_())

