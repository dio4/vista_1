# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBSpecialityEditor.ui'
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
        ItemEditorDialog.resize(482, 509)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtOKSOCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtOKSOCode.setObjectName(_fromUtf8("edtOKSOCode"))
        self.gridLayout.addWidget(self.edtOKSOCode, 4, 1, 1, 3)
        self.lblFederalCode = QtGui.QLabel(ItemEditorDialog)
        self.lblFederalCode.setObjectName(_fromUtf8("lblFederalCode"))
        self.gridLayout.addWidget(self.lblFederalCode, 5, 0, 1, 1)
        self.lblVersSpec = QtGui.QLabel(ItemEditorDialog)
        self.lblVersSpec.setObjectName(_fromUtf8("lblVersSpec"))
        self.gridLayout.addWidget(self.lblVersSpec, 8, 0, 1, 1)
        self.lblSex = QtGui.QLabel(ItemEditorDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout.addWidget(self.lblSex, 14, 0, 1, 1)
        self.cmbProvinceService = CRBComboBox(ItemEditorDialog)
        self.cmbProvinceService.setObjectName(_fromUtf8("cmbProvinceService"))
        self.gridLayout.addWidget(self.cmbProvinceService, 10, 1, 1, 2)
        self.cmbVersSpec = QtGui.QComboBox(ItemEditorDialog)
        self.cmbVersSpec.setObjectName(_fromUtf8("cmbVersSpec"))
        self.cmbVersSpec.addItem(_fromUtf8(""))
        self.cmbVersSpec.setItemText(0, _fromUtf8(""))
        self.cmbVersSpec.addItem(_fromUtf8(""))
        self.cmbVersSpec.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbVersSpec, 8, 1, 1, 3)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtFederalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtFederalCode.setObjectName(_fromUtf8("edtFederalCode"))
        self.gridLayout.addWidget(self.edtFederalCode, 5, 1, 1, 3)
        self.cmbLocalService = CRBComboBox(ItemEditorDialog)
        self.cmbLocalService.setObjectName(_fromUtf8("cmbLocalService"))
        self.gridLayout.addWidget(self.cmbLocalService, 9, 1, 1, 2)
        self.cmbSex = QtGui.QComboBox(ItemEditorDialog)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbSex, 14, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 13, 0, 1, 1)
        self.lblProvinceService = QtGui.QLabel(ItemEditorDialog)
        self.lblProvinceService.setObjectName(_fromUtf8("lblProvinceService"))
        self.gridLayout.addWidget(self.lblProvinceService, 10, 0, 1, 1)
        self.lblMKBFilter = QtGui.QLabel(ItemEditorDialog)
        self.lblMKBFilter.setObjectName(_fromUtf8("lblMKBFilter"))
        self.gridLayout.addWidget(self.lblMKBFilter, 16, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(141, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 14, 2, 1, 2)
        self.edtShortName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtShortName.setObjectName(_fromUtf8("edtShortName"))
        self.gridLayout.addWidget(self.edtShortName, 2, 1, 1, 3)
        self.lblName_2 = QtGui.QLabel(ItemEditorDialog)
        self.lblName_2.setObjectName(_fromUtf8("lblName_2"))
        self.gridLayout.addWidget(self.lblName_2, 3, 0, 1, 1)
        self.lblShortName = QtGui.QLabel(ItemEditorDialog)
        self.lblShortName.setObjectName(_fromUtf8("lblShortName"))
        self.gridLayout.addWidget(self.lblShortName, 2, 0, 1, 1)
        self.lblSyncGUID = QtGui.QLabel(ItemEditorDialog)
        self.lblSyncGUID.setObjectName(_fromUtf8("lblSyncGUID"))
        self.gridLayout.addWidget(self.lblSyncGUID, 7, 0, 1, 1)
        self.edtSyncGUID = QtGui.QLineEdit(ItemEditorDialog)
        self.edtSyncGUID.setObjectName(_fromUtf8("edtSyncGUID"))
        self.gridLayout.addWidget(self.edtSyncGUID, 7, 1, 1, 3)
        self.lblRegionalCode = QtGui.QLabel(ItemEditorDialog)
        self.lblRegionalCode.setObjectName(_fromUtf8("lblRegionalCode"))
        self.gridLayout.addWidget(self.lblRegionalCode, 6, 0, 1, 1)
        self.edtRegionalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtRegionalCode.setObjectName(_fromUtf8("edtRegionalCode"))
        self.gridLayout.addWidget(self.edtRegionalCode, 6, 1, 1, 3)
        self.edtMKBFilter = QtGui.QLineEdit(ItemEditorDialog)
        self.edtMKBFilter.setObjectName(_fromUtf8("edtMKBFilter"))
        self.gridLayout.addWidget(self.edtMKBFilter, 16, 1, 1, 3)
        spacerItem2 = QtGui.QSpacerItem(73, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 18, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 21, 0, 1, 4)
        self.lblOtherService = QtGui.QLabel(ItemEditorDialog)
        self.lblOtherService.setObjectName(_fromUtf8("lblOtherService"))
        self.gridLayout.addWidget(self.lblOtherService, 11, 0, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.btnSelectOtherService = QtGui.QToolButton(ItemEditorDialog)
        self.btnSelectOtherService.setObjectName(_fromUtf8("btnSelectOtherService"))
        self.gridLayout.addWidget(self.btnSelectOtherService, 11, 3, 1, 1)
        self.btnSelectLocalService = QtGui.QToolButton(ItemEditorDialog)
        self.btnSelectLocalService.setObjectName(_fromUtf8("btnSelectLocalService"))
        self.gridLayout.addWidget(self.btnSelectLocalService, 9, 3, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 3)
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
        self.edtEndAgeCount.setMaxLength(3)
        self.edtEndAgeCount.setObjectName(_fromUtf8("edtEndAgeCount"))
        self.horizontalLayout.addWidget(self.edtEndAgeCount)
        self.gridLayout.addLayout(self.horizontalLayout, 15, 1, 1, 3)
        self.edtOKSOName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtOKSOName.setObjectName(_fromUtf8("edtOKSOName"))
        self.gridLayout.addWidget(self.edtOKSOName, 3, 1, 1, 3)
        self.btnSelectProvinceService = QtGui.QToolButton(ItemEditorDialog)
        self.btnSelectProvinceService.setObjectName(_fromUtf8("btnSelectProvinceService"))
        self.gridLayout.addWidget(self.btnSelectProvinceService, 10, 3, 1, 1)
        self.cmbOtherService = CRBComboBox(ItemEditorDialog)
        self.cmbOtherService.setObjectName(_fromUtf8("cmbOtherService"))
        self.gridLayout.addWidget(self.cmbOtherService, 11, 1, 1, 2)
        self.lblAge = QtGui.QLabel(ItemEditorDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout.addWidget(self.lblAge, 15, 0, 1, 1)
        self.lblName_3 = QtGui.QLabel(ItemEditorDialog)
        self.lblName_3.setObjectName(_fromUtf8("lblName_3"))
        self.gridLayout.addWidget(self.lblName_3, 4, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 3)
        self.label = QtGui.QLabel(ItemEditorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 12, 0, 1, 1)
        self.cmbFundingService = CRBComboBox(ItemEditorDialog)
        self.cmbFundingService.setObjectName(_fromUtf8("cmbFundingService"))
        self.gridLayout.addWidget(self.cmbFundingService, 12, 1, 1, 2)
        self.btnSelectFundingService = QtGui.QToolButton(ItemEditorDialog)
        self.btnSelectFundingService.setObjectName(_fromUtf8("btnSelectFundingService"))
        self.gridLayout.addWidget(self.btnSelectFundingService, 12, 3, 1, 1)
        self.lblLocalService = QtGui.QLabel(ItemEditorDialog)
        self.lblLocalService.setObjectName(_fromUtf8("lblLocalService"))
        self.gridLayout.addWidget(self.lblLocalService, 9, 0, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSpacing(3)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_2 = QtGui.QLabel(ItemEditorDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.tblQueueShare = CItemListView(ItemEditorDialog)
        self.tblQueueShare.setObjectName(_fromUtf8("tblQueueShare"))
        self.gridLayout_2.addWidget(self.tblQueueShare, 1, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 19, 0, 1, 4)
        self.lblFederalCode.setBuddy(self.edtFederalCode)
        self.lblVersSpec.setBuddy(self.cmbVersSpec)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblName.setBuddy(self.edtName)
        self.lblProvinceService.setBuddy(self.cmbProvinceService)
        self.lblMKBFilter.setBuddy(self.edtMKBFilter)
        self.lblName_2.setBuddy(self.edtOKSOName)
        self.lblRegionalCode.setBuddy(self.edtRegionalCode)
        self.lblOtherService.setBuddy(self.cmbOtherService)
        self.lblCode.setBuddy(self.edtCode)
        self.lblAgeSep.setBuddy(self.cmbEndAgeUnit)
        self.lblAge.setBuddy(self.cmbBegAgeUnit)
        self.lblName_3.setBuddy(self.edtOKSOCode)
        self.lblLocalService.setBuddy(self.cmbLocalService)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.edtShortName)
        ItemEditorDialog.setTabOrder(self.edtShortName, self.edtOKSOName)
        ItemEditorDialog.setTabOrder(self.edtOKSOName, self.edtOKSOCode)
        ItemEditorDialog.setTabOrder(self.edtOKSOCode, self.edtFederalCode)
        ItemEditorDialog.setTabOrder(self.edtFederalCode, self.edtRegionalCode)
        ItemEditorDialog.setTabOrder(self.edtRegionalCode, self.cmbVersSpec)
        ItemEditorDialog.setTabOrder(self.cmbVersSpec, self.cmbLocalService)
        ItemEditorDialog.setTabOrder(self.cmbLocalService, self.btnSelectLocalService)
        ItemEditorDialog.setTabOrder(self.btnSelectLocalService, self.cmbProvinceService)
        ItemEditorDialog.setTabOrder(self.cmbProvinceService, self.btnSelectProvinceService)
        ItemEditorDialog.setTabOrder(self.btnSelectProvinceService, self.cmbOtherService)
        ItemEditorDialog.setTabOrder(self.cmbOtherService, self.btnSelectOtherService)
        ItemEditorDialog.setTabOrder(self.btnSelectOtherService, self.cmbSex)
        ItemEditorDialog.setTabOrder(self.cmbSex, self.cmbBegAgeUnit)
        ItemEditorDialog.setTabOrder(self.cmbBegAgeUnit, self.edtBegAgeCount)
        ItemEditorDialog.setTabOrder(self.edtBegAgeCount, self.cmbEndAgeUnit)
        ItemEditorDialog.setTabOrder(self.cmbEndAgeUnit, self.edtEndAgeCount)
        ItemEditorDialog.setTabOrder(self.edtEndAgeCount, self.edtMKBFilter)
        ItemEditorDialog.setTabOrder(self.edtMKBFilter, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.lblFederalCode.setText(_translate("ItemEditorDialog", "&Федеральный код", None))
        self.lblVersSpec.setText(_translate("ItemEditorDialog", "Версия справочника", None))
        self.lblSex.setText(_translate("ItemEditorDialog", "&Пол", None))
        self.cmbVersSpec.setItemText(1, _translate("ItemEditorDialog", "V004", None))
        self.cmbVersSpec.setItemText(2, _translate("ItemEditorDialog", "V015", None))
        self.lblName.setText(_translate("ItemEditorDialog", "&Наименование", None))
        self.cmbSex.setItemText(1, _translate("ItemEditorDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("ItemEditorDialog", "Ж", None))
        self.lblProvinceService.setText(_translate("ItemEditorDialog", "Услуга для областного населения", None))
        self.lblMKBFilter.setText(_translate("ItemEditorDialog", "&Фильтр диагнозов по МКБ", None))
        self.lblName_2.setText(_translate("ItemEditorDialog", "Наименование по ОКСО", None))
        self.lblShortName.setText(_translate("ItemEditorDialog", "Краткое наименование", None))
        self.lblSyncGUID.setText(_translate("ItemEditorDialog", "Код синхронизации", None))
        self.lblRegionalCode.setText(_translate("ItemEditorDialog", "&Региональный код", None))
        self.lblOtherService.setText(_translate("ItemEditorDialog", "Услуга для прочего населения", None))
        self.lblCode.setText(_translate("ItemEditorDialog", "&Код", None))
        self.btnSelectOtherService.setText(_translate("ItemEditorDialog", "...", None))
        self.btnSelectLocalService.setText(_translate("ItemEditorDialog", "...", None))
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
        self.btnSelectProvinceService.setText(_translate("ItemEditorDialog", "...", None))
        self.lblAge.setText(_translate("ItemEditorDialog", "&Возраст", None))
        self.lblName_3.setText(_translate("ItemEditorDialog", "Код по &ОКСО", None))
        self.label.setText(_translate("ItemEditorDialog", "Услуга для подушевого финансирования", None))
        self.btnSelectFundingService.setText(_translate("ItemEditorDialog", "...", None))
        self.lblLocalService.setText(_translate("ItemEditorDialog", "&Услуга для местного населения", None))
        self.label_2.setText(_translate("ItemEditorDialog", "Досупное количество номерков по дням от текущей даты (в %)", None))

from library.ItemListView import CItemListView
from library.crbcombobox import CRBComboBox
