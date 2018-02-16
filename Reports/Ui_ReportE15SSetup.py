# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportE15SSetup.ui'
#
# Created: Mon Oct 26 14:18:25 2015
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

class Ui_ReportE15SSetupDialog(object):
    def setupUi(self, ReportE15SSetupDialog):
        ReportE15SSetupDialog.setObjectName(_fromUtf8("ReportE15SSetupDialog"))
        ReportE15SSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportE15SSetupDialog.resize(397, 207)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportE15SSetupDialog.sizePolicy().hasHeightForWidth())
        ReportE15SSetupDialog.setSizePolicy(sizePolicy)
        ReportE15SSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportE15SSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ReportE15SSetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cmbAge = QtGui.QComboBox(ReportE15SSetupDialog)
        self.cmbAge.setObjectName(_fromUtf8("cmbAge"))
        self.cmbAge.addItem(_fromUtf8(""))
        self.cmbAge.addItem(_fromUtf8(""))
        self.cmbAge.addItem(_fromUtf8(""))
        self.cmbAge.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbAge, 6, 1, 1, 1)
        self.lblFinance = QtGui.QLabel(ReportE15SSetupDialog)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridLayout.addWidget(self.lblFinance, 4, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportE15SSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 1, 1, 1)
        self.lblOrgStruct = QtGui.QLabel(ReportE15SSetupDialog)
        self.lblOrgStruct.setObjectName(_fromUtf8("lblOrgStruct"))
        self.gridLayout.addWidget(self.lblOrgStruct, 3, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportE15SSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 1, 0, 1, 1)
        self.cmbFinance = CRBComboBox(ReportE15SSetupDialog)
        self.cmbFinance.setObjectName(_fromUtf8("cmbFinance"))
        self.gridLayout.addWidget(self.cmbFinance, 4, 1, 1, 1)
        self.edtBegDate = CDateEdit(ReportE15SSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportE15SSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportE15SSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportE15SSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 2)
        self.lblAge = QtGui.QLabel(ReportE15SSetupDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout.addWidget(self.lblAge, 6, 0, 1, 1)

        self.retranslateUi(ReportE15SSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportE15SSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportE15SSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportE15SSetupDialog)

    def retranslateUi(self, ReportE15SSetupDialog):
        ReportE15SSetupDialog.setWindowTitle(_translate("ReportE15SSetupDialog", "параметры отчёта", None))
        self.label.setText(_translate("ReportE15SSetupDialog", "Расчетная дата реестра:", None))
        self.cmbAge.setItemText(0, _translate("ReportE15SSetupDialog", "все", None))
        self.cmbAge.setItemText(1, _translate("ReportE15SSetupDialog", "дети", None))
        self.cmbAge.setItemText(2, _translate("ReportE15SSetupDialog", "взрослые", None))
        self.cmbAge.setItemText(3, _translate("ReportE15SSetupDialog", "лица старше трудоспособного возраста", None))
        self.lblFinance.setText(_translate("ReportE15SSetupDialog", "Тип финансирования", None))
        self.lblOrgStruct.setText(_translate("ReportE15SSetupDialog", "Подразделение", None))
        self.lblBegDate.setText(_translate("ReportE15SSetupDialog", "c", None))
        self.lblEndDate.setText(_translate("ReportE15SSetupDialog", "по", None))
        self.lblAge.setText(_translate("ReportE15SSetupDialog", "Возрастная категория", None))

from library.crbcombobox import CRBComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
