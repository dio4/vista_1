# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReferralEditDialog.ui'
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

class Ui_EdtReferralDialog(object):
    def setupUi(self, EdtReferralDialog):
        EdtReferralDialog.setObjectName(_fromUtf8("EdtReferralDialog"))
        EdtReferralDialog.resize(248, 504)
        self.gridLayout = QtGui.QGridLayout(EdtReferralDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbSpeciality = CRBComboBox(EdtReferralDialog)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 19, 0, 1, 2)
        self.cmbReferralType = CRBComboBox(EdtReferralDialog)
        self.cmbReferralType.setEnabled(False)
        self.cmbReferralType.setObjectName(_fromUtf8("cmbReferralType"))
        self.gridLayout.addWidget(self.cmbReferralType, 1, 0, 1, 2)
        self.lblReferralType = QtGui.QLabel(EdtReferralDialog)
        self.lblReferralType.setObjectName(_fromUtf8("lblReferralType"))
        self.gridLayout.addWidget(self.lblReferralType, 0, 0, 1, 1)
        self.lblReferralNumber = QtGui.QLabel(EdtReferralDialog)
        self.lblReferralNumber.setObjectName(_fromUtf8("lblReferralNumber"))
        self.gridLayout.addWidget(self.lblReferralNumber, 2, 0, 1, 1)
        self.edtReferralNumber = QtGui.QLineEdit(EdtReferralDialog)
        self.edtReferralNumber.setObjectName(_fromUtf8("edtReferralNumber"))
        self.gridLayout.addWidget(self.edtReferralNumber, 3, 0, 1, 2)
        self.lblReferralDate = QtGui.QLabel(EdtReferralDialog)
        self.lblReferralDate.setObjectName(_fromUtf8("lblReferralDate"))
        self.gridLayout.addWidget(self.lblReferralDate, 4, 0, 1, 1)
        self.edtReferralDate = QtGui.QDateEdit(EdtReferralDialog)
        self.edtReferralDate.setObjectName(_fromUtf8("edtReferralDate"))
        self.gridLayout.addWidget(self.edtReferralDate, 4, 1, 1, 1)
        self.lblReferralHospDate = QtGui.QLabel(EdtReferralDialog)
        self.lblReferralHospDate.setObjectName(_fromUtf8("lblReferralHospDate"))
        self.gridLayout.addWidget(self.lblReferralHospDate, 5, 0, 1, 1)
        self.edtReferralPlanedDate = QtGui.QDateEdit(EdtReferralDialog)
        self.edtReferralPlanedDate.setObjectName(_fromUtf8("edtReferralPlanedDate"))
        self.gridLayout.addWidget(self.edtReferralPlanedDate, 5, 1, 1, 1)
        self.lblRelegateMO = QtGui.QLabel(EdtReferralDialog)
        self.lblRelegateMO.setObjectName(_fromUtf8("lblRelegateMO"))
        self.gridLayout.addWidget(self.lblRelegateMO, 6, 0, 1, 1)
        self.cmbRelegateMo = COrgComboBox(EdtReferralDialog)
        self.cmbRelegateMo.setObjectName(_fromUtf8("cmbRelegateMo"))
        self.gridLayout.addWidget(self.cmbRelegateMo, 7, 0, 1, 2)
        self.lblReferralMKB = QtGui.QLabel(EdtReferralDialog)
        self.lblReferralMKB.setObjectName(_fromUtf8("lblReferralMKB"))
        self.gridLayout.addWidget(self.lblReferralMKB, 8, 0, 1, 1)
        self.cmbReferralMKB = CICDCodeEditEx(EdtReferralDialog)
        self.cmbReferralMKB.setObjectName(_fromUtf8("cmbReferralMKB"))
        self.gridLayout.addWidget(self.cmbReferralMKB, 9, 0, 1, 2)
        self.lblClinicType = QtGui.QLabel(EdtReferralDialog)
        self.lblClinicType.setObjectName(_fromUtf8("lblClinicType"))
        self.gridLayout.addWidget(self.lblClinicType, 10, 0, 1, 1)
        self.cmbClinicType = QtGui.QComboBox(EdtReferralDialog)
        self.cmbClinicType.setObjectName(_fromUtf8("cmbClinicType"))
        self.cmbClinicType.addItem(_fromUtf8(""))
        self.cmbClinicType.addItem(_fromUtf8(""))
        self.cmbClinicType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbClinicType, 11, 0, 1, 2)
        self.lblReferralSpeciality = QtGui.QLabel(EdtReferralDialog)
        self.lblReferralSpeciality.setObjectName(_fromUtf8("lblReferralSpeciality"))
        self.gridLayout.addWidget(self.lblReferralSpeciality, 18, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(EdtReferralDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 20, 0, 1, 2)
        self.lblPerson = QtGui.QLabel(EdtReferralDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 12, 0, 1, 1)
        self.lblOrgStructureProfile = QtGui.QLabel(EdtReferralDialog)
        self.lblOrgStructureProfile.setObjectName(_fromUtf8("lblOrgStructureProfile"))
        self.gridLayout.addWidget(self.lblOrgStructureProfile, 16, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(EdtReferralDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 13, 0, 1, 2)
        self.lblBedProfile = QtGui.QLabel(EdtReferralDialog)
        self.lblBedProfile.setObjectName(_fromUtf8("lblBedProfile"))
        self.gridLayout.addWidget(self.lblBedProfile, 14, 0, 1, 1)
        self.cmbBedProfile = CRBComboBox(EdtReferralDialog)
        self.cmbBedProfile.setObjectName(_fromUtf8("cmbBedProfile"))
        self.gridLayout.addWidget(self.cmbBedProfile, 15, 0, 1, 2)
        self.cmbOrgStructure = CRBComboBox(EdtReferralDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 17, 0, 1, 2)

        self.retranslateUi(EdtReferralDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EdtReferralDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EdtReferralDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EdtReferralDialog)

    def retranslateUi(self, EdtReferralDialog):
        EdtReferralDialog.setWindowTitle(_translate("EdtReferralDialog", "Редактирования направления", None))
        self.lblReferralType.setText(_translate("EdtReferralDialog", "Тип направления:", None))
        self.lblReferralNumber.setText(_translate("EdtReferralDialog", "Номер направления:", None))
        self.lblReferralDate.setText(_translate("EdtReferralDialog", "Дата выдачи направления:", None))
        self.lblReferralHospDate.setText(_translate("EdtReferralDialog", "Планируемая дата:", None))
        self.lblRelegateMO.setText(_translate("EdtReferralDialog", "Направлен в МО:", None))
        self.lblReferralMKB.setText(_translate("EdtReferralDialog", "Код МКБ:", None))
        self.lblClinicType.setText(_translate("EdtReferralDialog", "Тип стационара:", None))
        self.cmbClinicType.setItemText(0, _translate("EdtReferralDialog", "не задано", None))
        self.cmbClinicType.setItemText(1, _translate("EdtReferralDialog", "стационар", None))
        self.cmbClinicType.setItemText(2, _translate("EdtReferralDialog", "дневной стационар", None))
        self.lblReferralSpeciality.setText(_translate("EdtReferralDialog", "Специальность:", None))
        self.lblPerson.setText(_translate("EdtReferralDialog", "Врач:", None))
        self.lblOrgStructureProfile.setText(_translate("EdtReferralDialog", "Профиль отделения:", None))
        self.lblBedProfile.setText(_translate("EdtReferralDialog", "Профиль койки:", None))

from Orgs.OrgComboBox import COrgComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.ICDCodeEdit import CICDCodeEditEx
from library.crbcombobox import CRBComboBox
