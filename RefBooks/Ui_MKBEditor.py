# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MKBEditor.ui'
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
        ItemEditorDialog.resize(584, 648)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(289, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 4, 2, 1, 5)
        self.lblEndDate = QtGui.QLabel(ItemEditorDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 13, 4, 1, 1)
        self.chkPrim = QtGui.QCheckBox(ItemEditorDialog)
        self.chkPrim.setObjectName(_fromUtf8("chkPrim"))
        self.gridLayout.addWidget(self.chkPrim, 0, 3, 1, 4)
        spacerItem1 = QtGui.QSpacerItem(173, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 6, 4, 1, 3)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(289, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 5, 2, 1, 5)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 2)
        self.cmbCharacters = QtGui.QComboBox(ItemEditorDialog)
        self.cmbCharacters.setObjectName(_fromUtf8("cmbCharacters"))
        self.gridLayout.addWidget(self.cmbCharacters, 3, 1, 1, 6)
        self.cmbMKBSubclass = CRBComboBox(ItemEditorDialog)
        self.cmbMKBSubclass.setObjectName(_fromUtf8("cmbMKBSubclass"))
        self.gridLayout.addWidget(self.cmbMKBSubclass, 2, 1, 1, 6)
        self.label_2 = QtGui.QLabel(ItemEditorDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 8, 0, 1, 7)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.cmbBegAgeUnit = QtGui.QComboBox(ItemEditorDialog)
        self.cmbBegAgeUnit.setObjectName(_fromUtf8("cmbBegAgeUnit"))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.setItemText(0, _fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.cmbBegAgeUnit)
        self.edtBegAgeCount = QtGui.QLineEdit(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegAgeCount.sizePolicy().hasHeightForWidth())
        self.edtBegAgeCount.setSizePolicy(sizePolicy)
        self.edtBegAgeCount.setMaxLength(3)
        self.edtBegAgeCount.setObjectName(_fromUtf8("edtBegAgeCount"))
        self.horizontalLayout.addWidget(self.edtBegAgeCount)
        self.lblAgeSep = QtGui.QLabel(ItemEditorDialog)
        self.lblAgeSep.setObjectName(_fromUtf8("lblAgeSep"))
        self.horizontalLayout.addWidget(self.lblAgeSep)
        self.cmbEndAgeUnit = QtGui.QComboBox(ItemEditorDialog)
        self.cmbEndAgeUnit.setObjectName(_fromUtf8("cmbEndAgeUnit"))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.setItemText(0, _fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.cmbEndAgeUnit)
        self.edtEndAgeCount = QtGui.QLineEdit(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndAgeCount.sizePolicy().hasHeightForWidth())
        self.edtEndAgeCount.setSizePolicy(sizePolicy)
        self.edtEndAgeCount.setMaxLength(3)
        self.edtEndAgeCount.setObjectName(_fromUtf8("edtEndAgeCount"))
        self.horizontalLayout.addWidget(self.edtEndAgeCount)
        self.gridLayout.addLayout(self.horizontalLayout, 6, 1, 1, 3)
        self.lblDuration = QtGui.QLabel(ItemEditorDialog)
        self.lblDuration.setObjectName(_fromUtf8("lblDuration"))
        self.gridLayout.addWidget(self.lblDuration, 4, 0, 1, 1)
        self.edtEndDate = CDateEdit(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setDate(QtCore.QDate(2200, 1, 1))
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 13, 5, 1, 1)
        self.lblSex = QtGui.QLabel(ItemEditorDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout.addWidget(self.lblSex, 5, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ItemEditorDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 13, 0, 1, 1)
        self.chkOMS = QtGui.QCheckBox(ItemEditorDialog)
        self.chkOMS.setObjectName(_fromUtf8("chkOMS"))
        self.gridLayout.addWidget(self.chkOMS, 14, 0, 1, 5)
        self.lblCharacters = QtGui.QLabel(ItemEditorDialog)
        self.lblCharacters.setObjectName(_fromUtf8("lblCharacters"))
        self.gridLayout.addWidget(self.lblCharacters, 3, 0, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.label = QtGui.QLabel(ItemEditorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.chkMTR = QtGui.QCheckBox(ItemEditorDialog)
        self.chkMTR.setObjectName(_fromUtf8("chkMTR"))
        self.gridLayout.addWidget(self.chkMTR, 15, 0, 1, 2)
        self.lblAge = QtGui.QLabel(ItemEditorDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout.addWidget(self.lblAge, 6, 0, 1, 1)
        self.edtBegDate = CDateEdit(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 13, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 16, 0, 1, 7)
        self.cmbSex = QtGui.QComboBox(ItemEditorDialog)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbSex, 5, 1, 1, 1)
        self.edtDuration = QtGui.QSpinBox(ItemEditorDialog)
        self.edtDuration.setMaximum(999)
        self.edtDuration.setObjectName(_fromUtf8("edtDuration"))
        self.gridLayout.addWidget(self.edtDuration, 4, 1, 1, 1)
        self.edtName = QtGui.QTextEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 6)
        self.tblServiceSpecialty = CInDocTableView(ItemEditorDialog)
        self.tblServiceSpecialty.setEnabled(True)
        self.tblServiceSpecialty.setMinimumSize(QtCore.QSize(0, 150))
        self.tblServiceSpecialty.setObjectName(_fromUtf8("tblServiceSpecialty"))
        self.gridLayout.addWidget(self.tblServiceSpecialty, 10, 1, 3, 6)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 11, 0, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblAgeSep.setBuddy(self.cmbEndAgeUnit)
        self.lblDuration.setBuddy(self.edtDuration)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblCharacters.setBuddy(self.cmbCharacters)
        self.lblName.setBuddy(self.edtName)
        self.label.setBuddy(self.cmbMKBSubclass)
        self.lblAge.setBuddy(self.cmbBegAgeUnit)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.chkPrim)
        ItemEditorDialog.setTabOrder(self.chkPrim, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.cmbMKBSubclass)
        ItemEditorDialog.setTabOrder(self.cmbMKBSubclass, self.cmbCharacters)
        ItemEditorDialog.setTabOrder(self.cmbCharacters, self.edtDuration)
        ItemEditorDialog.setTabOrder(self.edtDuration, self.cmbSex)
        ItemEditorDialog.setTabOrder(self.cmbSex, self.cmbBegAgeUnit)
        ItemEditorDialog.setTabOrder(self.cmbBegAgeUnit, self.edtBegAgeCount)
        ItemEditorDialog.setTabOrder(self.edtBegAgeCount, self.cmbEndAgeUnit)
        ItemEditorDialog.setTabOrder(self.cmbEndAgeUnit, self.edtEndAgeCount)
        ItemEditorDialog.setTabOrder(self.edtEndAgeCount, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.lblEndDate.setText(_translate("ItemEditorDialog", "Дата окончания:", None))
        self.chkPrim.setWhatsThis(_translate("ItemEditorDialog", "В справочнике МКБ обычно отмечается звёздочкой", None))
        self.chkPrim.setText(_translate("ItemEditorDialog", "уточняется в других рубриках", None))
        self.lblCode.setText(_translate("ItemEditorDialog", "&Код", None))
        self.cmbCharacters.setWhatsThis(_translate("ItemEditorDialog", "Допустимый характер заболевания, применяется для контроля ввода", None))
        self.cmbMKBSubclass.setWhatsThis(_translate("ItemEditorDialog", "Последующее уточнение кода диагноза, не предписанное справочником МКБ", None))
        self.label_2.setText(_translate("ItemEditorDialog", "Услуга - Специальность", None))
        self.cmbBegAgeUnit.setItemText(1, _translate("ItemEditorDialog", "Д", None))
        self.cmbBegAgeUnit.setItemText(2, _translate("ItemEditorDialog", "Н", None))
        self.cmbBegAgeUnit.setItemText(3, _translate("ItemEditorDialog", "М", None))
        self.cmbBegAgeUnit.setItemText(4, _translate("ItemEditorDialog", "Г", None))
        self.edtBegAgeCount.setInputMask(_translate("ItemEditorDialog", "000; ", None))
        self.lblAgeSep.setText(_translate("ItemEditorDialog", "по", None))
        self.cmbEndAgeUnit.setItemText(1, _translate("ItemEditorDialog", "Д", None))
        self.cmbEndAgeUnit.setItemText(2, _translate("ItemEditorDialog", "Н", None))
        self.cmbEndAgeUnit.setItemText(3, _translate("ItemEditorDialog", "М", None))
        self.cmbEndAgeUnit.setItemText(4, _translate("ItemEditorDialog", "Г", None))
        self.edtEndAgeCount.setInputMask(_translate("ItemEditorDialog", "000; ", None))
        self.lblDuration.setText(_translate("ItemEditorDialog", "&Длительность", None))
        self.lblSex.setText(_translate("ItemEditorDialog", "&Пол", None))
        self.lblBegDate.setText(_translate("ItemEditorDialog", "Дата начала:", None))
        self.chkOMS.setText(_translate("ItemEditorDialog", "Краевой", None))
        self.lblCharacters.setText(_translate("ItemEditorDialog", "&Характер", None))
        self.lblName.setText(_translate("ItemEditorDialog", "&Наименование", None))
        self.label.setText(_translate("ItemEditorDialog", "Cу&бклассификация\n"
"МКБ по 5 знаку", None))
        self.chkMTR.setText(_translate("ItemEditorDialog", "Инокраевой", None))
        self.lblAge.setText(_translate("ItemEditorDialog", "&Возраст", None))
        self.cmbSex.setItemText(1, _translate("ItemEditorDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("ItemEditorDialog", "Ж", None))

from library.DateEdit import CDateEdit
from library.InDocTable import CInDocTableView
from library.crbcombobox import CRBComboBox
