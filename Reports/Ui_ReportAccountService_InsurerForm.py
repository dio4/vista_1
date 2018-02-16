# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportAccountService_InsurerForm.ui'
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(400, 45)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setContentsMargins(9, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.chkWithout = QtGui.QCheckBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkWithout.sizePolicy().hasHeightForWidth())
        self.chkWithout.setSizePolicy(sizePolicy)
        self.chkWithout.setObjectName(_fromUtf8("chkWithout"))
        self.horizontalLayout.addWidget(self.chkWithout)
        self.cmbInsurer = CInsurerComboBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbInsurer.sizePolicy().hasHeightForWidth())
        self.cmbInsurer.setSizePolicy(sizePolicy)
        self.cmbInsurer.setObjectName(_fromUtf8("cmbInsurer"))
        self.horizontalLayout.addWidget(self.cmbInsurer)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.chkWithout.setText(_translate("Form", "Исключить", None))

from Orgs.OrgComboBox import CInsurerComboBox
