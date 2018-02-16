# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBMealEditor.ui'
#
# Created: Thu Apr 02 19:58:29 2015
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

class Ui_RBMealEditorDialog(object):
    def setupUi(self, RBMealEditorDialog):
        RBMealEditorDialog.setObjectName(_fromUtf8("RBMealEditorDialog"))
        RBMealEditorDialog.resize(312, 145)
        RBMealEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(RBMealEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.edtCode = QtGui.QLineEdit(RBMealEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RBMealEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 7, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 6, 0, 1, 1)
        self.lblAmount = QtGui.QLabel(RBMealEditorDialog)
        self.lblAmount.setObjectName(_fromUtf8("lblAmount"))
        self.gridlayout.addWidget(self.lblAmount, 3, 0, 1, 1)
        self.edtAmount = QtGui.QLineEdit(RBMealEditorDialog)
        self.edtAmount.setObjectName(_fromUtf8("edtAmount"))
        self.gridlayout.addWidget(self.edtAmount, 3, 1, 1, 1)
        self.edtName = QtGui.QLineEdit(RBMealEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.lblName = QtGui.QLabel(RBMealEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.lblCode = QtGui.QLabel(RBMealEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.lblUnit = QtGui.QLabel(RBMealEditorDialog)
        self.lblUnit.setObjectName(_fromUtf8("lblUnit"))
        self.gridlayout.addWidget(self.lblUnit, 4, 0, 1, 1)
        self.edtUnit = QtGui.QLineEdit(RBMealEditorDialog)
        self.edtUnit.setObjectName(_fromUtf8("edtUnit"))
        self.gridlayout.addWidget(self.edtUnit, 4, 1, 1, 1)
        self.lblAmount.setBuddy(self.edtName)
        self.lblName.setBuddy(self.edtName)
        self.lblCode.setBuddy(self.edtCode)
        self.lblUnit.setBuddy(self.edtName)

        self.retranslateUi(RBMealEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBMealEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBMealEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RBMealEditorDialog)
        RBMealEditorDialog.setTabOrder(self.edtCode, self.edtName)
        RBMealEditorDialog.setTabOrder(self.edtName, self.buttonBox)

    def retranslateUi(self, RBMealEditorDialog):
        RBMealEditorDialog.setWindowTitle(_translate("RBMealEditorDialog", "ChangeMe!", None))
        self.lblAmount.setText(_translate("RBMealEditorDialog", "Количество", None))
        self.lblName.setText(_translate("RBMealEditorDialog", "Наименование", None))
        self.lblCode.setText(_translate("RBMealEditorDialog", "Код", None))
        self.lblUnit.setText(_translate("RBMealEditorDialog", "Единица измерения", None))

