# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\ReportActionsByServiceTypeSetupDialog.ui'
#
# Created: Fri Jun 15 12:17:54 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportActionsByServiceTypeSetupDialog(object):
    def setupUi(self, ReportActionsByServiceTypeSetupDialog):
        ReportActionsByServiceTypeSetupDialog.setObjectName(_fromUtf8("ReportActionsByServiceTypeSetupDialog"))
        ReportActionsByServiceTypeSetupDialog.resize(530, 288)
        self.gridLayout = QtGui.QGridLayout(ReportActionsByServiceTypeSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportActionsByServiceTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblBegDate.sizePolicy().hasHeightForWidth())
        self.lblBegDate.setSizePolicy(sizePolicy)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportActionsByServiceTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportActionsByServiceTypeSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportActionsByServiceTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(ReportActionsByServiceTypeSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportActionsByServiceTypeSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 2)
        self.lblFinance = QtGui.QLabel(ReportActionsByServiceTypeSetupDialog)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 3, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportActionsByServiceTypeSetupDialog)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 3, 1, 1, 2)
        self.chkPodtver = QtGui.QCheckBox(ReportActionsByServiceTypeSetupDialog)
        self.chkPodtver.setObjectName(_fromUtf8("chkPodtver"))
        self.gridLayout.addWidget(self.chkPodtver, 4, 0, 1, 1)
        self.lblPodtver = QtGui.QLabel(ReportActionsByServiceTypeSetupDialog)
        self.lblPodtver.setEnabled(False)
        self.lblPodtver.setObjectName(_fromUtf8("lblPodtver"))
        self.gridLayout.addWidget(self.lblPodtver, 5, 0, 1, 1)
        self.cmbPodtver = QtGui.QComboBox(ReportActionsByServiceTypeSetupDialog)
        self.cmbPodtver.setEnabled(False)
        self.cmbPodtver.setObjectName(_fromUtf8("cmbPodtver"))
        self.cmbPodtver.addItem(_fromUtf8(""))
        self.cmbPodtver.addItem(_fromUtf8(""))
        self.cmbPodtver.addItem(_fromUtf8(""))
        self.cmbPodtver.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbPodtver, 5, 1, 1, 2)
        self.lblBegDatePodtver = QtGui.QLabel(ReportActionsByServiceTypeSetupDialog)
        self.lblBegDatePodtver.setEnabled(False)
        self.lblBegDatePodtver.setObjectName(_fromUtf8("lblBegDatePodtver"))
        self.gridLayout.addWidget(self.lblBegDatePodtver, 6, 0, 1, 1)
        self.edtBegDatePodtver = CDateEdit(ReportActionsByServiceTypeSetupDialog)
        self.edtBegDatePodtver.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDatePodtver.sizePolicy().hasHeightForWidth())
        self.edtBegDatePodtver.setSizePolicy(sizePolicy)
        self.edtBegDatePodtver.setObjectName(_fromUtf8("edtBegDatePodtver"))
        self.gridLayout.addWidget(self.edtBegDatePodtver, 6, 1, 1, 1)
        self.lblEndDatePodtver = QtGui.QLabel(ReportActionsByServiceTypeSetupDialog)
        self.lblEndDatePodtver.setEnabled(False)
        self.lblEndDatePodtver.setObjectName(_fromUtf8("lblEndDatePodtver"))
        self.gridLayout.addWidget(self.lblEndDatePodtver, 7, 0, 1, 1)
        self.edtEndDatePodtver = CDateEdit(ReportActionsByServiceTypeSetupDialog)
        self.edtEndDatePodtver.setEnabled(False)
        self.edtEndDatePodtver.setObjectName(_fromUtf8("edtEndDatePodtver"))
        self.gridLayout.addWidget(self.edtEndDatePodtver, 7, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportActionsByServiceTypeSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(ReportActionsByServiceTypeSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportActionsByServiceTypeSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportActionsByServiceTypeSetupDialog.reject)
        QtCore.QObject.connect(self.chkPodtver, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cmbPodtver.setEnabled)
        QtCore.QObject.connect(self.chkPodtver, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.edtBegDatePodtver.setEnabled)
        QtCore.QObject.connect(self.chkPodtver, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.edtEndDatePodtver.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ReportActionsByServiceTypeSetupDialog)
        ReportActionsByServiceTypeSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportActionsByServiceTypeSetupDialog.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        ReportActionsByServiceTypeSetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbFinance)
        ReportActionsByServiceTypeSetupDialog.setTabOrder(self.cmbFinance, self.chkPodtver)
        ReportActionsByServiceTypeSetupDialog.setTabOrder(self.chkPodtver, self.cmbPodtver)
        ReportActionsByServiceTypeSetupDialog.setTabOrder(self.cmbPodtver, self.edtBegDatePodtver)
        ReportActionsByServiceTypeSetupDialog.setTabOrder(self.edtBegDatePodtver, self.edtEndDatePodtver)
        ReportActionsByServiceTypeSetupDialog.setTabOrder(self.edtEndDatePodtver, self.buttonBox)

    def retranslateUi(self, ReportActionsByServiceTypeSetupDialog):
        ReportActionsByServiceTypeSetupDialog.setWindowTitle(QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "Дата &начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "Дата &окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "&Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFinance.setText(QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "Тип финансирования", None, QtGui.QApplication.UnicodeUTF8))
        self.chkPodtver.setText(QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "Подтверждение оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPodtver.setText(QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "Тип подтверждения:", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPodtver.setItemText(0, QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "не выставлено", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPodtver.setItemText(1, QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "выставлено", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPodtver.setItemText(2, QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "оплачено", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPodtver.setItemText(3, QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "отказано", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDatePodtver.setText(QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "Начало периода подтверждения:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDatePodtver.setText(QtGui.QApplication.translate("ReportActionsByServiceTypeSetupDialog", "Окончание периода подтверждения:", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportActionsByServiceTypeSetupDialog = QtGui.QDialog()
    ui = Ui_ReportActionsByServiceTypeSetupDialog()
    ui.setupUi(ReportActionsByServiceTypeSetupDialog)
    ReportActionsByServiceTypeSetupDialog.show()
    sys.exit(app.exec_())

