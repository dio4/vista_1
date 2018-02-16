# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBActionTypeSimilarityEditor.ui'
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

class Ui_ItemEditorDialog(object):
    def setupUi(self, ItemEditorDialog):
        ItemEditorDialog.setObjectName(_fromUtf8("ItemEditorDialog"))
        ItemEditorDialog.resize(492, 196)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 4, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 3, 1, 1, 1)
        self.lblSimilarityType = QtGui.QLabel(ItemEditorDialog)
        self.lblSimilarityType.setObjectName(_fromUtf8("lblSimilarityType"))
        self.gridlayout.addWidget(self.lblSimilarityType, 2, 0, 1, 1)
        self.grbSecondAT = QtGui.QGroupBox(ItemEditorDialog)
        self.grbSecondAT.setObjectName(_fromUtf8("grbSecondAT"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.grbSecondAT)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lblSecondAT = QtGui.QLabel(self.grbSecondAT)
        self.lblSecondAT.setObjectName(_fromUtf8("lblSecondAT"))
        self.horizontalLayout_2.addWidget(self.lblSecondAT)
        spacerItem1 = QtGui.QSpacerItem(322, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.btnSecondAT = QtGui.QPushButton(self.grbSecondAT)
        self.btnSecondAT.setObjectName(_fromUtf8("btnSecondAT"))
        self.horizontalLayout_2.addWidget(self.btnSecondAT)
        self.gridlayout.addWidget(self.grbSecondAT, 1, 0, 1, 3)
        self.grbFirstAT = QtGui.QGroupBox(ItemEditorDialog)
        self.grbFirstAT.setObjectName(_fromUtf8("grbFirstAT"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.grbFirstAT)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblFirstAT = QtGui.QLabel(self.grbFirstAT)
        self.lblFirstAT.setObjectName(_fromUtf8("lblFirstAT"))
        self.horizontalLayout.addWidget(self.lblFirstAT)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.btnFirstAT = QtGui.QPushButton(self.grbFirstAT)
        self.btnFirstAT.setObjectName(_fromUtf8("btnFirstAT"))
        self.horizontalLayout.addWidget(self.btnFirstAT)
        self.gridlayout.addWidget(self.grbFirstAT, 0, 0, 1, 3)
        self.cmbSimilarityType = QtGui.QComboBox(ItemEditorDialog)
        self.cmbSimilarityType.setObjectName(_fromUtf8("cmbSimilarityType"))
        self.cmbSimilarityType.addItem(_fromUtf8(""))
        self.cmbSimilarityType.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbSimilarityType, 2, 1, 1, 2)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.lblSimilarityType.setText(_translate("ItemEditorDialog", "Тип схожести", None))
        self.grbSecondAT.setTitle(_translate("ItemEditorDialog", "Тип действия 2", None))
        self.lblSecondAT.setText(_translate("ItemEditorDialog", "Не задано", None))
        self.btnSecondAT.setText(_translate("ItemEditorDialog", "Изменить", None))
        self.grbFirstAT.setTitle(_translate("ItemEditorDialog", "Тип действия 1", None))
        self.lblFirstAT.setText(_translate("ItemEditorDialog", "Не задано", None))
        self.btnFirstAT.setText(_translate("ItemEditorDialog", "Изменить", None))
        self.cmbSimilarityType.setItemText(0, _translate("ItemEditorDialog", "для копирования из предыдущих типов действий", None))
        self.cmbSimilarityType.setItemText(1, _translate("ItemEditorDialog", "для рекомендаций", None))

