# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TableEditorDialog.ui'
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

class Ui_TableDialog(object):
    def setupUi(self, TableDialog):
        TableDialog.setObjectName(_fromUtf8("TableDialog"))
        TableDialog.setEnabled(True)
        TableDialog.resize(410, 280)
        self.gridLayout = QtGui.QGridLayout(TableDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDescription = QtGui.QLabel(TableDialog)
        self.lblDescription.setObjectName(_fromUtf8("lblDescription"))
        self.gridLayout.addWidget(self.lblDescription, 6, 0, 1, 1)
        self.edtTable = QtGui.QLineEdit(TableDialog)
        self.edtTable.setObjectName(_fromUtf8("edtTable"))
        self.gridLayout.addWidget(self.edtTable, 4, 1, 1, 1)
        self.edtGroup = QtGui.QLineEdit(TableDialog)
        self.edtGroup.setObjectName(_fromUtf8("edtGroup"))
        self.gridLayout.addWidget(self.edtGroup, 7, 1, 1, 1)
        self.lblGroup = QtGui.QLabel(TableDialog)
        self.lblGroup.setObjectName(_fromUtf8("lblGroup"))
        self.gridLayout.addWidget(self.lblGroup, 7, 0, 1, 1)
        self.lblTable = QtGui.QLabel(TableDialog)
        self.lblTable.setObjectName(_fromUtf8("lblTable"))
        self.gridLayout.addWidget(self.lblTable, 4, 0, 1, 1)
        self.edtDescription = QtGui.QTextEdit(TableDialog)
        self.edtDescription.setObjectName(_fromUtf8("edtDescription"))
        self.gridLayout.addWidget(self.edtDescription, 6, 1, 1, 1)
        self.lblName = QtGui.QLabel(TableDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(TableDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 2)
        self.edtName = QtGui.QLineEdit(TableDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 0, 1, 1, 1)

        self.retranslateUi(TableDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TableDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TableDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TableDialog)

    def retranslateUi(self, TableDialog):
        TableDialog.setWindowTitle(_translate("TableDialog", "Dialog", None))
        self.lblDescription.setText(_translate("TableDialog", "Описание", None))
        self.lblGroup.setText(_translate("TableDialog", "Группа", None))
        self.lblTable.setText(_translate("TableDialog", "Таблица", None))
        self.lblName.setText(_translate("TableDialog", "Наименование", None))

