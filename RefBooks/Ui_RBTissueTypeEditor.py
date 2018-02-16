# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBTissueTypeEditor.ui'
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

class Ui_TissueTypeEditorDialog(object):
    def setupUi(self, TissueTypeEditorDialog):
        TissueTypeEditorDialog.setObjectName(_fromUtf8("TissueTypeEditorDialog"))
        TissueTypeEditorDialog.resize(381, 193)
        TissueTypeEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(TissueTypeEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCode = QtGui.QLabel(TissueTypeEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(TissueTypeEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(TissueTypeEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(TissueTypeEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(TissueTypeEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 0, 1, 1)
        self.lblResetCounterType = QtGui.QLabel(TissueTypeEditorDialog)
        self.lblResetCounterType.setObjectName(_fromUtf8("lblResetCounterType"))
        self.gridLayout.addWidget(self.lblResetCounterType, 6, 0, 1, 1)
        self.cmbCounterResetType = QtGui.QComboBox(TissueTypeEditorDialog)
        self.cmbCounterResetType.setObjectName(_fromUtf8("cmbCounterResetType"))
        self.cmbCounterResetType.addItem(_fromUtf8(""))
        self.cmbCounterResetType.addItem(_fromUtf8(""))
        self.cmbCounterResetType.addItem(_fromUtf8(""))
        self.cmbCounterResetType.addItem(_fromUtf8(""))
        self.cmbCounterResetType.addItem(_fromUtf8(""))
        self.cmbCounterResetType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbCounterResetType, 6, 1, 1, 1)
        self.chkCounterManualInput = QtGui.QCheckBox(TissueTypeEditorDialog)
        self.chkCounterManualInput.setText(_fromUtf8(""))
        self.chkCounterManualInput.setObjectName(_fromUtf8("chkCounterManualInput"))
        self.gridLayout.addWidget(self.chkCounterManualInput, 3, 1, 1, 1)
        self.lblCounterManualInput = QtGui.QLabel(TissueTypeEditorDialog)
        self.lblCounterManualInput.setObjectName(_fromUtf8("lblCounterManualInput"))
        self.gridLayout.addWidget(self.lblCounterManualInput, 3, 0, 1, 1)
        self.cmbSex = QtGui.QComboBox(TissueTypeEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSex.sizePolicy().hasHeightForWidth())
        self.cmbSex.setSizePolicy(sizePolicy)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbSex, 2, 1, 1, 1)
        self.lblSex = QtGui.QLabel(TissueTypeEditorDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout.addWidget(self.lblSex, 2, 0, 1, 1)
        self.lblExternalIdLimit = QtGui.QLabel(TissueTypeEditorDialog)
        self.lblExternalIdLimit.setObjectName(_fromUtf8("lblExternalIdLimit"))
        self.gridLayout.addWidget(self.lblExternalIdLimit, 8, 0, 1, 1)
        self.edtExternalIdLimit = QtGui.QLineEdit(TissueTypeEditorDialog)
        self.edtExternalIdLimit.setObjectName(_fromUtf8("edtExternalIdLimit"))
        self.gridLayout.addWidget(self.edtExternalIdLimit, 8, 1, 1, 1)
        self.edtCounterValue = QtGui.QLineEdit(TissueTypeEditorDialog)
        self.edtCounterValue.setEnabled(False)
        self.edtCounterValue.setObjectName(_fromUtf8("edtCounterValue"))
        self.gridLayout.addWidget(self.edtCounterValue, 5, 1, 1, 1)
        self.chkIdentCounter = QtGui.QCheckBox(TissueTypeEditorDialog)
        self.chkIdentCounter.setObjectName(_fromUtf8("chkIdentCounter"))
        self.gridLayout.addWidget(self.chkIdentCounter, 5, 0, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblResetCounterType.setBuddy(self.cmbCounterResetType)
        self.lblCounterManualInput.setBuddy(self.chkCounterManualInput)
        self.lblSex.setBuddy(self.cmbSex)

        self.retranslateUi(TissueTypeEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TissueTypeEditorDialog.accept)
        QtCore.QObject.connect(self.chkIdentCounter, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtCounterValue.setEnabled)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TissueTypeEditorDialog.reject)
        QtCore.QObject.connect(self.chkCounterManualInput, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkIdentCounter.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(TissueTypeEditorDialog)
        TissueTypeEditorDialog.setTabOrder(self.edtCode, self.edtName)
        TissueTypeEditorDialog.setTabOrder(self.edtName, self.cmbSex)
        TissueTypeEditorDialog.setTabOrder(self.cmbSex, self.chkCounterManualInput)
        TissueTypeEditorDialog.setTabOrder(self.chkCounterManualInput, self.cmbCounterResetType)
        TissueTypeEditorDialog.setTabOrder(self.cmbCounterResetType, self.buttonBox)

    def retranslateUi(self, TissueTypeEditorDialog):
        TissueTypeEditorDialog.setWindowTitle(_translate("TissueTypeEditorDialog", "Dialog", None))
        self.lblCode.setText(_translate("TissueTypeEditorDialog", "Код", None))
        self.lblName.setText(_translate("TissueTypeEditorDialog", "Наименование", None))
        self.lblResetCounterType.setText(_translate("TissueTypeEditorDialog", "Период уникальности идентификатора", None))
        self.cmbCounterResetType.setItemText(0, _translate("TissueTypeEditorDialog", "День", None))
        self.cmbCounterResetType.setItemText(1, _translate("TissueTypeEditorDialog", "Неделя", None))
        self.cmbCounterResetType.setItemText(2, _translate("TissueTypeEditorDialog", "Месяц", None))
        self.cmbCounterResetType.setItemText(3, _translate("TissueTypeEditorDialog", "Полгода", None))
        self.cmbCounterResetType.setItemText(4, _translate("TissueTypeEditorDialog", "Год", None))
        self.cmbCounterResetType.setItemText(5, _translate("TissueTypeEditorDialog", "Постоянно", None))
        self.lblCounterManualInput.setText(_translate("TissueTypeEditorDialog", "Ручной ввод идентификатора", None))
        self.cmbSex.setItemText(1, _translate("TissueTypeEditorDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("TissueTypeEditorDialog", "Ж", None))
        self.lblSex.setText(_translate("TissueTypeEditorDialog", "Пол", None))
        self.lblExternalIdLimit.setText(_translate("TissueTypeEditorDialog", "Ограничение длины идентификатора", None))
        self.chkIdentCounter.setText(_translate("TissueTypeEditorDialog", "Счетчик идентификатора", None))

