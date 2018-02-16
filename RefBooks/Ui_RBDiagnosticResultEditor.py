# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBDiagnosticResultEditor.ui'
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
        ItemEditorDialog.resize(466, 474)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.chkFilterResults = QtGui.QCheckBox(ItemEditorDialog)
        self.chkFilterResults.setObjectName(_fromUtf8("chkFilterResults"))
        self.gridlayout.addWidget(self.chkFilterResults, 5, 0, 1, 2)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 4, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ItemEditorDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridlayout.addWidget(self.lblBegDate, 8, 0, 1, 1)
        self.label = QtGui.QLabel(ItemEditorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 0, 0, 1, 1)
        self.cmbEventPurpose = CRBComboBox(ItemEditorDialog)
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.gridlayout.addWidget(self.cmbEventPurpose, 0, 1, 1, 1)
        self.lblRBResult = QtGui.QLabel(ItemEditorDialog)
        self.lblRBResult.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblRBResult.setObjectName(_fromUtf8("lblRBResult"))
        self.gridlayout.addWidget(self.lblRBResult, 6, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setMaxLength(8)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 1, 1, 1, 1)
        self.lblRegionalCode = QtGui.QLabel(ItemEditorDialog)
        self.lblRegionalCode.setObjectName(_fromUtf8("lblRegionalCode"))
        self.gridlayout.addWidget(self.lblRegionalCode, 2, 0, 1, 1)
        self.lblFederalCode = QtGui.QLabel(ItemEditorDialog)
        self.lblFederalCode.setObjectName(_fromUtf8("lblFederalCode"))
        self.gridlayout.addWidget(self.lblFederalCode, 3, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 4, 1, 1, 1)
        self.edtRegionalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtRegionalCode.setMaxLength(8)
        self.edtRegionalCode.setObjectName(_fromUtf8("edtRegionalCode"))
        self.gridlayout.addWidget(self.edtRegionalCode, 2, 1, 1, 1)
        self.edtFederalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtFederalCode.setObjectName(_fromUtf8("edtFederalCode"))
        self.gridlayout.addWidget(self.edtFederalCode, 3, 1, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 1, 0, 1, 1)
        self.edtBegDate = CDateEdit(ItemEditorDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridlayout.addWidget(self.edtBegDate, 8, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 10, 0, 1, 2)
        self.edtEndDate = CDateEdit(ItemEditorDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridlayout.addWidget(self.edtEndDate, 9, 1, 1, 1)
        self.tblRBResult = CRBListBox(ItemEditorDialog)
        self.tblRBResult.setMinimumSize(QtCore.QSize(0, 150))
        self.tblRBResult.setObjectName(_fromUtf8("tblRBResult"))
        self.gridlayout.addWidget(self.tblRBResult, 6, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ItemEditorDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridlayout.addWidget(self.lblEndDate, 9, 0, 1, 1)
        self.lblName.setBuddy(self.edtName)
        self.label.setBuddy(self.cmbEventPurpose)
        self.lblRegionalCode.setBuddy(self.edtRegionalCode)
        self.lblFederalCode.setBuddy(self.edtFederalCode)
        self.lblCode.setBuddy(self.edtCode)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.cmbEventPurpose, self.edtCode)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtRegionalCode)
        ItemEditorDialog.setTabOrder(self.edtRegionalCode, self.edtFederalCode)
        ItemEditorDialog.setTabOrder(self.edtFederalCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.chkFilterResults.setText(_translate("ItemEditorDialog", "Фильтровать результат обращения", None))
        self.lblName.setText(_translate("ItemEditorDialog", "&Наименование", None))
        self.lblBegDate.setText(_translate("ItemEditorDialog", "Дата начала", None))
        self.label.setText(_translate("ItemEditorDialog", "&Цель визита", None))
        self.lblRBResult.setText(_translate("ItemEditorDialog", "Допустимые\n"
"результаты\n"
"обращения", None))
        self.lblRegionalCode.setText(_translate("ItemEditorDialog", "&Региональный код", None))
        self.lblFederalCode.setText(_translate("ItemEditorDialog", "&Федеральный код", None))
        self.lblCode.setText(_translate("ItemEditorDialog", "&Код", None))
        self.lblEndDate.setText(_translate("ItemEditorDialog", "Дата окончания", None))

from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
from library.crbcombobox import CRBComboBox
