# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBActionTypeIncompatibilityEditor.ui'
#
# Created: Wed Dec 25 16:44:42 2013
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_ItemEditorDialog(object):
    def setupUi(self, ItemEditorDialog):
        ItemEditorDialog.setObjectName(_fromUtf8("ItemEditorDialog"))
        ItemEditorDialog.resize(492, 196)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.edtReason = QtGui.QTextEdit(ItemEditorDialog)
        self.edtReason.setObjectName(_fromUtf8("edtReason"))
        self.gridlayout.addWidget(self.edtReason, 2, 1, 1, 3)
        self.cmbSecondActionType = CActionTypeComboBox(ItemEditorDialog)
        self.cmbSecondActionType.setObjectName(_fromUtf8("cmbSecondActionType"))
        self.gridlayout.addWidget(self.cmbSecondActionType, 0, 3, 1, 1)
        self.cmbFirstActionType = CActionTypeComboBox(ItemEditorDialog)
        self.cmbFirstActionType.setObjectName(_fromUtf8("cmbFirstActionType"))
        self.gridlayout.addWidget(self.cmbFirstActionType, 0, 1, 1, 1)
        self.lblFirstActionType = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFirstActionType.sizePolicy().hasHeightForWidth())
        self.lblFirstActionType.setSizePolicy(sizePolicy)
        self.lblFirstActionType.setObjectName(_fromUtf8("lblFirstActionType"))
        self.gridlayout.addWidget(self.lblFirstActionType, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 4, 0, 1, 4)
        self.lblReason = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblReason.sizePolicy().hasHeightForWidth())
        self.lblReason.setSizePolicy(sizePolicy)
        self.lblReason.setObjectName(_fromUtf8("lblReason"))
        self.gridlayout.addWidget(self.lblReason, 2, 0, 1, 1)
        self.label = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QtCore.QSize(20, 16777215))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 0, 2, 1, 1)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.lblFirstActionType.setText(_translate("ItemEditorDialog", "Типы действия", None))
        self.lblReason.setText(_translate("ItemEditorDialog", "Последствия", None))
        self.label.setText(_translate("ItemEditorDialog", "-", None))

from Events.ActionTypeComboBox import CActionTypeComboBox
