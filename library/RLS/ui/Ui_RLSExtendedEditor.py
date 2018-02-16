# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RLSExtendedEditor.ui'
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

class Ui_RLSExtendedEditor(object):
    def setupUi(self, RLSExtendedEditor):
        RLSExtendedEditor.setObjectName(_fromUtf8("RLSExtendedEditor"))
        RLSExtendedEditor.setWindowModality(QtCore.Qt.ApplicationModal)
        RLSExtendedEditor.resize(440, 280)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(RLSExtendedEditor.sizePolicy().hasHeightForWidth())
        RLSExtendedEditor.setSizePolicy(sizePolicy)
        self.gridLayout_2 = QtGui.QGridLayout(RLSExtendedEditor)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.llblAmount = QtGui.QLabel(RLSExtendedEditor)
        self.llblAmount.setObjectName(_fromUtf8("llblAmount"))
        self.gridLayout.addWidget(self.llblAmount, 2, 0, 1, 1)
        self.cmbRLS = CRLSComboBox(RLSExtendedEditor)
        self.cmbRLS.setObjectName(_fromUtf8("cmbRLS"))
        self.gridLayout.addWidget(self.cmbRLS, 0, 1, 1, 1)
        self.cmbForm = CRBComboBox(RLSExtendedEditor)
        self.cmbForm.setObjectName(_fromUtf8("cmbForm"))
        self.gridLayout.addWidget(self.cmbForm, 1, 1, 1, 1)
        self.lblRLS = QtGui.QLabel(RLSExtendedEditor)
        self.lblRLS.setObjectName(_fromUtf8("lblRLS"))
        self.gridLayout.addWidget(self.lblRLS, 0, 0, 1, 1)
        self.edtNote = QtGui.QTextEdit(RLSExtendedEditor)
        self.edtNote.setObjectName(_fromUtf8("edtNote"))
        self.gridLayout.addWidget(self.edtNote, 3, 1, 1, 1)
        self.lblNote = QtGui.QLabel(RLSExtendedEditor)
        self.lblNote.setObjectName(_fromUtf8("lblNote"))
        self.gridLayout.addWidget(self.lblNote, 3, 0, 1, 1)
        self.lblForm = QtGui.QLabel(RLSExtendedEditor)
        self.lblForm.setObjectName(_fromUtf8("lblForm"))
        self.gridLayout.addWidget(self.lblForm, 1, 0, 1, 1)
        self.edtAmount = QtGui.QLineEdit(RLSExtendedEditor)
        self.edtAmount.setCursorPosition(1)
        self.edtAmount.setObjectName(_fromUtf8("edtAmount"))
        self.gridLayout.addWidget(self.edtAmount, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RLSExtendedEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(RLSExtendedEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RLSExtendedEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RLSExtendedEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(RLSExtendedEditor)

    def retranslateUi(self, RLSExtendedEditor):
        RLSExtendedEditor.setWindowTitle(_translate("RLSExtendedEditor", "Dialog", None))
        self.llblAmount.setText(_translate("RLSExtendedEditor", "Дозировка", None))
        self.lblRLS.setText(_translate("RLSExtendedEditor", "Препарат", None))
        self.lblNote.setText(_translate("RLSExtendedEditor", "Примечание", None))
        self.lblForm.setText(_translate("RLSExtendedEditor", "Единица измерения", None))
        self.edtAmount.setText(_translate("RLSExtendedEditor", "0", None))

from library.RLS.RLSComboBox import CRLSComboBox
from library.crbcombobox import CRBComboBox
