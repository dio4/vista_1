# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RCConditionItemEditor.ui'
#
# Created: Tue Mar 22 10:45:28 2016
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_RCConditionItemEditorDialog(object):
    def setupUi(self, RCConditionItemEditorDialog):
        RCConditionItemEditorDialog.setObjectName(_fromUtf8("RCConditionItemEditorDialog"))
        RCConditionItemEditorDialog.setEnabled(True)
        RCConditionItemEditorDialog.resize(420, 263)
        RCConditionItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(RCConditionItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.cmbField = CRCFieldsComboBox(RCConditionItemEditorDialog)
        self.cmbField.setObjectName(_fromUtf8("cmbField"))
        self.gridlayout.addWidget(self.cmbField, 0, 1, 1, 1)
        self.cmbConditionType = CRBComboBox(RCConditionItemEditorDialog)
        self.cmbConditionType.setObjectName(_fromUtf8("cmbConditionType"))
        self.gridlayout.addWidget(self.cmbConditionType, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RCConditionItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 8, 0, 1, 2)
        self.lblField = QtGui.QLabel(RCConditionItemEditorDialog)
        self.lblField.setObjectName(_fromUtf8("lblField"))
        self.gridlayout.addWidget(self.lblField, 0, 0, 1, 1)
        self.lblConditionType = QtGui.QLabel(RCConditionItemEditorDialog)
        self.lblConditionType.setObjectName(_fromUtf8("lblConditionType"))
        self.gridlayout.addWidget(self.lblConditionType, 1, 0, 1, 1)
        self.lblValue = QtGui.QLabel(RCConditionItemEditorDialog)
        self.lblValue.setObjectName(_fromUtf8("lblValue"))
        self.gridlayout.addWidget(self.lblValue, 3, 0, 1, 1)
        self.cmbValueType = CRBComboBox(RCConditionItemEditorDialog)
        self.cmbValueType.setObjectName(_fromUtf8("cmbValueType"))
        self.gridlayout.addWidget(self.cmbValueType, 2, 1, 1, 1)
        self.lblValueType = QtGui.QLabel(RCConditionItemEditorDialog)
        self.lblValueType.setObjectName(_fromUtf8("lblValueType"))
        self.gridlayout.addWidget(self.lblValueType, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(73, 41, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 7, 0, 1, 1)
        self.valueLayout = QtGui.QVBoxLayout()
        self.valueLayout.setObjectName(_fromUtf8("valueLayout"))
        self.edtValue = QtGui.QLineEdit(RCConditionItemEditorDialog)
        self.edtValue.setMinimumSize(QtCore.QSize(200, 0))
        self.edtValue.setObjectName(_fromUtf8("edtValue"))
        self.valueLayout.addWidget(self.edtValue)
        self.cmbValueField = CRCFieldsComboBox(RCConditionItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbValueField.sizePolicy().hasHeightForWidth())
        self.cmbValueField.setSizePolicy(sizePolicy)
        self.cmbValueField.setObjectName(_fromUtf8("cmbValueField"))
        self.valueLayout.addWidget(self.cmbValueField)
        self.cmbParams = CRCComboBox(RCConditionItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbParams.sizePolicy().hasHeightForWidth())
        self.cmbParams.setSizePolicy(sizePolicy)
        self.cmbParams.setObjectName(_fromUtf8("cmbParams"))
        self.valueLayout.addWidget(self.cmbParams)
        self.edtDate = QtGui.QDateEdit(RCConditionItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDate.sizePolicy().hasHeightForWidth())
        self.edtDate.setSizePolicy(sizePolicy)
        self.edtDate.setCalendarPopup(True)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.valueLayout.addWidget(self.edtDate)
        self.edtValueInt = QtGui.QSpinBox(RCConditionItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtValueInt.sizePolicy().hasHeightForWidth())
        self.edtValueInt.setSizePolicy(sizePolicy)
        self.edtValueInt.setMaximum(10000)
        self.edtValueInt.setObjectName(_fromUtf8("edtValueInt"))
        self.valueLayout.addWidget(self.edtValueInt)
        self.edtValueDouble = QtGui.QDoubleSpinBox(RCConditionItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtValueDouble.sizePolicy().hasHeightForWidth())
        self.edtValueDouble.setSizePolicy(sizePolicy)
        self.edtValueDouble.setObjectName(_fromUtf8("edtValueDouble"))
        self.valueLayout.addWidget(self.edtValueDouble)
        self.edtCustom = CRCFieldLineEdit(RCConditionItemEditorDialog)
        self.edtCustom.setObjectName(_fromUtf8("edtCustom"))
        self.valueLayout.addWidget(self.edtCustom)
        self.gridlayout.addLayout(self.valueLayout, 3, 1, 1, 1)
        self.lblValue.setBuddy(self.edtValue)

        self.retranslateUi(RCConditionItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RCConditionItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RCConditionItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RCConditionItemEditorDialog)

    def retranslateUi(self, RCConditionItemEditorDialog):
        RCConditionItemEditorDialog.setWindowTitle(_translate("RCConditionItemEditorDialog", "ChangeMe!", None))
        self.lblField.setText(_translate("RCConditionItemEditorDialog", "Поле", None))
        self.lblConditionType.setText(_translate("RCConditionItemEditorDialog", "Тип условия", None))
        self.lblValue.setText(_translate("RCConditionItemEditorDialog", "Значение", None))
        self.lblValueType.setText(_translate("RCConditionItemEditorDialog", "Тип Значения", None))

from Reports.ReportsConstructor.RCComboBox import CRCComboBox, CRCFieldsComboBox
from Reports.ReportsConstructor.RCLineEdit import CRCFieldLineEdit
from library.crbcombobox import CRBComboBox
