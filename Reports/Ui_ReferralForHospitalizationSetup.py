# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReferralForHospitalizationSetup.ui'
#
# Created: Fri Jan 31 16:36:53 2014
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_ReferralForHospitalizationSetupDialog(object):
    def setupUi(self, ReferralForHospitalizationSetupDialog):
        ReferralForHospitalizationSetupDialog.setObjectName(_fromUtf8("ReferralForHospitalizationSetupDialog"))
        ReferralForHospitalizationSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReferralForHospitalizationSetupDialog.resize(293, 141)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReferralForHospitalizationSetupDialog.sizePolicy().hasHeightForWidth())
        ReferralForHospitalizationSetupDialog.setSizePolicy(sizePolicy)
        ReferralForHospitalizationSetupDialog.setSizeGripEnabled(True)
        self.formLayout = QtGui.QFormLayout(ReferralForHospitalizationSetupDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lblBegDate = QtGui.QLabel(ReferralForHospitalizationSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lblBegDate)
        self.edtBegDate = QtGui.QDateEdit(ReferralForHospitalizationSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtBegDate)
        self.lblEndDate = QtGui.QLabel(ReferralForHospitalizationSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lblEndDate)
        self.edtEndDate = QtGui.QDateEdit(ReferralForHospitalizationSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtEndDate)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(2, QtGui.QFormLayout.FieldRole, spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ReferralForHospitalizationSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(ReferralForHospitalizationSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReferralForHospitalizationSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReferralForHospitalizationSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReferralForHospitalizationSetupDialog)

    def retranslateUi(self, ReferralForHospitalizationSetupDialog):
        ReferralForHospitalizationSetupDialog.setWindowTitle(_translate("ReferralForHospitalizationSetupDialog", "параметры отчёта", None))
        self.lblBegDate.setText(_translate("ReferralForHospitalizationSetupDialog", "Дата начала периода", None))
        self.lblEndDate.setText(_translate("ReferralForHospitalizationSetupDialog", "Дата окончания периода", None))

