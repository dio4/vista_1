# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MKBFinder.ui'
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

class Ui_ItemFinderDialog(object):
    def setupUi(self, ItemFinderDialog):
        ItemFinderDialog.setObjectName(_fromUtf8("ItemFinderDialog"))
        ItemFinderDialog.resize(560, 370)
        ItemFinderDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemFinderDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtCode = QtGui.QLineEdit(ItemFinderDialog)
        self.edtCode.setEnabled(False)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 2)
        self.chkPrim = QtGui.QCheckBox(ItemFinderDialog)
        self.chkPrim.setEnabled(False)
        self.chkPrim.setObjectName(_fromUtf8("chkPrim"))
        self.gridLayout.addWidget(self.chkPrim, 0, 3, 1, 4)
        self.btnSelectService = QtGui.QToolButton(ItemFinderDialog)
        self.btnSelectService.setEnabled(False)
        self.btnSelectService.setObjectName(_fromUtf8("btnSelectService"))
        self.gridLayout.addWidget(self.btnSelectService, 8, 6, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.cmbBegAgeUnit = QtGui.QComboBox(ItemFinderDialog)
        self.cmbBegAgeUnit.setEnabled(False)
        self.cmbBegAgeUnit.setObjectName(_fromUtf8("cmbBegAgeUnit"))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.setItemText(0, _fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.cmbBegAgeUnit)
        self.edtBegAgeCount = QtGui.QLineEdit(ItemFinderDialog)
        self.edtBegAgeCount.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegAgeCount.sizePolicy().hasHeightForWidth())
        self.edtBegAgeCount.setSizePolicy(sizePolicy)
        self.edtBegAgeCount.setMaxLength(3)
        self.edtBegAgeCount.setObjectName(_fromUtf8("edtBegAgeCount"))
        self.horizontalLayout.addWidget(self.edtBegAgeCount)
        self.lblAgeSep = QtGui.QLabel(ItemFinderDialog)
        self.lblAgeSep.setEnabled(False)
        self.lblAgeSep.setObjectName(_fromUtf8("lblAgeSep"))
        self.horizontalLayout.addWidget(self.lblAgeSep)
        self.cmbEndAgeUnit = QtGui.QComboBox(ItemFinderDialog)
        self.cmbEndAgeUnit.setEnabled(False)
        self.cmbEndAgeUnit.setObjectName(_fromUtf8("cmbEndAgeUnit"))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.setItemText(0, _fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.cmbEndAgeUnit)
        self.edtEndAgeCount = QtGui.QLineEdit(ItemFinderDialog)
        self.edtEndAgeCount.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndAgeCount.sizePolicy().hasHeightForWidth())
        self.edtEndAgeCount.setSizePolicy(sizePolicy)
        self.edtEndAgeCount.setMaxLength(3)
        self.edtEndAgeCount.setObjectName(_fromUtf8("edtEndAgeCount"))
        self.horizontalLayout.addWidget(self.edtEndAgeCount)
        self.gridLayout.addLayout(self.horizontalLayout, 7, 1, 1, 3)
        self.cmbService = CRBComboBox(ItemFinderDialog)
        self.cmbService.setEnabled(False)
        self.cmbService.setObjectName(_fromUtf8("cmbService"))
        self.gridLayout.addWidget(self.cmbService, 8, 1, 1, 5)
        spacerItem = QtGui.QSpacerItem(173, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 7, 5, 1, 2)
        self.cmbMKBSubclass = CRBComboBox(ItemFinderDialog)
        self.cmbMKBSubclass.setEnabled(False)
        self.cmbMKBSubclass.setObjectName(_fromUtf8("cmbMKBSubclass"))
        self.gridLayout.addWidget(self.cmbMKBSubclass, 3, 1, 1, 6)
        self.cmbCharacters = QtGui.QComboBox(ItemFinderDialog)
        self.cmbCharacters.setEnabled(False)
        self.cmbCharacters.setObjectName(_fromUtf8("cmbCharacters"))
        self.gridLayout.addWidget(self.cmbCharacters, 4, 1, 1, 6)
        self.edtDuration = QtGui.QSpinBox(ItemFinderDialog)
        self.edtDuration.setEnabled(False)
        self.edtDuration.setMaximum(999)
        self.edtDuration.setObjectName(_fromUtf8("edtDuration"))
        self.gridLayout.addWidget(self.edtDuration, 5, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(289, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 5, 2, 1, 5)
        self.cmbSex = QtGui.QComboBox(ItemFinderDialog)
        self.cmbSex.setEnabled(False)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbSex, 6, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(289, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 6, 2, 1, 5)
        self.buttonBox = QtGui.QDialogButtonBox(ItemFinderDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 13, 0, 1, 7)
        self.edtEndDate = CDateEdit(ItemFinderDialog)
        self.edtEndDate.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setDate(QtCore.QDate(2200, 1, 1))
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 9, 5, 1, 1)
        self.edtBegDate = CDateEdit(ItemFinderDialog)
        self.edtBegDate.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 9, 1, 1, 1)
        self.chkSex = QtGui.QCheckBox(ItemFinderDialog)
        self.chkSex.setObjectName(_fromUtf8("chkSex"))
        self.gridLayout.addWidget(self.chkSex, 6, 0, 1, 1)
        self.chkMKBSubclass = QtGui.QCheckBox(ItemFinderDialog)
        self.chkMKBSubclass.setObjectName(_fromUtf8("chkMKBSubclass"))
        self.gridLayout.addWidget(self.chkMKBSubclass, 3, 0, 1, 1)
        self.chkCode = QtGui.QCheckBox(ItemFinderDialog)
        self.chkCode.setObjectName(_fromUtf8("chkCode"))
        self.gridLayout.addWidget(self.chkCode, 0, 0, 1, 1)
        self.chkName = QtGui.QCheckBox(ItemFinderDialog)
        self.chkName.setObjectName(_fromUtf8("chkName"))
        self.gridLayout.addWidget(self.chkName, 1, 0, 2, 1)
        self.chkCharacters = QtGui.QCheckBox(ItemFinderDialog)
        self.chkCharacters.setObjectName(_fromUtf8("chkCharacters"))
        self.gridLayout.addWidget(self.chkCharacters, 4, 0, 1, 1)
        self.chkDuration = QtGui.QCheckBox(ItemFinderDialog)
        self.chkDuration.setObjectName(_fromUtf8("chkDuration"))
        self.gridLayout.addWidget(self.chkDuration, 5, 0, 1, 1)
        self.chkService = QtGui.QCheckBox(ItemFinderDialog)
        self.chkService.setObjectName(_fromUtf8("chkService"))
        self.gridLayout.addWidget(self.chkService, 8, 0, 1, 1)
        self.chkEndDate = QtGui.QCheckBox(ItemFinderDialog)
        self.chkEndDate.setObjectName(_fromUtf8("chkEndDate"))
        self.gridLayout.addWidget(self.chkEndDate, 9, 4, 1, 1)
        self.chkAge = QtGui.QCheckBox(ItemFinderDialog)
        self.chkAge.setObjectName(_fromUtf8("chkAge"))
        self.gridLayout.addWidget(self.chkAge, 7, 0, 1, 1)
        self.edtName = QtGui.QTextEdit(ItemFinderDialog)
        self.edtName.setEnabled(False)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 6)
        self.chkBegDate = QtGui.QCheckBox(ItemFinderDialog)
        self.chkBegDate.setObjectName(_fromUtf8("chkBegDate"))
        self.gridLayout.addWidget(self.chkBegDate, 9, 0, 1, 1)
        self.chkOMSMTR = QtGui.QCheckBox(ItemFinderDialog)
        self.chkOMSMTR.setObjectName(_fromUtf8("chkOMSMTR"))
        self.gridLayout.addWidget(self.chkOMSMTR, 10, 0, 1, 1)
        self.chkMTR = QtGui.QCheckBox(ItemFinderDialog)
        self.chkMTR.setEnabled(False)
        self.chkMTR.setObjectName(_fromUtf8("chkMTR"))
        self.gridLayout.addWidget(self.chkMTR, 10, 2, 1, 1)
        self.chkOMS = QtGui.QCheckBox(ItemFinderDialog)
        self.chkOMS.setEnabled(False)
        self.chkOMS.setObjectName(_fromUtf8("chkOMS"))
        self.gridLayout.addWidget(self.chkOMS, 10, 1, 1, 1)
        self.lblAgeSep.setBuddy(self.cmbEndAgeUnit)

        self.retranslateUi(ItemFinderDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemFinderDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemFinderDialog.reject)
        QtCore.QObject.connect(self.chkCode, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtCode.setEnabled)
        QtCore.QObject.connect(self.chkCode, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkPrim.setEnabled)
        QtCore.QObject.connect(self.chkMKBSubclass, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbMKBSubclass.setEnabled)
        QtCore.QObject.connect(self.chkCharacters, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbCharacters.setEnabled)
        QtCore.QObject.connect(self.chkDuration, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtDuration.setEnabled)
        QtCore.QObject.connect(self.chkSex, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbSex.setEnabled)
        QtCore.QObject.connect(self.chkAge, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbBegAgeUnit.setEnabled)
        QtCore.QObject.connect(self.chkAge, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtBegAgeCount.setEnabled)
        QtCore.QObject.connect(self.chkAge, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblAgeSep.setEnabled)
        QtCore.QObject.connect(self.chkAge, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbEndAgeUnit.setEnabled)
        QtCore.QObject.connect(self.chkAge, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtEndAgeCount.setEnabled)
        QtCore.QObject.connect(self.chkService, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbService.setEnabled)
        QtCore.QObject.connect(self.chkService, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.btnSelectService.setEnabled)
        QtCore.QObject.connect(self.chkBegDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtBegDate.setEnabled)
        QtCore.QObject.connect(self.chkEndDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtEndDate.setEnabled)
        QtCore.QObject.connect(self.chkName, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtName.setEnabled)
        QtCore.QObject.connect(self.chkOMSMTR, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkOMS.setEnabled)
        QtCore.QObject.connect(self.chkOMSMTR, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkMTR.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ItemFinderDialog)
        ItemFinderDialog.setTabOrder(self.edtCode, self.chkPrim)
        ItemFinderDialog.setTabOrder(self.chkPrim, self.edtName)
        ItemFinderDialog.setTabOrder(self.edtName, self.cmbMKBSubclass)
        ItemFinderDialog.setTabOrder(self.cmbMKBSubclass, self.cmbCharacters)
        ItemFinderDialog.setTabOrder(self.cmbCharacters, self.edtDuration)
        ItemFinderDialog.setTabOrder(self.edtDuration, self.cmbSex)
        ItemFinderDialog.setTabOrder(self.cmbSex, self.cmbBegAgeUnit)
        ItemFinderDialog.setTabOrder(self.cmbBegAgeUnit, self.edtBegAgeCount)
        ItemFinderDialog.setTabOrder(self.edtBegAgeCount, self.cmbEndAgeUnit)
        ItemFinderDialog.setTabOrder(self.cmbEndAgeUnit, self.edtEndAgeCount)
        ItemFinderDialog.setTabOrder(self.edtEndAgeCount, self.cmbService)
        ItemFinderDialog.setTabOrder(self.cmbService, self.btnSelectService)
        ItemFinderDialog.setTabOrder(self.btnSelectService, self.buttonBox)

    def retranslateUi(self, ItemFinderDialog):
        ItemFinderDialog.setWindowTitle(_translate("ItemFinderDialog", "ChangeMe!", None))
        self.chkPrim.setWhatsThis(_translate("ItemFinderDialog", "В справочнике МКБ обычно отмечается звёздочкой", None))
        self.chkPrim.setText(_translate("ItemFinderDialog", "уточняется в других рубриках", None))
        self.btnSelectService.setText(_translate("ItemFinderDialog", "...", None))
        self.cmbBegAgeUnit.setItemText(1, _translate("ItemFinderDialog", "Д", None))
        self.cmbBegAgeUnit.setItemText(2, _translate("ItemFinderDialog", "Н", None))
        self.cmbBegAgeUnit.setItemText(3, _translate("ItemFinderDialog", "М", None))
        self.cmbBegAgeUnit.setItemText(4, _translate("ItemFinderDialog", "Г", None))
        self.edtBegAgeCount.setInputMask(_translate("ItemFinderDialog", "000; ", None))
        self.lblAgeSep.setText(_translate("ItemFinderDialog", "по", None))
        self.cmbEndAgeUnit.setItemText(1, _translate("ItemFinderDialog", "Д", None))
        self.cmbEndAgeUnit.setItemText(2, _translate("ItemFinderDialog", "Н", None))
        self.cmbEndAgeUnit.setItemText(3, _translate("ItemFinderDialog", "М", None))
        self.cmbEndAgeUnit.setItemText(4, _translate("ItemFinderDialog", "Г", None))
        self.edtEndAgeCount.setInputMask(_translate("ItemFinderDialog", "000; ", None))
        self.cmbMKBSubclass.setWhatsThis(_translate("ItemFinderDialog", "Последующее уточнение кода диагноза, не предписанное справочником МКБ", None))
        self.cmbCharacters.setWhatsThis(_translate("ItemFinderDialog", "Допустимый характер заболевания, применяется для контроля ввода", None))
        self.cmbSex.setItemText(1, _translate("ItemFinderDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("ItemFinderDialog", "Ж", None))
        self.chkSex.setText(_translate("ItemFinderDialog", "&Пол", None))
        self.chkMKBSubclass.setText(_translate("ItemFinderDialog", "Cу&бклассификация\n"
"МКБ по 5 знаку", None))
        self.chkCode.setText(_translate("ItemFinderDialog", "Код", None))
        self.chkName.setText(_translate("ItemFinderDialog", "Наименование", None))
        self.chkCharacters.setText(_translate("ItemFinderDialog", "&Характер", None))
        self.chkDuration.setText(_translate("ItemFinderDialog", "&Длительность", None))
        self.chkService.setText(_translate("ItemFinderDialog", "&Услуга", None))
        self.chkEndDate.setText(_translate("ItemFinderDialog", "Дата окончания:", None))
        self.chkAge.setText(_translate("ItemFinderDialog", "&Возраст", None))
        self.chkBegDate.setText(_translate("ItemFinderDialog", "Дата начала:", None))
        self.chkOMSMTR.setText(_translate("ItemFinderDialog", "Краевой/Инокрай", None))
        self.chkMTR.setText(_translate("ItemFinderDialog", "Инокраевой", None))
        self.chkOMS.setText(_translate("ItemFinderDialog", "Краевой", None))

from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
