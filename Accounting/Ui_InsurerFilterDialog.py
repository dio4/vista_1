# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'InsurerFilterDialog.ui'
#
# Created: Fri Mar 20 17:26:50 2015
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

class Ui_InsurerFilterDialog(object):
    def setupUi(self, InsurerFilterDialog):
        InsurerFilterDialog.setObjectName(_fromUtf8("InsurerFilterDialog"))
        InsurerFilterDialog.resize(306, 101)
        self.gridLayout = QtGui.QGridLayout(InsurerFilterDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 212, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.cmbInsurerFilterDialog = CInsurerComboBox(InsurerFilterDialog)
        self.cmbInsurerFilterDialog.setObjectName(_fromUtf8("cmbInsurerFilterDialog"))
        self.gridLayout.addWidget(self.cmbInsurerFilterDialog, 0, 0, 1, 1)
        self.chkAssistent = QtGui.QCheckBox(InsurerFilterDialog)
        self.chkAssistent.setObjectName(_fromUtf8("chkAssistent"))
        self.gridLayout.addWidget(self.chkAssistent, 2, 0, 1, 1)
        self.bbxInsurerFilerDialog = QtGui.QDialogButtonBox(InsurerFilterDialog)
        self.bbxInsurerFilerDialog.setOrientation(QtCore.Qt.Horizontal)
        self.bbxInsurerFilerDialog.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.bbxInsurerFilerDialog.setObjectName(_fromUtf8("bbxInsurerFilerDialog"))
        self.gridLayout.addWidget(self.bbxInsurerFilerDialog, 3, 0, 1, 1)

        self.retranslateUi(InsurerFilterDialog)
        QtCore.QObject.connect(self.bbxInsurerFilerDialog, QtCore.SIGNAL(_fromUtf8("accepted()")), InsurerFilterDialog.accept)
        QtCore.QObject.connect(self.bbxInsurerFilerDialog, QtCore.SIGNAL(_fromUtf8("rejected()")), InsurerFilterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(InsurerFilterDialog)

    def retranslateUi(self, InsurerFilterDialog):
        InsurerFilterDialog.setWindowTitle(_translate("InsurerFilterDialog", "Выбор СМО", None))
        self.chkAssistent.setText(_translate("InsurerFilterDialog", "Выводить ассистента", None))

from Orgs.OrgComboBox import CInsurerComboBox
