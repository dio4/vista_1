# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportPreventiveExaminationsSetup.ui'
#
# Created: Mon Jul 14 20:42:15 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_ReportPreventiveExaminationsSetupDialog(object):
    def setupUi(self, ReportPreventiveExaminationsSetupDialog):
        ReportPreventiveExaminationsSetupDialog.setObjectName(_fromUtf8("ReportPreventiveExaminationsSetupDialog"))
        ReportPreventiveExaminationsSetupDialog.resize(320, 188)
        self.gridLayout = QtGui.QGridLayout(ReportPreventiveExaminationsSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbEventType = CRBComboBox(ReportPreventiveExaminationsSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 3, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportPreventiveExaminationsSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 3, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportPreventiveExaminationsSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.btnSelectWorkOrganisation = QtGui.QToolButton(ReportPreventiveExaminationsSetupDialog)
        self.btnSelectWorkOrganisation.setArrowType(QtCore.Qt.NoArrow)
        self.btnSelectWorkOrganisation.setObjectName(_fromUtf8("btnSelectWorkOrganisation"))
        self.gridLayout.addWidget(self.btnSelectWorkOrganisation, 2, 2, 1, 1)
        self.lblClientOrganisation = QtGui.QLabel(ReportPreventiveExaminationsSetupDialog)
        self.lblClientOrganisation.setObjectName(_fromUtf8("lblClientOrganisation"))
        self.gridLayout.addWidget(self.lblClientOrganisation, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportPreventiveExaminationsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 3)
        self.lblEndDate = QtGui.QLabel(ReportPreventiveExaminationsSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.cmbWorkOrganisation = COrgComboBox(ReportPreventiveExaminationsSetupDialog)
        self.cmbWorkOrganisation.setObjectName(_fromUtf8("cmbWorkOrganisation"))
        self.gridLayout.addWidget(self.cmbWorkOrganisation, 2, 1, 1, 1)
        self.edtBegDate = CDateEdit(ReportPreventiveExaminationsSetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.edtEndDate = CDateEdit(ReportPreventiveExaminationsSetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblClientOrganisation.setBuddy(self.cmbWorkOrganisation)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportPreventiveExaminationsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportPreventiveExaminationsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportPreventiveExaminationsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportPreventiveExaminationsSetupDialog)
        ReportPreventiveExaminationsSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportPreventiveExaminationsSetupDialog.setTabOrder(self.edtEndDate, self.cmbWorkOrganisation)
        ReportPreventiveExaminationsSetupDialog.setTabOrder(self.cmbWorkOrganisation, self.btnSelectWorkOrganisation)
        ReportPreventiveExaminationsSetupDialog.setTabOrder(self.btnSelectWorkOrganisation, self.cmbEventType)
        ReportPreventiveExaminationsSetupDialog.setTabOrder(self.cmbEventType, self.buttonBox)

    def retranslateUi(self, ReportPreventiveExaminationsSetupDialog):
        ReportPreventiveExaminationsSetupDialog.setWindowTitle(_translate("ReportPreventiveExaminationsSetupDialog", "Dialog", None))
        self.lblEventType.setText(_translate("ReportPreventiveExaminationsSetupDialog", "&Тип события", None))
        self.lblBegDate.setText(_translate("ReportPreventiveExaminationsSetupDialog", "Дата &начала периода", None))
        self.btnSelectWorkOrganisation.setText(_translate("ReportPreventiveExaminationsSetupDialog", "...", None))
        self.lblClientOrganisation.setText(_translate("ReportPreventiveExaminationsSetupDialog", "Место работы", None))
        self.lblEndDate.setText(_translate("ReportPreventiveExaminationsSetupDialog", "Дата &окончания периода", None))

from Orgs.OrgComboBox import COrgComboBox
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
