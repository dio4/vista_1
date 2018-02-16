# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HospitalBedsLocationCardEditor.ui'
#
# Created: Wed Aug 13 18:09:22 2014
#      by: PyQt4 UI code generator 4.11
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

class Ui_HospitalBedsLocationCardEditor(object):
    def setupUi(self, HospitalBedsLocationCardEditor):
        HospitalBedsLocationCardEditor.setObjectName(_fromUtf8("HospitalBedsLocationCardEditor"))
        HospitalBedsLocationCardEditor.resize(411, 138)
        HospitalBedsLocationCardEditor.setSizeGripEnabled(False)
        self.gridLayout = QtGui.QGridLayout(HospitalBedsLocationCardEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbLocationCardType = CRBComboBox(HospitalBedsLocationCardEditor)
        self.cmbLocationCardType.setObjectName(_fromUtf8("cmbLocationCardType"))
        self.gridLayout.addWidget(self.cmbLocationCardType, 0, 1, 1, 1)
        self.lblLocationCardType = QtGui.QLabel(HospitalBedsLocationCardEditor)
        self.lblLocationCardType.setObjectName(_fromUtf8("lblLocationCardType"))
        self.gridLayout.addWidget(self.lblLocationCardType, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(HospitalBedsLocationCardEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.lblDateMoveCard = QtGui.QLabel(HospitalBedsLocationCardEditor)
        self.lblDateMoveCard.setObjectName(_fromUtf8("lblDateMoveCard"))
        self.gridLayout.addWidget(self.lblDateMoveCard, 1, 0, 1, 1)
        self.edtDateMoveCard = CDateEdit(HospitalBedsLocationCardEditor)
        self.edtDateMoveCard.setObjectName(_fromUtf8("edtDateMoveCard"))
        self.gridLayout.addWidget(self.edtDateMoveCard, 1, 1, 1, 1)
        self.lblDateReturnCard = QtGui.QLabel(HospitalBedsLocationCardEditor)
        self.lblDateReturnCard.setObjectName(_fromUtf8("lblDateReturnCard"))
        self.gridLayout.addWidget(self.lblDateReturnCard, 2, 0, 1, 1)
        self.edtDateReturnCard = CDateEdit(HospitalBedsLocationCardEditor)
        self.edtDateReturnCard.setObjectName(_fromUtf8("edtDateReturnCard"))
        self.gridLayout.addWidget(self.edtDateReturnCard, 2, 1, 1, 1)

        self.retranslateUi(HospitalBedsLocationCardEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), HospitalBedsLocationCardEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), HospitalBedsLocationCardEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(HospitalBedsLocationCardEditor)

    def retranslateUi(self, HospitalBedsLocationCardEditor):
        HospitalBedsLocationCardEditor.setWindowTitle(_translate("HospitalBedsLocationCardEditor", "Место нахождения истории болезни", None))
        self.lblLocationCardType.setText(_translate("HospitalBedsLocationCardEditor", "Место нахождения истории болезни", None))
        self.lblDateMoveCard.setText(_translate("HospitalBedsLocationCardEditor", "Дата перемещения истории болезни", None))
        self.lblDateReturnCard.setText(_translate("HospitalBedsLocationCardEditor", "Дата возврата истории болезни", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
