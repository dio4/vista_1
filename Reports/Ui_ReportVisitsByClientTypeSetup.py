# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportVisitsByClientTypeSetup.ui'
#
# Created: Tue Jan 12 17:55:17 2016
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_ReportVisitsByClientTypeSetupDialog(object):
    def setupUi(self, ReportVisitsByClientTypeSetupDialog):
        ReportVisitsByClientTypeSetupDialog.setObjectName(_fromUtf8("ReportVisitsByClientTypeSetupDialog"))
        ReportVisitsByClientTypeSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportVisitsByClientTypeSetupDialog.resize(363, 321)
        ReportVisitsByClientTypeSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportVisitsByClientTypeSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCitizen = QtGui.QLabel(ReportVisitsByClientTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblCitizen.sizePolicy().hasHeightForWidth())
        self.lblCitizen.setSizePolicy(sizePolicy)
        self.lblCitizen.setObjectName(_fromUtf8("lblCitizen"))
        self.gridLayout.addWidget(self.lblCitizen, 6, 0, 1, 2)
        self.lblBegDate = QtGui.QLabel(ReportVisitsByClientTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblBegDate.sizePolicy().hasHeightForWidth())
        self.lblBegDate.setSizePolicy(sizePolicy)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.lblMKBTo = QtGui.QLabel(ReportVisitsByClientTypeSetupDialog)
        self.lblMKBTo.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMKBTo.sizePolicy().hasHeightForWidth())
        self.lblMKBTo.setSizePolicy(sizePolicy)
        self.lblMKBTo.setObjectName(_fromUtf8("lblMKBTo"))
        self.gridLayout.addWidget(self.lblMKBTo, 5, 5, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportVisitsByClientTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEventType.sizePolicy().hasHeightForWidth())
        self.lblEventType.setSizePolicy(sizePolicy)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 2, 0, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportVisitsByClientTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEndDate.sizePolicy().hasHeightForWidth())
        self.lblEndDate.setSizePolicy(sizePolicy)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 2)
        self.cmbMKBFrom = CICDCodeEditEx(ReportVisitsByClientTypeSetupDialog)
        self.cmbMKBFrom.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbMKBFrom.sizePolicy().hasHeightForWidth())
        self.cmbMKBFrom.setSizePolicy(sizePolicy)
        self.cmbMKBFrom.setObjectName(_fromUtf8("cmbMKBFrom"))
        self.gridLayout.addWidget(self.cmbMKBFrom, 5, 3, 1, 1)
        self.lblMKBRange = QtGui.QLabel(ReportVisitsByClientTypeSetupDialog)
        self.lblMKBRange.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMKBRange.sizePolicy().hasHeightForWidth())
        self.lblMKBRange.setSizePolicy(sizePolicy)
        self.lblMKBRange.setObjectName(_fromUtf8("lblMKBRange"))
        self.gridLayout.addWidget(self.lblMKBRange, 5, 1, 1, 1)
        self.lblMKBFrom = QtGui.QLabel(ReportVisitsByClientTypeSetupDialog)
        self.lblMKBFrom.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMKBFrom.sizePolicy().hasHeightForWidth())
        self.lblMKBFrom.setSizePolicy(sizePolicy)
        self.lblMKBFrom.setObjectName(_fromUtf8("lblMKBFrom"))
        self.gridLayout.addWidget(self.lblMKBFrom, 5, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportVisitsByClientTypeSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 2, 1, 5)
        self.edtBegDate = QtGui.QDateEdit(ReportVisitsByClientTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 5)
        self.cmbIsPrimary = QtGui.QComboBox(ReportVisitsByClientTypeSetupDialog)
        self.cmbIsPrimary.setObjectName(_fromUtf8("cmbIsPrimary"))
        self.cmbIsPrimary.addItem(_fromUtf8(""))
        self.cmbIsPrimary.addItem(_fromUtf8(""))
        self.cmbIsPrimary.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbIsPrimary, 3, 2, 1, 5)
        self.chbMKBFilter = QtGui.QCheckBox(ReportVisitsByClientTypeSetupDialog)
        self.chbMKBFilter.setText(_fromUtf8(""))
        self.chbMKBFilter.setObjectName(_fromUtf8("chbMKBFilter"))
        self.gridLayout.addWidget(self.chbMKBFilter, 5, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 4, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(ReportVisitsByClientTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOrgStructure.sizePolicy().hasHeightForWidth())
        self.lblOrgStructure.setSizePolicy(sizePolicy)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 4, 0, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(ReportVisitsByClientTypeSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 4, 2, 1, 5)
        self.lblPrimaryStatus = QtGui.QLabel(ReportVisitsByClientTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPrimaryStatus.sizePolicy().hasHeightForWidth())
        self.lblPrimaryStatus.setSizePolicy(sizePolicy)
        self.lblPrimaryStatus.setObjectName(_fromUtf8("lblPrimaryStatus"))
        self.gridLayout.addWidget(self.lblPrimaryStatus, 3, 0, 1, 2)
        self.edtEndDate = QtGui.QDateEdit(ReportVisitsByClientTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 2, 1, 5)
        self.cmbMKBTo = CICDCodeEditEx(ReportVisitsByClientTypeSetupDialog)
        self.cmbMKBTo.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbMKBTo.sizePolicy().hasHeightForWidth())
        self.cmbMKBTo.setSizePolicy(sizePolicy)
        self.cmbMKBTo.setObjectName(_fromUtf8("cmbMKBTo"))
        self.gridLayout.addWidget(self.cmbMKBTo, 5, 6, 1, 1)
        self.cmbEventType = CRBComboBox(ReportVisitsByClientTypeSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbEventType.sizePolicy().hasHeightForWidth())
        self.cmbEventType.setSizePolicy(sizePolicy)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 2, 2, 1, 5)
        self.cmbCitizen = QtGui.QComboBox(ReportVisitsByClientTypeSetupDialog)
        self.cmbCitizen.setObjectName(_fromUtf8("cmbCitizen"))
        self.cmbCitizen.addItem(_fromUtf8(""))
        self.cmbCitizen.addItem(_fromUtf8(""))
        self.cmbCitizen.addItem(_fromUtf8(""))
        self.cmbCitizen.addItem(_fromUtf8(""))
        self.cmbCitizen.addItem(_fromUtf8(""))
        self.cmbCitizen.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbCitizen, 6, 2, 1, 5)
        self.lblCitizen.setBuddy(self.cmbOrgStructure)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblMKBRange.setBuddy(self.cmbOrgStructure)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblPrimaryStatus.setBuddy(self.cmbEventType)

        self.retranslateUi(ReportVisitsByClientTypeSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportVisitsByClientTypeSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportVisitsByClientTypeSetupDialog.reject)
        QtCore.QObject.connect(self.chbMKBFilter, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblMKBRange.setEnabled)
        QtCore.QObject.connect(self.chbMKBFilter, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblMKBFrom.setEnabled)
        QtCore.QObject.connect(self.chbMKBFilter, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblMKBTo.setEnabled)
        QtCore.QObject.connect(self.chbMKBFilter, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbMKBFrom.setEnabled)
        QtCore.QObject.connect(self.chbMKBFilter, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbMKBTo.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ReportVisitsByClientTypeSetupDialog)
        ReportVisitsByClientTypeSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportVisitsByClientTypeSetupDialog.setTabOrder(self.edtEndDate, self.cmbEventType)
        ReportVisitsByClientTypeSetupDialog.setTabOrder(self.cmbEventType, self.cmbOrgStructure)

    def retranslateUi(self, ReportVisitsByClientTypeSetupDialog):
        ReportVisitsByClientTypeSetupDialog.setWindowTitle(_translate("ReportVisitsByClientTypeSetupDialog", "параметры отчёта", None))
        self.lblCitizen.setText(_translate("ReportVisitsByClientTypeSetupDialog", "&Житель", None))
        self.lblBegDate.setText(_translate("ReportVisitsByClientTypeSetupDialog", "Дата &начала периода", None))
        self.lblMKBTo.setText(_translate("ReportVisitsByClientTypeSetupDialog", "по", None))
        self.lblEventType.setText(_translate("ReportVisitsByClientTypeSetupDialog", "&Тип обращения", None))
        self.lblEndDate.setText(_translate("ReportVisitsByClientTypeSetupDialog", "Дата &окончания периода", None))
        self.lblMKBRange.setText(_translate("ReportVisitsByClientTypeSetupDialog", "&Диапазон диагнозов:", None))
        self.lblMKBFrom.setText(_translate("ReportVisitsByClientTypeSetupDialog", "с", None))
        self.cmbIsPrimary.setItemText(0, _translate("ReportVisitsByClientTypeSetupDialog", "Не заполнять", None))
        self.cmbIsPrimary.setItemText(1, _translate("ReportVisitsByClientTypeSetupDialog", "Первичное", None))
        self.cmbIsPrimary.setItemText(2, _translate("ReportVisitsByClientTypeSetupDialog", "Повторное", None))
        self.lblOrgStructure.setText(_translate("ReportVisitsByClientTypeSetupDialog", "&Подразделение", None))
        self.lblPrimaryStatus.setText(_translate("ReportVisitsByClientTypeSetupDialog", "&Вид обращения", None))
        self.cmbCitizen.setItemText(0, _translate("ReportVisitsByClientTypeSetupDialog", "Не заполнять", None))
        self.cmbCitizen.setItemText(1, _translate("ReportVisitsByClientTypeSetupDialog", "Житель Санкт-Петербурга", None))
        self.cmbCitizen.setItemText(2, _translate("ReportVisitsByClientTypeSetupDialog", "Житель Лен. области", None))
        self.cmbCitizen.setItemText(3, _translate("ReportVisitsByClientTypeSetupDialog", "Иногородний житель", None))
        self.cmbCitizen.setItemText(4, _translate("ReportVisitsByClientTypeSetupDialog", "Иностранец", None))
        self.cmbCitizen.setItemText(5, _translate("ReportVisitsByClientTypeSetupDialog", "Сельский житель", None))

from library.crbcombobox import CRBComboBox
from library.ICDCodeEdit import CICDCodeEditEx
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
