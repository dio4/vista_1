# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportUnderageMedicalExaminationSetup.ui'
#
# Created: Tue May 06 16:51:01 2014
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

class Ui_ReportUnderageMedicalExaminationSetup(object):
    def setupUi(self, ReportUnderageMedicalExaminationSetup):
        ReportUnderageMedicalExaminationSetup.setObjectName(_fromUtf8("ReportUnderageMedicalExaminationSetup"))
        ReportUnderageMedicalExaminationSetup.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportUnderageMedicalExaminationSetup.resize(376, 200)
        ReportUnderageMedicalExaminationSetup.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportUnderageMedicalExaminationSetup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblSpeciality = QtGui.QLabel(ReportUnderageMedicalExaminationSetup)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout.addWidget(self.lblSpeciality, 3, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportUnderageMedicalExaminationSetup)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 2, 1, 1, 2)
        self.edtBegDate = CDateEdit(ReportUnderageMedicalExaminationSetup)
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
        self.buttonBox = QtGui.QDialogButtonBox(ReportUnderageMedicalExaminationSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(21, 21, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 7, 0, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportUnderageMedicalExaminationSetup)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 2, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportUnderageMedicalExaminationSetup)
        self.edtEndDate.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblBegDae = QtGui.QLabel(ReportUnderageMedicalExaminationSetup)
        self.lblBegDae.setObjectName(_fromUtf8("lblBegDae"))
        self.gridLayout.addWidget(self.lblBegDae, 0, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportUnderageMedicalExaminationSetup)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.chkAttendant = QtGui.QCheckBox(ReportUnderageMedicalExaminationSetup)
        self.chkAttendant.setObjectName(_fromUtf8("chkAttendant"))
        self.gridLayout.addWidget(self.chkAttendant, 4, 0, 1, 3)
        self.cmbOrgStructure = COrgStructureComboBox(ReportUnderageMedicalExaminationSetup)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 5, 1, 1, 2)
        self.lblSubdivision = QtGui.QLabel(ReportUnderageMedicalExaminationSetup)
        self.lblSubdivision.setObjectName(_fromUtf8("lblSubdivision"))
        self.gridLayout.addWidget(self.lblSubdivision, 5, 0, 1, 1)
        self.lblOrgStrucutreAttachType = QtGui.QLabel(ReportUnderageMedicalExaminationSetup)
        self.lblOrgStrucutreAttachType.setObjectName(_fromUtf8("lblOrgStrucutreAttachType"))
        self.gridLayout.addWidget(self.lblOrgStrucutreAttachType, 6, 0, 1, 1)
        self.cmbOrgStructureAttachType = COrgStructureComboBox(ReportUnderageMedicalExaminationSetup)
        self.cmbOrgStructureAttachType.setObjectName(_fromUtf8("cmbOrgStructureAttachType"))
        self.gridLayout.addWidget(self.cmbOrgStructureAttachType, 6, 1, 1, 2)
        self.cmbSpeciality = CRBComboBox(ReportUnderageMedicalExaminationSetup)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 3, 1, 1, 2)
        self.lblSpeciality.setBuddy(self.cmbEventType)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblBegDae.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportUnderageMedicalExaminationSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportUnderageMedicalExaminationSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportUnderageMedicalExaminationSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportUnderageMedicalExaminationSetup)
        ReportUnderageMedicalExaminationSetup.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportUnderageMedicalExaminationSetup.setTabOrder(self.edtEndDate, self.cmbEventType)
        ReportUnderageMedicalExaminationSetup.setTabOrder(self.cmbEventType, self.chkAttendant)
        ReportUnderageMedicalExaminationSetup.setTabOrder(self.chkAttendant, self.buttonBox)

    def retranslateUi(self, ReportUnderageMedicalExaminationSetup):
        ReportUnderageMedicalExaminationSetup.setWindowTitle(_translate("ReportUnderageMedicalExaminationSetup", "параметры отчёта", None))
        self.lblSpeciality.setText(_translate("ReportUnderageMedicalExaminationSetup", "Специальность", None))
        self.cmbEventType.setWhatsThis(_translate("ReportUnderageMedicalExaminationSetup", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.lblEventType.setText(_translate("ReportUnderageMedicalExaminationSetup", "&Тип обращения", None))
        self.lblBegDae.setText(_translate("ReportUnderageMedicalExaminationSetup", "Дата начала", None))
        self.lblEndDate.setText(_translate("ReportUnderageMedicalExaminationSetup", "Дата окончания", None))
        self.chkAttendant.setText(_translate("ReportUnderageMedicalExaminationSetup", "Учитывать сопутствующие", None))
        self.lblSubdivision.setText(_translate("ReportUnderageMedicalExaminationSetup", "Подразделение", None))
        self.lblOrgStrucutreAttachType.setText(_translate("ReportUnderageMedicalExaminationSetup", "Подразделение прикрепления", None))
        self.cmbSpeciality.setWhatsThis(_translate("ReportUnderageMedicalExaminationSetup", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
