# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportFE5PSetup.ui'
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

class Ui_ReportFE5PSetupDialog(object):
    def setupUi(self, ReportFE5PSetupDialog):
        ReportFE5PSetupDialog.setObjectName(_fromUtf8("ReportFE5PSetupDialog"))
        ReportFE5PSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportFE5PSetupDialog.resize(543, 346)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportFE5PSetupDialog.sizePolicy().hasHeightForWidth())
        ReportFE5PSetupDialog.setSizePolicy(sizePolicy)
        ReportFE5PSetupDialog.setMinimumSize(QtCore.QSize(543, 346))
        ReportFE5PSetupDialog.setSizeGripEnabled(True)
        ReportFE5PSetupDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(ReportFE5PSetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(428, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 19, 1, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ReportFE5PSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 20, 1, 1, 3)
        self.cmbPayStatus = QtGui.QComboBox(ReportFE5PSetupDialog)
        self.cmbPayStatus.setEnabled(False)
        self.cmbPayStatus.setObjectName(_fromUtf8("cmbPayStatus"))
        self.gridLayout.addWidget(self.cmbPayStatus, 11, 2, 1, 2)
        self.lblFinance = QtGui.QLabel(ReportFE5PSetupDialog)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 7, 1, 1, 1)
        self.gbDateInterval = QtGui.QGroupBox(ReportFE5PSetupDialog)
        self.gbDateInterval.setObjectName(_fromUtf8("gbDateInterval"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gbDateInterval)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(78, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 1, 4, 1, 1)
        self.lblEndDate = QtGui.QLabel(self.gbDateInterval)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout_2.addWidget(self.lblEndDate, 3, 0, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 1, 2, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(78, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 3, 4, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem4, 3, 2, 1, 1)
        self.lblBegDate = QtGui.QLabel(self.gbDateInterval)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout_2.addWidget(self.lblBegDate, 1, 0, 1, 2)
        self.edtBegDate = CDateEdit(self.gbDateInterval)
        self.edtBegDate.setMinimumSize(QtCore.QSize(250, 0))
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout_2.addWidget(self.edtBegDate, 1, 3, 1, 1)
        self.edtEndDate = CDateEdit(self.gbDateInterval)
        self.edtEndDate.setMinimumSize(QtCore.QSize(250, 0))
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout_2.addWidget(self.edtEndDate, 3, 3, 1, 1)
        self.lblBegDate.raise_()
        self.edtBegDate.raise_()
        self.lblEndDate.raise_()
        self.edtEndDate.raise_()
        self.gridLayout.addWidget(self.gbDateInterval, 2, 1, 1, 2)
        self.lblOrgStructure = QtGui.QLabel(ReportFE5PSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 10, 1, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportFE5PSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 10, 2, 1, 2)
        self.cmbFinance = CRBComboBox(ReportFE5PSetupDialog)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 7, 2, 1, 2)
        self.lblAccountNumber = QtGui.QLabel(ReportFE5PSetupDialog)
        self.lblAccountNumber.setObjectName(_fromUtf8("lblAccountNumber"))
        self.gridLayout.addWidget(self.lblAccountNumber, 3, 1, 1, 1)
        self.chkPayStatus = QtGui.QCheckBox(ReportFE5PSetupDialog)
        self.chkPayStatus.setObjectName(_fromUtf8("chkPayStatus"))
        self.gridLayout.addWidget(self.chkPayStatus, 11, 1, 1, 1)
        self.edtAccountNumber = QtGui.QLineEdit(ReportFE5PSetupDialog)
        self.edtAccountNumber.setObjectName(_fromUtf8("edtAccountNumber"))
        self.gridLayout.addWidget(self.edtAccountNumber, 3, 2, 1, 1)
        self.label = QtGui.QLabel(ReportFE5PSetupDialog)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 1, 1, 2)

        self.retranslateUi(ReportFE5PSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportFE5PSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportFE5PSetupDialog.reject)
        QtCore.QObject.connect(self.chkPayStatus, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbPayStatus.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ReportFE5PSetupDialog)
        ReportFE5PSetupDialog.setTabOrder(self.cmbFinance, self.buttonBox)

    def retranslateUi(self, ReportFE5PSetupDialog):
        ReportFE5PSetupDialog.setWindowTitle(_translate("ReportFE5PSetupDialog", "параметры отчёта", None))
        self.lblFinance.setText(_translate("ReportFE5PSetupDialog", "Тип финанисирования", None))
        self.gbDateInterval.setTitle(_translate("ReportFE5PSetupDialog", "Реестры с расчетными датами:", None))
        self.lblEndDate.setText(_translate("ReportFE5PSetupDialog", "по", None))
        self.lblBegDate.setText(_translate("ReportFE5PSetupDialog", "c", None))
        self.lblOrgStructure.setText(_translate("ReportFE5PSetupDialog", "Подразделение", None))
        self.lblAccountNumber.setText(_translate("ReportFE5PSetupDialog", "Номера реестров через запятую: ", None))
        self.chkPayStatus.setText(_translate("ReportFE5PSetupDialog", "Тип реестра", None))
        self.label.setText(_translate("ReportFE5PSetupDialog", "Отчет строится по сформированным реестрам. Вы можете выбрать нужные для отчета реестры, указав период <u>или</u> перечислив номера нужных вам реестров.", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
