# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportMentalDisorderSetup.ui'
#
# Created: Tue Oct 29 13:47:51 2013
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

class Ui_ReportMentalDisorderSetupDialog(object):
    def setupUi(self, ReportMentalDisorderSetupDialog):
        ReportMentalDisorderSetupDialog.setObjectName(_fromUtf8("ReportMentalDisorderSetupDialog"))
        ReportMentalDisorderSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportMentalDisorderSetupDialog.resize(319, 341)
        ReportMentalDisorderSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportMentalDisorderSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbEventType = CRBComboBox(ReportMentalDisorderSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 3, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportMentalDisorderSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportMentalDisorderSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.cmbEventPurpose = CRBComboBox(ReportMentalDisorderSetupDialog)
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.gridLayout.addWidget(self.cmbEventPurpose, 2, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportMentalDisorderSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 3, 0, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(ReportMentalDisorderSetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lblSocStatusClass = QtGui.QLabel(ReportMentalDisorderSetupDialog)
        self.lblSocStatusClass.setObjectName(_fromUtf8("lblSocStatusClass"))
        self.gridLayout.addWidget(self.lblSocStatusClass, 5, 0, 1, 1)
        self.lblSocStatusType = QtGui.QLabel(ReportMentalDisorderSetupDialog)
        self.lblSocStatusType.setObjectName(_fromUtf8("lblSocStatusType"))
        self.gridLayout.addWidget(self.lblSocStatusType, 6, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 8, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportMentalDisorderSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)
        self.edtBegDate = QtGui.QDateEdit(ReportMentalDisorderSetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.cmbSocStatusClass = CSocStatusComboBox(ReportMentalDisorderSetupDialog)
        self.cmbSocStatusClass.setObjectName(_fromUtf8("cmbSocStatusClass"))
        self.gridLayout.addWidget(self.cmbSocStatusClass, 5, 1, 1, 1)
        self.cmbSocStatusType = CRBComboBox(ReportMentalDisorderSetupDialog)
        self.cmbSocStatusType.setObjectName(_fromUtf8("cmbSocStatusType"))
        self.gridLayout.addWidget(self.cmbSocStatusType, 6, 1, 1, 1)
        self.lblEventPurpose = QtGui.QLabel(ReportMentalDisorderSetupDialog)
        self.lblEventPurpose.setObjectName(_fromUtf8("lblEventPurpose"))
        self.gridLayout.addWidget(self.lblEventPurpose, 2, 0, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportMentalDisorderSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 4, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(61, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 2, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportMentalDisorderSetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbPerson, 4, 1, 1, 1)
        self.cmbOrganisation = CPolyclinicComboBox(ReportMentalDisorderSetupDialog)
        self.cmbOrganisation.setObjectName(_fromUtf8("cmbOrganisation"))
        self.gridLayout.addWidget(self.cmbOrganisation, 7, 1, 1, 1)
        self.lblOrganisation = QtGui.QLabel(ReportMentalDisorderSetupDialog)
        self.lblOrganisation.setObjectName(_fromUtf8("lblOrganisation"))
        self.gridLayout.addWidget(self.lblOrganisation, 7, 0, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblEventPurpose.setBuddy(self.cmbEventPurpose)
        self.lblPerson.setBuddy(self.cmbPerson)

        self.retranslateUi(ReportMentalDisorderSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportMentalDisorderSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportMentalDisorderSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportMentalDisorderSetupDialog)
        ReportMentalDisorderSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportMentalDisorderSetupDialog.setTabOrder(self.edtEndDate, self.buttonBox)

    def retranslateUi(self, ReportMentalDisorderSetupDialog):
        ReportMentalDisorderSetupDialog.setWindowTitle(_translate("ReportMentalDisorderSetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReportMentalDisorderSetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReportMentalDisorderSetupDialog", "Дата окончания периода", None))
        self.lblEventType.setText(_translate("ReportMentalDisorderSetupDialog", "&Тип обращения", None))
        self.lblSocStatusClass.setText(_translate("ReportMentalDisorderSetupDialog", "Класс соц.статуса", None))
        self.lblSocStatusType.setText(_translate("ReportMentalDisorderSetupDialog", "Тип соц.статуса", None))
        self.lblEventPurpose.setText(_translate("ReportMentalDisorderSetupDialog", "&Назначение обращения", None))
        self.lblPerson.setText(_translate("ReportMentalDisorderSetupDialog", "&Врач", None))
        self.cmbPerson.setItemText(0, _translate("ReportMentalDisorderSetupDialog", "Врач", None))
        self.lblOrganisation.setText(_translate("ReportMentalDisorderSetupDialog", "ЛПУ", None))

from Orgs.OrgComboBox import CPolyclinicComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from Registry.SocStatusComboBox import CSocStatusComboBox
