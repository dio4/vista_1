# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ParamEditorDialog.ui'
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

class Ui_ParamDialog(object):
    def setupUi(self, ParamDialog):
        ParamDialog.setObjectName(_fromUtf8("ParamDialog"))
        ParamDialog.setEnabled(True)
        ParamDialog.resize(476, 571)
        self.gridLayout = QtGui.QGridLayout(ParamDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupRb = QtGui.QGroupBox(ParamDialog)
        self.groupRb.setObjectName(_fromUtf8("groupRb"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupRb)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.edtRbTableName = QtGui.QLineEdit(self.groupRb)
        self.edtRbTableName.setObjectName(_fromUtf8("edtRbTableName"))
        self.gridLayout_3.addWidget(self.edtRbTableName, 0, 1, 1, 1)
        self.lblRbTableName = QtGui.QLabel(self.groupRb)
        self.lblRbTableName.setObjectName(_fromUtf8("lblRbTableName"))
        self.gridLayout_3.addWidget(self.lblRbTableName, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupRb, 1, 0, 1, 1)
        self.groupCmb = QtGui.QGroupBox(ParamDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupCmb.sizePolicy().hasHeightForWidth())
        self.groupCmb.setSizePolicy(sizePolicy)
        self.groupCmb.setObjectName(_fromUtf8("groupCmb"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupCmb)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tblCmbValue = CInDocTableView(self.groupCmb)
        self.tblCmbValue.setObjectName(_fromUtf8("tblCmbValue"))
        self.horizontalLayout.addWidget(self.tblCmbValue)
        self.gridLayout.addWidget(self.groupCmb, 2, 0, 1, 2)
        self.groupInfo = QtGui.QGroupBox(ParamDialog)
        self.groupInfo.setObjectName(_fromUtf8("groupInfo"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupInfo)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.edtName = QtGui.QLineEdit(self.groupInfo)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout_2.addWidget(self.edtName, 0, 2, 1, 1)
        self.lblName = QtGui.QLabel(self.groupInfo)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout_2.addWidget(self.lblName, 0, 0, 1, 1)
        self.lblText = QtGui.QLabel(self.groupInfo)
        self.lblText.setObjectName(_fromUtf8("lblText"))
        self.gridLayout_2.addWidget(self.lblText, 1, 0, 1, 1)
        self.lblCode = QtGui.QLabel(self.groupInfo)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout_2.addWidget(self.lblCode, 2, 0, 1, 1)
        self.edtText = QtGui.QLineEdit(self.groupInfo)
        self.edtText.setObjectName(_fromUtf8("edtText"))
        self.gridLayout_2.addWidget(self.edtText, 1, 2, 1, 1)
        self.lblValueType = QtGui.QLabel(self.groupInfo)
        self.lblValueType.setObjectName(_fromUtf8("lblValueType"))
        self.gridLayout_2.addWidget(self.lblValueType, 3, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(self.groupInfo)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout_2.addWidget(self.edtCode, 2, 2, 1, 1)
        self.cmbValueType = CRBComboBox(self.groupInfo)
        self.cmbValueType.setObjectName(_fromUtf8("cmbValueType"))
        self.gridLayout_2.addWidget(self.cmbValueType, 3, 2, 1, 1)
        self.lblParamType = QtGui.QLabel(self.groupInfo)
        self.lblParamType.setObjectName(_fromUtf8("lblParamType"))
        self.gridLayout_2.addWidget(self.lblParamType, 4, 0, 1, 1)
        self.cmbParamType = CRBComboBox(self.groupInfo)
        self.cmbParamType.setObjectName(_fromUtf8("cmbParamType"))
        self.gridLayout_2.addWidget(self.cmbParamType, 4, 2, 1, 1)
        self.gridLayout.addWidget(self.groupInfo, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ParamDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)

        self.retranslateUi(ParamDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ParamDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ParamDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ParamDialog)

    def retranslateUi(self, ParamDialog):
        ParamDialog.setWindowTitle(_translate("ParamDialog", "Dialog", None))
        self.groupRb.setTitle(_translate("ParamDialog", "Значение справочника", None))
        self.lblRbTableName.setText(_translate("ParamDialog", "Имя таблицы", None))
        self.groupCmb.setTitle(_translate("ParamDialog", "Значения комбобокса", None))
        self.groupInfo.setTitle(_translate("ParamDialog", "Основная информация", None))
        self.lblName.setText(_translate("ParamDialog", "Наименование", None))
        self.lblText.setText(_translate("ParamDialog", "Имя в интерфейсе", None))
        self.lblCode.setText(_translate("ParamDialog", "Код", None))
        self.lblValueType.setText(_translate("ParamDialog", "Тип значения", None))
        self.lblParamType.setText(_translate("ParamDialog", "Тип параметра", None))

from library.InDocTable import CInDocTableView
from library.crbcombobox import CRBComboBox
