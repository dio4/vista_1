# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FunctionEditorDialog.ui'
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

class Ui_FunctionDialog(object):
    def setupUi(self, FunctionDialog):
        FunctionDialog.setObjectName(_fromUtf8("FunctionDialog"))
        FunctionDialog.setEnabled(True)
        FunctionDialog.resize(413, 255)
        self.gridLayout = QtGui.QGridLayout(FunctionDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtFunction = QtGui.QLineEdit(FunctionDialog)
        self.edtFunction.setObjectName(_fromUtf8("edtFunction"))
        self.gridLayout.addWidget(self.edtFunction, 4, 2, 1, 1)
        self.lblFunction = QtGui.QLabel(FunctionDialog)
        self.lblFunction.setObjectName(_fromUtf8("lblFunction"))
        self.gridLayout.addWidget(self.lblFunction, 4, 0, 1, 1)
        self.edtDescription = QtGui.QTextEdit(FunctionDialog)
        self.edtDescription.setObjectName(_fromUtf8("edtDescription"))
        self.gridLayout.addWidget(self.edtDescription, 6, 2, 1, 1)
        self.lblName = QtGui.QLabel(FunctionDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 0, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(FunctionDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 0, 2, 1, 1)
        self.lblDescription = QtGui.QLabel(FunctionDialog)
        self.lblDescription.setObjectName(_fromUtf8("lblDescription"))
        self.gridLayout.addWidget(self.lblDescription, 6, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(FunctionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 3)
        self.chkHasSpace = QtGui.QCheckBox(FunctionDialog)
        self.chkHasSpace.setObjectName(_fromUtf8("chkHasSpace"))
        self.gridLayout.addWidget(self.chkHasSpace, 7, 0, 1, 3)

        self.retranslateUi(FunctionDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FunctionDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FunctionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FunctionDialog)

    def retranslateUi(self, FunctionDialog):
        FunctionDialog.setWindowTitle(_translate("FunctionDialog", "Dialog", None))
        self.lblFunction.setText(_translate("FunctionDialog", "Функция", None))
        self.lblName.setText(_translate("FunctionDialog", "Наименование", None))
        self.lblDescription.setText(_translate("FunctionDialog", "Описание", None))
        self.chkHasSpace.setText(_translate("FunctionDialog", "Вставить пробел после функции", None))

