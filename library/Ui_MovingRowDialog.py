# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MovingRowDialog.ui'
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

class Ui_MovingRowDialog(object):
    def setupUi(self, MovingRowDialog):
        MovingRowDialog.setObjectName(_fromUtf8("MovingRowDialog"))
        MovingRowDialog.resize(346, 84)
        MovingRowDialog.setMinimumSize(QtCore.QSize(346, 84))
        MovingRowDialog.setMaximumSize(QtCore.QSize(346, 84))
        self.gridLayout_2 = QtGui.QGridLayout(MovingRowDialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblAction = QtGui.QLabel(MovingRowDialog)
        self.lblAction.setObjectName(_fromUtf8("lblAction"))
        self.gridLayout_2.addWidget(self.lblAction, 0, 0, 1, 1)
        self.edtValue = QtGui.QSpinBox(MovingRowDialog)
        self.edtValue.setMinimum(1)
        self.edtValue.setObjectName(_fromUtf8("edtValue"))
        self.gridLayout_2.addWidget(self.edtValue, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(MovingRowDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 2)

        self.retranslateUi(MovingRowDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), MovingRowDialog.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MovingRowDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(MovingRowDialog)

    def retranslateUi(self, MovingRowDialog):
        MovingRowDialog.setWindowTitle(_translate("MovingRowDialog", "Dialog", None))
        self.lblAction.setText(_translate("MovingRowDialog", "Переместить %s на:", None))
        self.edtValue.setToolTip(_translate("MovingRowDialog", "Число позиций", None))

