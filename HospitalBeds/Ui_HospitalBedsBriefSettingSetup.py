# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HospitalBedsBriefSettingSetup.ui'
#
# Created: Sat Apr 11 19:00:35 2015
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

class Ui_HospitalBedsBriefSettingSetupDialog(object):
    def setupUi(self, HospitalBedsBriefSettingSetupDialog):
        HospitalBedsBriefSettingSetupDialog.setObjectName(_fromUtf8("HospitalBedsBriefSettingSetupDialog"))
        HospitalBedsBriefSettingSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        HospitalBedsBriefSettingSetupDialog.resize(676, 465)
        HospitalBedsBriefSettingSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(HospitalBedsBriefSettingSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkNothing = QtGui.QCheckBox(HospitalBedsBriefSettingSetupDialog)
        self.chkNothing.setObjectName(_fromUtf8("chkNothing"))
        self.gridLayout.addWidget(self.chkNothing, 2, 0, 1, 2)
        self.chkAll = QtGui.QCheckBox(HospitalBedsBriefSettingSetupDialog)
        self.chkAll.setObjectName(_fromUtf8("chkAll"))
        self.gridLayout.addWidget(self.chkAll, 1, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(HospitalBedsBriefSettingSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        self.lstColumn = CRBListBox(HospitalBedsBriefSettingSetupDialog)
        self.lstColumn.setObjectName(_fromUtf8("lstColumn"))
        self.gridLayout.addWidget(self.lstColumn, 0, 0, 1, 2)
        self.lblFontSize = QtGui.QLabel(HospitalBedsBriefSettingSetupDialog)
        self.lblFontSize.setObjectName(_fromUtf8("lblFontSize"))
        self.gridLayout.addWidget(self.lblFontSize, 4, 0, 1, 1)
        self.edtFontSize = QtGui.QLineEdit(HospitalBedsBriefSettingSetupDialog)
        self.edtFontSize.setObjectName(_fromUtf8("edtFontSize"))
        self.gridLayout.addWidget(self.edtFontSize, 4, 1, 1, 1)

        self.retranslateUi(HospitalBedsBriefSettingSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), HospitalBedsBriefSettingSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), HospitalBedsBriefSettingSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(HospitalBedsBriefSettingSetupDialog)

    def retranslateUi(self, HospitalBedsBriefSettingSetupDialog):
        HospitalBedsBriefSettingSetupDialog.setWindowTitle(_translate("HospitalBedsBriefSettingSetupDialog", "параметры отчёта", None))
        self.chkNothing.setText(_translate("HospitalBedsBriefSettingSetupDialog", "Снять все выделения", None))
        self.chkAll.setText(_translate("HospitalBedsBriefSettingSetupDialog", "Выбрать всё", None))
        self.lblFontSize.setText(_translate("HospitalBedsBriefSettingSetupDialog", "Размер шрифта", None))

from library.RBListBox import CRBListBox
