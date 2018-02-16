# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBNetEditor.ui'
#
# Created: Tue Oct 22 16:40:07 2013
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_RBNetEditorDialog(object):
    def setupUi(self, RBNetEditorDialog):
        RBNetEditorDialog.setObjectName(_fromUtf8("RBNetEditorDialog"))
        RBNetEditorDialog.resize(458, 175)
        RBNetEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(RBNetEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblSex = QtGui.QLabel(RBNetEditorDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridlayout.addWidget(self.lblSex, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(221, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 1, 6, 1, 1)
        self.cmbBegAgeUnit = QtGui.QComboBox(RBNetEditorDialog)
        self.cmbBegAgeUnit.setObjectName(_fromUtf8("cmbBegAgeUnit"))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.setItemText(0, _fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbBegAgeUnit, 3, 1, 1, 1)
        self.cmbSex = QtGui.QComboBox(RBNetEditorDialog)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbSex, 2, 1, 1, 1)
        self.lblAge = QtGui.QLabel(RBNetEditorDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridlayout.addWidget(self.lblAge, 3, 0, 1, 1)
        self.edtBegAgeCount = QtGui.QLineEdit(RBNetEditorDialog)
        self.edtBegAgeCount.setMaxLength(3)
        self.edtBegAgeCount.setObjectName(_fromUtf8("edtBegAgeCount"))
        self.gridlayout.addWidget(self.edtBegAgeCount, 3, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(321, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 2, 2, 1, 5)
        spacerItem2 = QtGui.QSpacerItem(20, 71, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem2, 5, 0, 1, 1)
        self.edtEndAgeCount = QtGui.QLineEdit(RBNetEditorDialog)
        self.edtEndAgeCount.setMaxLength(3)
        self.edtEndAgeCount.setObjectName(_fromUtf8("edtEndAgeCount"))
        self.gridlayout.addWidget(self.edtEndAgeCount, 3, 5, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(151, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem3, 3, 6, 1, 1)
        self.lblAgeSep = QtGui.QLabel(RBNetEditorDialog)
        self.lblAgeSep.setObjectName(_fromUtf8("lblAgeSep"))
        self.gridlayout.addWidget(self.lblAgeSep, 3, 3, 1, 1)
        self.cmbEndAgeUnit = QtGui.QComboBox(RBNetEditorDialog)
        self.cmbEndAgeUnit.setObjectName(_fromUtf8("cmbEndAgeUnit"))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.setItemText(0, _fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbEndAgeUnit, 3, 4, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RBNetEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 6, 0, 1, 7)
        self.lblCode = QtGui.QLabel(RBNetEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(RBNetEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 5)
        spacerItem4 = QtGui.QSpacerItem(321, 22, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem4, 0, 6, 1, 1)
        self.lblName = QtGui.QLabel(RBNetEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(RBNetEditorDialog)
        self.edtName.setMinimumSize(QtCore.QSize(200, 0))
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 5)
        self.chkUseInCreateClients = QtGui.QCheckBox(RBNetEditorDialog)
        self.chkUseInCreateClients.setObjectName(_fromUtf8("chkUseInCreateClients"))
        self.gridlayout.addWidget(self.chkUseInCreateClients, 4, 1, 1, 5)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblAge.setBuddy(self.cmbBegAgeUnit)
        self.lblAgeSep.setBuddy(self.cmbEndAgeUnit)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(RBNetEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBNetEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBNetEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RBNetEditorDialog)
        RBNetEditorDialog.setTabOrder(self.edtCode, self.edtName)
        RBNetEditorDialog.setTabOrder(self.edtName, self.cmbSex)
        RBNetEditorDialog.setTabOrder(self.cmbSex, self.cmbBegAgeUnit)
        RBNetEditorDialog.setTabOrder(self.cmbBegAgeUnit, self.edtBegAgeCount)
        RBNetEditorDialog.setTabOrder(self.edtBegAgeCount, self.cmbEndAgeUnit)
        RBNetEditorDialog.setTabOrder(self.cmbEndAgeUnit, self.edtEndAgeCount)
        RBNetEditorDialog.setTabOrder(self.edtEndAgeCount, self.buttonBox)

    def retranslateUi(self, RBNetEditorDialog):
        RBNetEditorDialog.setWindowTitle(_translate("RBNetEditorDialog", "ChangeMe!", None))
        self.lblSex.setText(_translate("RBNetEditorDialog", "&Пол", None))
        self.cmbBegAgeUnit.setItemText(1, _translate("RBNetEditorDialog", "Д", None))
        self.cmbBegAgeUnit.setItemText(2, _translate("RBNetEditorDialog", "Н", None))
        self.cmbBegAgeUnit.setItemText(3, _translate("RBNetEditorDialog", "М", None))
        self.cmbBegAgeUnit.setItemText(4, _translate("RBNetEditorDialog", "Г", None))
        self.cmbSex.setItemText(1, _translate("RBNetEditorDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("RBNetEditorDialog", "Ж", None))
        self.lblAge.setText(_translate("RBNetEditorDialog", "&Возраст", None))
        self.edtBegAgeCount.setInputMask(_translate("RBNetEditorDialog", "000; ", None))
        self.edtEndAgeCount.setInputMask(_translate("RBNetEditorDialog", "000; ", None))
        self.lblAgeSep.setText(_translate("RBNetEditorDialog", "по", None))
        self.cmbEndAgeUnit.setItemText(1, _translate("RBNetEditorDialog", "Д", None))
        self.cmbEndAgeUnit.setItemText(2, _translate("RBNetEditorDialog", "Н", None))
        self.cmbEndAgeUnit.setItemText(3, _translate("RBNetEditorDialog", "М", None))
        self.cmbEndAgeUnit.setItemText(4, _translate("RBNetEditorDialog", "Г", None))
        self.lblCode.setText(_translate("RBNetEditorDialog", "&Код", None))
        self.lblName.setText(_translate("RBNetEditorDialog", "На&именование", None))
        self.chkUseInCreateClients.setText(_translate("RBNetEditorDialog", "Применять ограничения при регистрации пациента", None))

