# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TestListDialog.ui'
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

class Ui_TestListDialog(object):
    def setupUi(self, TestListDialog):
        TestListDialog.setObjectName(_fromUtf8("TestListDialog"))
        TestListDialog.resize(636, 420)
        TestListDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(TestListDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(TestListDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 4, 0, 1, 2)
        self.chkGroup = QtGui.QCheckBox(TestListDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkGroup.sizePolicy().hasHeightForWidth())
        self.chkGroup.setSizePolicy(sizePolicy)
        self.chkGroup.setObjectName(_fromUtf8("chkGroup"))
        self.gridLayout.addWidget(self.chkGroup, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(TestListDialog)
        self.edtCode.setEnabled(False)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 1, 1, 1, 1)
        self.tblItems = CTableView(TestListDialog)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(TestListDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        self.cmbGroup = CRBComboBox(TestListDialog)
        self.cmbGroup.setEnabled(False)
        self.cmbGroup.setObjectName(_fromUtf8("cmbGroup"))
        self.gridLayout.addWidget(self.cmbGroup, 0, 1, 1, 1)
        self.chkCode = QtGui.QCheckBox(TestListDialog)
        self.chkCode.setObjectName(_fromUtf8("chkCode"))
        self.gridLayout.addWidget(self.chkCode, 1, 0, 1, 1)
        self.chkName = QtGui.QCheckBox(TestListDialog)
        self.chkName.setObjectName(_fromUtf8("chkName"))
        self.gridLayout.addWidget(self.chkName, 2, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(TestListDialog)
        self.edtName.setEnabled(False)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 2, 1, 1, 1)

        self.retranslateUi(TestListDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TestListDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TestListDialog.reject)
        QtCore.QObject.connect(self.chkGroup, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cmbGroup.setEnabled)
        QtCore.QObject.connect(self.chkCode, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.edtCode.setEnabled)
        QtCore.QObject.connect(self.chkName, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.edtName.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(TestListDialog)
        TestListDialog.setTabOrder(self.chkGroup, self.cmbGroup)
        TestListDialog.setTabOrder(self.cmbGroup, self.chkCode)
        TestListDialog.setTabOrder(self.chkCode, self.edtCode)
        TestListDialog.setTabOrder(self.edtCode, self.chkName)
        TestListDialog.setTabOrder(self.chkName, self.edtName)
        TestListDialog.setTabOrder(self.edtName, self.tblItems)
        TestListDialog.setTabOrder(self.tblItems, self.buttonBox)

    def retranslateUi(self, TestListDialog):
        TestListDialog.setWindowTitle(_translate("TestListDialog", "Dialog", None))
        self.label.setText(_translate("TestListDialog", "Всего", None))
        self.chkGroup.setText(_translate("TestListDialog", "Группа", None))
        self.chkCode.setText(_translate("TestListDialog", "Код", None))
        self.chkName.setText(_translate("TestListDialog", "Наименование", None))

from library.TableView import CTableView
from library.crbcombobox import CRBComboBox
