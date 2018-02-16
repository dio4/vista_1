# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportClinicalIssues.ui'
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(264, 191)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBeginDate = QtGui.QLabel(Dialog)
        self.lblBeginDate.setObjectName(_fromUtf8("lblBeginDate"))
        self.gridLayout.addWidget(self.lblBeginDate, 0, 0, 1, 1)
        self.edtBegDate = QtGui.QDateEdit(Dialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.lblEndDate = QtGui.QLabel(Dialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 0, 3, 1, 1)
        self.edtEndDate = QtGui.QDateEdit(Dialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 0, 4, 1, 1)
        self.lblorgStruct = QtGui.QLabel(Dialog)
        self.lblorgStruct.setObjectName(_fromUtf8("lblorgStruct"))
        self.gridLayout.addWidget(self.lblorgStruct, 1, 0, 1, 2)
        self.cmbOrgStruct = COrgStructureComboBox(Dialog)
        self.cmbOrgStruct.setObjectName(_fromUtf8("cmbOrgStruct"))
        self.gridLayout.addWidget(self.cmbOrgStruct, 1, 2, 1, 3)
        self.lblChiefResearcher = QtGui.QLabel(Dialog)
        self.lblChiefResearcher.setObjectName(_fromUtf8("lblChiefResearcher"))
        self.gridLayout.addWidget(self.lblChiefResearcher, 2, 0, 1, 3)
        self.cmbResearcher = CPersonComboBoxEx(Dialog)
        self.cmbResearcher.setObjectName(_fromUtf8("cmbResearcher"))
        self.gridLayout.addWidget(self.cmbResearcher, 2, 3, 1, 2)
        self.lblPartner = QtGui.QLabel(Dialog)
        self.lblPartner.setObjectName(_fromUtf8("lblPartner"))
        self.gridLayout.addWidget(self.lblPartner, 3, 0, 1, 2)
        self.cmbPartner = COrgComboBox(Dialog)
        self.cmbPartner.setObjectName(_fromUtf8("cmbPartner"))
        self.gridLayout.addWidget(self.cmbPartner, 3, 3, 1, 2)
        self.chkIsValid = QtGui.QCheckBox(Dialog)
        self.chkIsValid.setObjectName(_fromUtf8("chkIsValid"))
        self.gridLayout.addWidget(self.chkIsValid, 4, 0, 1, 3)
        self.chkIsEnrollment = QtGui.QCheckBox(Dialog)
        self.chkIsEnrollment.setObjectName(_fromUtf8("chkIsEnrollment"))
        self.gridLayout.addWidget(self.chkIsEnrollment, 5, 0, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 1, 1, 4)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.lblBeginDate.setText(_translate("Dialog", "С:", None))
        self.lblEndDate.setText(_translate("Dialog", "По:", None))
        self.lblorgStruct.setText(_translate("Dialog", "Подразделение:", None))
        self.lblChiefResearcher.setText(_translate("Dialog", "Главный исследователь:", None))
        self.lblPartner.setText(_translate("Dialog", "Контрагент:", None))
        self.chkIsValid.setText(_translate("Dialog", "Только действующие", None))
        self.chkIsEnrollment.setText(_translate("Dialog", "Открыт набор пациентов", None))

from Orgs.OrgComboBox import COrgComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
