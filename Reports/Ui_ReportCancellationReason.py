# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportCancellationReason.ui'
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
        Dialog.resize(307, 138)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblPeriod = QtGui.QLabel(Dialog)
        self.lblPeriod.setObjectName(_fromUtf8("lblPeriod"))
        self.gridLayout.addWidget(self.lblPeriod, 0, 0, 1, 2)
        self.lblDateFrom = QtGui.QLabel(Dialog)
        self.lblDateFrom.setObjectName(_fromUtf8("lblDateFrom"))
        self.gridLayout.addWidget(self.lblDateFrom, 1, 0, 1, 1)
        self.dtFrom = QtGui.QDateEdit(Dialog)
        self.dtFrom.setObjectName(_fromUtf8("dtFrom"))
        self.gridLayout.addWidget(self.dtFrom, 1, 1, 1, 2)
        self.lblDateTo = QtGui.QLabel(Dialog)
        self.lblDateTo.setObjectName(_fromUtf8("lblDateTo"))
        self.gridLayout.addWidget(self.lblDateTo, 1, 3, 1, 1)
        self.dtTo = QtGui.QDateEdit(Dialog)
        self.dtTo.setObjectName(_fromUtf8("dtTo"))
        self.gridLayout.addWidget(self.dtTo, 1, 4, 1, 1)
        self.lblOrgstructure = QtGui.QLabel(Dialog)
        self.lblOrgstructure.setObjectName(_fromUtf8("lblOrgstructure"))
        self.gridLayout.addWidget(self.lblOrgstructure, 2, 0, 1, 2)
        self.cmbOrgStruct = COrgStructureComboBox(Dialog)
        self.cmbOrgStruct.setObjectName(_fromUtf8("cmbOrgStruct"))
        self.gridLayout.addWidget(self.cmbOrgStruct, 2, 2, 1, 3)
        self.lblPerson = QtGui.QLabel(Dialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 3, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(Dialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 3, 2, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 5)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Отчет по причинам отказов в оказании услуг (предварительный)", None))
        self.lblPeriod.setText(_translate("Dialog", "Период:", None))
        self.lblDateFrom.setText(_translate("Dialog", "С:", None))
        self.lblDateTo.setText(_translate("Dialog", "До:", None))
        self.lblOrgstructure.setText(_translate("Dialog", "Подразделение:", None))
        self.lblPerson.setText(_translate("Dialog", "Врач:", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
