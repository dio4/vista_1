# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HospitalizationTransferPage.ui'
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

class Ui_HospitalizationTransferPage(object):
    def setupUi(self, HospitalizationTransferPage):
        HospitalizationTransferPage.setObjectName(_fromUtf8("HospitalizationTransferPage"))
        HospitalizationTransferPage.resize(811, 448)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(HospitalizationTransferPage.sizePolicy().hasHeightForWidth())
        HospitalizationTransferPage.setSizePolicy(sizePolicy)
        HospitalizationTransferPage.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.gridLayout_5 = QtGui.QGridLayout(HospitalizationTransferPage)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.tblHospitalizationTransfer = CInDocTableView(HospitalizationTransferPage)
        self.tblHospitalizationTransfer.setObjectName(_fromUtf8("tblHospitalizationTransfer"))
        self.gridLayout_5.addWidget(self.tblHospitalizationTransfer, 0, 0, 1, 1)

        self.retranslateUi(HospitalizationTransferPage)
        QtCore.QMetaObject.connectSlotsByName(HospitalizationTransferPage)

    def retranslateUi(self, HospitalizationTransferPage):
        HospitalizationTransferPage.setWindowTitle(_translate("HospitalizationTransferPage", "Form", None))

from library.InDocTable import CInDocTableView
