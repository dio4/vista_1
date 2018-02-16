# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBCancellationReasonList.ui'
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

class Ui_CancellationReasonDialog(object):
    def setupUi(self, CancellationReasonDialog):
        CancellationReasonDialog.setObjectName(_fromUtf8("CancellationReasonDialog"))
        CancellationReasonDialog.resize(283, 68)
        self.gridLayout = QtGui.QGridLayout(CancellationReasonDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCancellationReason = QtGui.QLabel(CancellationReasonDialog)
        self.lblCancellationReason.setObjectName(_fromUtf8("lblCancellationReason"))
        self.gridLayout.addWidget(self.lblCancellationReason, 0, 0, 1, 1)
        self.cmbReason = CRBComboBox(CancellationReasonDialog)
        self.cmbReason.setObjectName(_fromUtf8("cmbReason"))
        self.gridLayout.addWidget(self.cmbReason, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(CancellationReasonDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)

        self.retranslateUi(CancellationReasonDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CancellationReasonDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CancellationReasonDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CancellationReasonDialog)

    def retranslateUi(self, CancellationReasonDialog):
        CancellationReasonDialog.setWindowTitle(_translate("CancellationReasonDialog", "Причина аннулирования", None))
        self.lblCancellationReason.setText(_translate("CancellationReasonDialog", "Причина аннулирования:", None))

from library.crbcombobox import CRBComboBox
