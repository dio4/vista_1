# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBDocumentTypeEditor.ui'
#
# Created: Wed Nov 18 15:39:15 2015
#      by: PyQt4 UI code generator 4.10.4
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
        ItemEditorDialog.resize(331, 221)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblFederalCode = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFederalCode.sizePolicy().hasHeightForWidth())
        self.lblFederalCode.setSizePolicy(sizePolicy)
        self.lblFederalCode.setObjectName(_fromUtf8("lblFederalCode"))
        self.gridlayout.addWidget(self.lblFederalCode, 1, 0, 1, 1)
        self.lblRegionalCode = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblRegionalCode.sizePolicy().hasHeightForWidth())
        self.lblRegionalCode.setSizePolicy(sizePolicy)
        self.lblRegionalCode.setObjectName(_fromUtf8("lblRegionalCode"))
        self.gridlayout.addWidget(self.lblRegionalCode, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 8, 0, 1, 1)
        self.chkDefault = QtGui.QCheckBox(ItemEditorDialog)
        self.chkDefault.setObjectName(_fromUtf8("chkDefault"))
        self.gridlayout.addWidget(self.chkDefault, 7, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 9, 0, 1, 3)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 3, 1, 1, 2)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 2)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblName.sizePolicy().hasHeightForWidth())
        self.lblName.setSizePolicy(sizePolicy)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 3, 0, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblCode.sizePolicy().hasHeightForWidth())
        self.lblCode.setSizePolicy(sizePolicy)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.lblFinance = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFinance.sizePolicy().hasHeightForWidth())
        self.lblFinance.setSizePolicy(sizePolicy)
        self.lblFinance.setObjectName(_fromUtf8("lblFinance"))
        self.gridlayout.addWidget(self.lblFinance, 4, 0, 1, 1)
        self.cmbGroup = CRBComboBox(ItemEditorDialog)
        self.cmbGroup.setObjectName(_fromUtf8("cmbGroup"))
        self.gridlayout.addWidget(self.cmbGroup, 4, 1, 1, 2)
        self.label = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 5, 0, 1, 1)
        self.cmbSerialFormat = QtGui.QComboBox(ItemEditorDialog)
        self.cmbSerialFormat.setObjectName(_fromUtf8("cmbSerialFormat"))
        self.cmbSerialFormat.addItem(_fromUtf8(""))
        self.cmbSerialFormat.addItem(_fromUtf8(""))
        self.cmbSerialFormat.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbSerialFormat, 5, 1, 1, 2)
        self.edtFederalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtFederalCode.setObjectName(_fromUtf8("edtFederalCode"))
        self.gridlayout.addWidget(self.edtFederalCode, 1, 1, 1, 2)
        self.edtRegionalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtRegionalCode.setObjectName(_fromUtf8("edtRegionalCode"))
        self.gridlayout.addWidget(self.edtRegionalCode, 2, 1, 1, 2)
        self.chkForeigner = QtGui.QCheckBox(ItemEditorDialog)
        self.chkForeigner.setObjectName(_fromUtf8("chkForeigner"))
        self.gridlayout.addWidget(self.chkForeigner, 6, 0, 1, 3)
        self.lblFederalCode.setBuddy(self.edtFederalCode)
        self.lblRegionalCode.setBuddy(self.edtRegionalCode)
        self.lblName.setBuddy(self.edtName)
        self.lblCode.setBuddy(self.edtCode)
        self.lblFinance.setBuddy(self.cmbGroup)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtFederalCode)
        ItemEditorDialog.setTabOrder(self.edtFederalCode, self.edtRegionalCode)
        ItemEditorDialog.setTabOrder(self.edtRegionalCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.cmbGroup)
        ItemEditorDialog.setTabOrder(self.cmbGroup, self.cmbSerialFormat)
        ItemEditorDialog.setTabOrder(self.cmbSerialFormat, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.lblFederalCode.setText(_translate("ItemEditorDialog", "&Федеральный код", None))
        self.lblRegionalCode.setText(_translate("ItemEditorDialog", "&Региональный код", None))
        self.chkDefault.setText(_translate("ItemEditorDialog", "Документ по умолчанию", None))
        self.lblName.setText(_translate("ItemEditorDialog", "&Наименование", None))
        self.lblCode.setText(_translate("ItemEditorDialog", "&Код", None))
        self.lblFinance.setText(_translate("ItemEditorDialog", "&Группа документов", None))
        self.label.setText(_translate("ItemEditorDialog", "Формат серии", None))
        self.cmbSerialFormat.setItemText(0, _translate("ItemEditorDialog", "Произвольный", None))
        self.cmbSerialFormat.setItemText(1, _translate("ItemEditorDialog", "\"Римские цифры\" - \"Русские буквы\"", None))
        self.cmbSerialFormat.setItemText(2, _translate("ItemEditorDialog", "Цифры Цифры", None))
        self.chkForeigner.setText(_translate("ItemEditorDialog", "Иностранный документ или документ для иностранцев", None))

from library.crbcombobox import CRBComboBox
