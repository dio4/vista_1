# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportAttachedClientSetup.ui'
#
# Created: Thu Feb 12 21:49:21 2015
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

class Ui_ReportAttachedClientSetup(object):
    def setupUi(self, ReportAttachedClientSetup):
        ReportAttachedClientSetup.setObjectName(_fromUtf8("ReportAttachedClientSetup"))
        ReportAttachedClientSetup.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportAttachedClientSetup.resize(283, 163)
        ReportAttachedClientSetup.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportAttachedClientSetup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtBegDate = CDateEdit(ReportAttachedClientSetup)
        self.edtBegDate.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(19, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAttachedClientSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(21, 21, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 7, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportAttachedClientSetup)
        self.edtEndDate.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblBegDae = QtGui.QLabel(ReportAttachedClientSetup)
        self.lblBegDae.setObjectName(_fromUtf8("lblBegDae"))
        self.gridLayout.addWidget(self.lblBegDae, 0, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportAttachedClientSetup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportAttachedClientSetup)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 1, 1, 2)
        self.lblSubdivision = QtGui.QLabel(ReportAttachedClientSetup)
        self.lblSubdivision.setObjectName(_fromUtf8("lblSubdivision"))
        self.gridLayout.addWidget(self.lblSubdivision, 3, 0, 1, 1)
        self.lblOrganisationAttachment = QtGui.QLabel(ReportAttachedClientSetup)
        self.lblOrganisationAttachment.setObjectName(_fromUtf8("lblOrganisationAttachment"))
        self.gridLayout.addWidget(self.lblOrganisationAttachment, 4, 0, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportAttachedClientSetup)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 6, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportAttachedClientSetup)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 6, 1, 1, 2)
        self.cmbOrganisationAttachment = CPolyclinicComboBox(ReportAttachedClientSetup)
        self.cmbOrganisationAttachment.setObjectName(_fromUtf8("cmbOrganisationAttachment"))
        self.gridLayout.addWidget(self.cmbOrganisationAttachment, 4, 1, 1, 2)
        self.lblBegDae.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblEventType.setBuddy(self.cmbEventType)

        self.retranslateUi(ReportAttachedClientSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAttachedClientSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAttachedClientSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAttachedClientSetup)
        ReportAttachedClientSetup.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportAttachedClientSetup.setTabOrder(self.edtEndDate, self.buttonBox)

    def retranslateUi(self, ReportAttachedClientSetup):
        ReportAttachedClientSetup.setWindowTitle(_translate("ReportAttachedClientSetup", "параметры отчёта", None))
        self.lblBegDae.setText(_translate("ReportAttachedClientSetup", "Дата начала", None))
        self.lblEndDate.setText(_translate("ReportAttachedClientSetup", "Дата окончания", None))
        self.lblSubdivision.setText(_translate("ReportAttachedClientSetup", "Подразделение", None))
        self.lblOrganisationAttachment.setText(_translate("ReportAttachedClientSetup", "ЛПУ прикрепления", None))
        self.lblEventType.setText(_translate("ReportAttachedClientSetup", "&Тип обращения", None))
        self.cmbEventType.setWhatsThis(_translate("ReportAttachedClientSetup", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))

from Orgs.OrgComboBox import CPolyclinicComboBox
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
