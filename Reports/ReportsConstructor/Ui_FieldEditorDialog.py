# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FieldEditorDialog.ui'
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

class Ui_FieldDialog(object):
    def setupUi(self, FieldDialog):
        FieldDialog.setObjectName(_fromUtf8("FieldDialog"))
        FieldDialog.setEnabled(True)
        FieldDialog.resize(410, 315)
        self.gridLayout = QtGui.QGridLayout(FieldDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDescription = QtGui.QLabel(FieldDialog)
        self.lblDescription.setObjectName(_fromUtf8("lblDescription"))
        self.gridLayout.addWidget(self.lblDescription, 6, 0, 1, 1)
        self.cmbField = QtGui.QComboBox(FieldDialog)
        self.cmbField.setObjectName(_fromUtf8("cmbField"))
        self.gridLayout.addWidget(self.cmbField, 4, 1, 1, 1)
        self.lblField = QtGui.QLabel(FieldDialog)
        self.lblField.setObjectName(_fromUtf8("lblField"))
        self.gridLayout.addWidget(self.lblField, 4, 0, 1, 1)
        self.edtDescription = QtGui.QTextEdit(FieldDialog)
        self.edtDescription.setObjectName(_fromUtf8("edtDescription"))
        self.gridLayout.addWidget(self.edtDescription, 6, 1, 1, 1)
        self.groupReference = QtGui.QGroupBox(FieldDialog)
        self.groupReference.setObjectName(_fromUtf8("groupReference"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupReference)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.cmbRefField = QtGui.QComboBox(self.groupReference)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbRefField.sizePolicy().hasHeightForWidth())
        self.cmbRefField.setSizePolicy(sizePolicy)
        self.cmbRefField.setObjectName(_fromUtf8("cmbRefField"))
        self.gridLayout_2.addWidget(self.cmbRefField, 1, 1, 1, 1)
        self.cmbRefTable = QtGui.QComboBox(self.groupReference)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbRefTable.sizePolicy().hasHeightForWidth())
        self.cmbRefTable.setSizePolicy(sizePolicy)
        self.cmbRefTable.setObjectName(_fromUtf8("cmbRefTable"))
        self.gridLayout_2.addWidget(self.cmbRefTable, 0, 1, 1, 1)
        self.lblRefTable = QtGui.QLabel(self.groupReference)
        self.lblRefTable.setObjectName(_fromUtf8("lblRefTable"))
        self.gridLayout_2.addWidget(self.lblRefTable, 0, 0, 1, 1)
        self.lblRefField = QtGui.QLabel(self.groupReference)
        self.lblRefField.setObjectName(_fromUtf8("lblRefField"))
        self.gridLayout_2.addWidget(self.lblRefField, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupReference, 9, 0, 1, 2)
        self.chkHasReference = QtGui.QCheckBox(FieldDialog)
        self.chkHasReference.setObjectName(_fromUtf8("chkHasReference"))
        self.gridLayout.addWidget(self.chkHasReference, 8, 0, 1, 1)
        self.lblName = QtGui.QLabel(FieldDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(FieldDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 11, 0, 1, 2)
        self.edtName = QtGui.QLineEdit(FieldDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 0, 1, 1, 1)
        self.chkVisible = QtGui.QCheckBox(FieldDialog)
        self.chkVisible.setObjectName(_fromUtf8("chkVisible"))
        self.gridLayout.addWidget(self.chkVisible, 7, 0, 1, 2)

        self.retranslateUi(FieldDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FieldDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FieldDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FieldDialog)

    def retranslateUi(self, FieldDialog):
        FieldDialog.setWindowTitle(_translate("FieldDialog", "Dialog", None))
        self.lblDescription.setText(_translate("FieldDialog", "Описание", None))
        self.lblField.setText(_translate("FieldDialog", "Поле", None))
        self.groupReference.setTitle(_translate("FieldDialog", "Ссылка", None))
        self.lblRefTable.setText(_translate("FieldDialog", "Таблица", None))
        self.lblRefField.setText(_translate("FieldDialog", "Поле", None))
        self.chkHasReference.setText(_translate("FieldDialog", "Ссылка", None))
        self.lblName.setText(_translate("FieldDialog", "Наименование", None))
        self.chkVisible.setText(_translate("FieldDialog", "Видимость", None))

