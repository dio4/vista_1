# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'BlanksDialog.ui'
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

class Ui_BlanksDialog(object):
    def setupUi(self, BlanksDialog):
        BlanksDialog.setObjectName(_fromUtf8("BlanksDialog"))
        BlanksDialog.resize(611, 503)
        self.gridLayout_3 = QtGui.QGridLayout(BlanksDialog)
        self.gridLayout_3.setMargin(4)
        self.gridLayout_3.setSpacing(4)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tabWidget = QtGui.QTabWidget(BlanksDialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabTypeTempInvalid = QtGui.QWidget()
        self.tabTypeTempInvalid.setObjectName(_fromUtf8("tabTypeTempInvalid"))
        self.gridLayout_4 = QtGui.QGridLayout(self.tabTypeTempInvalid)
        self.gridLayout_4.setMargin(4)
        self.gridLayout_4.setSpacing(4)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.splitter_3 = QtGui.QSplitter(self.tabTypeTempInvalid)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName(_fromUtf8("splitter_3"))
        self.splitter_2 = QtGui.QSplitter(self.splitter_3)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.treeBlankTypeTempInvalid = CTreeView(self.splitter_2)
        self.treeBlankTypeTempInvalid.setObjectName(_fromUtf8("treeBlankTypeTempInvalid"))
        self.grbTempInvalidFilter = QtGui.QGroupBox(self.splitter_2)
        self.grbTempInvalidFilter.setObjectName(_fromUtf8("grbTempInvalidFilter"))
        self.gridLayout = QtGui.QGridLayout(self.grbTempInvalidFilter)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.grbParty = QtGui.QGroupBox(self.grbTempInvalidFilter)
        self.grbParty.setObjectName(_fromUtf8("grbParty"))
        self.gridLayout_10 = QtGui.QGridLayout(self.grbParty)
        self.gridLayout_10.setMargin(4)
        self.gridLayout_10.setSpacing(4)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.lblPersonParty = QtGui.QLabel(self.grbParty)
        self.lblPersonParty.setObjectName(_fromUtf8("lblPersonParty"))
        self.gridLayout_10.addWidget(self.lblPersonParty, 0, 0, 1, 1)
        self.lblDateParty = QtGui.QLabel(self.grbParty)
        self.lblDateParty.setObjectName(_fromUtf8("lblDateParty"))
        self.gridLayout_10.addWidget(self.lblDateParty, 1, 0, 1, 1)
        self.lblSerialParty = QtGui.QLabel(self.grbParty)
        self.lblSerialParty.setObjectName(_fromUtf8("lblSerialParty"))
        self.gridLayout_10.addWidget(self.lblSerialParty, 2, 0, 1, 1)
        self.lblNumber = QtGui.QLabel(self.grbParty)
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.gridLayout_10.addWidget(self.lblNumber, 3, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(118, 13, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_10.addItem(spacerItem, 1, 5, 1, 1)
        self.edtSerialParty = QtGui.QLineEdit(self.grbParty)
        self.edtSerialParty.setObjectName(_fromUtf8("edtSerialParty"))
        self.gridLayout_10.addWidget(self.edtSerialParty, 2, 1, 1, 9)
        self.cmbPersonParty = CPersonComboBoxEx(self.grbParty)
        self.cmbPersonParty.setObjectName(_fromUtf8("cmbPersonParty"))
        self.gridLayout_10.addWidget(self.cmbPersonParty, 0, 1, 1, 9)
        self.labelActions_3 = QtGui.QLabel(self.grbParty)
        self.labelActions_3.setObjectName(_fromUtf8("labelActions_3"))
        self.gridLayout_10.addWidget(self.labelActions_3, 3, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.grbParty)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_10.addWidget(self.label_5, 1, 1, 1, 1)
        self.edtBegDateParty = CDateEdit(self.grbParty)
        self.edtBegDateParty.setCalendarPopup(True)
        self.edtBegDateParty.setObjectName(_fromUtf8("edtBegDateParty"))
        self.gridLayout_10.addWidget(self.edtBegDateParty, 1, 2, 1, 1)
        self.label = QtGui.QLabel(self.grbParty)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_10.addWidget(self.label, 1, 3, 1, 1)
        self.edtNumberFrom = QtGui.QSpinBox(self.grbParty)
        self.edtNumberFrom.setMaximum(99999999)
        self.edtNumberFrom.setObjectName(_fromUtf8("edtNumberFrom"))
        self.gridLayout_10.addWidget(self.edtNumberFrom, 3, 2, 1, 1)
        self.edtNumberTo = QtGui.QSpinBox(self.grbParty)
        self.edtNumberTo.setMaximum(99999999)
        self.edtNumberTo.setObjectName(_fromUtf8("edtNumberTo"))
        self.gridLayout_10.addWidget(self.edtNumberTo, 3, 4, 1, 1)
        self.edtEndDateParty = CDateEdit(self.grbParty)
        self.edtEndDateParty.setObjectName(_fromUtf8("edtEndDateParty"))
        self.gridLayout_10.addWidget(self.edtEndDateParty, 1, 4, 1, 1)
        self.labelActions_2 = QtGui.QLabel(self.grbParty)
        self.labelActions_2.setObjectName(_fromUtf8("labelActions_2"))
        self.gridLayout_10.addWidget(self.labelActions_2, 3, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(89, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_10.addItem(spacerItem1, 3, 5, 1, 4)
        self.gridLayout.addWidget(self.grbParty, 0, 0, 1, 1)
        self.grbSubParty = QtGui.QGroupBox(self.grbTempInvalidFilter)
        self.grbSubParty.setObjectName(_fromUtf8("grbSubParty"))
        self.gridLayout_6 = QtGui.QGridLayout(self.grbSubParty)
        self.gridLayout_6.setMargin(4)
        self.gridLayout_6.setSpacing(4)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.lblOrgStructureSubParty = QtGui.QLabel(self.grbSubParty)
        self.lblOrgStructureSubParty.setObjectName(_fromUtf8("lblOrgStructureSubParty"))
        self.gridLayout_6.addWidget(self.lblOrgStructureSubParty, 0, 0, 1, 1)
        self.lblPersonSubParty = QtGui.QLabel(self.grbSubParty)
        self.lblPersonSubParty.setObjectName(_fromUtf8("lblPersonSubParty"))
        self.gridLayout_6.addWidget(self.lblPersonSubParty, 1, 0, 1, 1)
        self.lblDateSubParty = QtGui.QLabel(self.grbSubParty)
        self.lblDateSubParty.setObjectName(_fromUtf8("lblDateSubParty"))
        self.gridLayout_6.addWidget(self.lblDateSubParty, 2, 0, 1, 1)
        self.edtBegDateSubParty = CDateEdit(self.grbSubParty)
        self.edtBegDateSubParty.setCalendarPopup(True)
        self.edtBegDateSubParty.setObjectName(_fromUtf8("edtBegDateSubParty"))
        self.gridLayout_6.addWidget(self.edtBegDateSubParty, 2, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(108, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem2, 2, 5, 1, 1)
        self.label_2 = QtGui.QLabel(self.grbSubParty)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_6.addWidget(self.label_2, 2, 3, 1, 1)
        self.edtEndDateSubParty = CDateEdit(self.grbSubParty)
        self.edtEndDateSubParty.setObjectName(_fromUtf8("edtEndDateSubParty"))
        self.gridLayout_6.addWidget(self.edtEndDateSubParty, 2, 4, 1, 1)
        self.label_6 = QtGui.QLabel(self.grbSubParty)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_6.addWidget(self.label_6, 2, 1, 1, 1)
        self.cmbPersonSubParty = CPersonComboBoxEx(self.grbSubParty)
        self.cmbPersonSubParty.setObjectName(_fromUtf8("cmbPersonSubParty"))
        self.gridLayout_6.addWidget(self.cmbPersonSubParty, 1, 1, 1, 5)
        self.cmbOrgStructureSubParty = COrgStructureComboBox(self.grbSubParty)
        self.cmbOrgStructureSubParty.setObjectName(_fromUtf8("cmbOrgStructureSubParty"))
        self.gridLayout_6.addWidget(self.cmbOrgStructureSubParty, 0, 1, 1, 5)
        self.gridLayout.addWidget(self.grbSubParty, 1, 0, 1, 1)
        self.buttonBoxFilter = QtGui.QDialogButtonBox(self.grbTempInvalidFilter)
        self.buttonBoxFilter.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBoxFilter.setObjectName(_fromUtf8("buttonBoxFilter"))
        self.gridLayout.addWidget(self.buttonBoxFilter, 3, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 2, 0, 1, 1)
        self.splitter = QtGui.QSplitter(self.splitter_3)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tblBlankTempInvalidParty = CInDocTableView(self.splitter)
        self.tblBlankTempInvalidParty.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblBlankTempInvalidParty.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblBlankTempInvalidParty.setObjectName(_fromUtf8("tblBlankTempInvalidParty"))
        self.tblBlankTempInvalidMoving = CInDocTableView(self.splitter)
        self.tblBlankTempInvalidMoving.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblBlankTempInvalidMoving.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblBlankTempInvalidMoving.setObjectName(_fromUtf8("tblBlankTempInvalidMoving"))
        self.gridLayout_4.addWidget(self.splitter_3, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabTypeTempInvalid, _fromUtf8(""))
        self.tabTypeActions = QtGui.QWidget()
        self.tabTypeActions.setObjectName(_fromUtf8("tabTypeActions"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tabTypeActions)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.splitter_6 = QtGui.QSplitter(self.tabTypeActions)
        self.splitter_6.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_6.setObjectName(_fromUtf8("splitter_6"))
        self.splitter_5 = QtGui.QSplitter(self.splitter_6)
        self.splitter_5.setOrientation(QtCore.Qt.Vertical)
        self.splitter_5.setObjectName(_fromUtf8("splitter_5"))
        self.treeBlankTypeActions = CTreeView(self.splitter_5)
        self.treeBlankTypeActions.setObjectName(_fromUtf8("treeBlankTypeActions"))
        self.grbActionsFilter = QtGui.QGroupBox(self.splitter_5)
        self.grbActionsFilter.setObjectName(_fromUtf8("grbActionsFilter"))
        self.gridLayout_8 = QtGui.QGridLayout(self.grbActionsFilter)
        self.gridLayout_8.setMargin(4)
        self.gridLayout_8.setSpacing(4)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.grbPartyActions = QtGui.QGroupBox(self.grbActionsFilter)
        self.grbPartyActions.setObjectName(_fromUtf8("grbPartyActions"))
        self.gridLayout_7 = QtGui.QGridLayout(self.grbPartyActions)
        self.gridLayout_7.setMargin(4)
        self.gridLayout_7.setSpacing(4)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.lblSerialPartyActions = QtGui.QLabel(self.grbPartyActions)
        self.lblSerialPartyActions.setObjectName(_fromUtf8("lblSerialPartyActions"))
        self.gridLayout_7.addWidget(self.lblSerialPartyActions, 2, 0, 1, 1)
        self.lblPersonPartyActions = QtGui.QLabel(self.grbPartyActions)
        self.lblPersonPartyActions.setObjectName(_fromUtf8("lblPersonPartyActions"))
        self.gridLayout_7.addWidget(self.lblPersonPartyActions, 0, 0, 1, 1)
        self.lblDatePartyActions = QtGui.QLabel(self.grbPartyActions)
        self.lblDatePartyActions.setObjectName(_fromUtf8("lblDatePartyActions"))
        self.gridLayout_7.addWidget(self.lblDatePartyActions, 1, 0, 1, 1)
        self.lblNumberActions = QtGui.QLabel(self.grbPartyActions)
        self.lblNumberActions.setObjectName(_fromUtf8("lblNumberActions"))
        self.gridLayout_7.addWidget(self.lblNumberActions, 3, 0, 1, 1)
        self.edtNumberFromActions = QtGui.QSpinBox(self.grbPartyActions)
        self.edtNumberFromActions.setMaximum(99999999)
        self.edtNumberFromActions.setObjectName(_fromUtf8("edtNumberFromActions"))
        self.gridLayout_7.addWidget(self.edtNumberFromActions, 3, 2, 1, 1)
        self.labelActions = QtGui.QLabel(self.grbPartyActions)
        self.labelActions.setObjectName(_fromUtf8("labelActions"))
        self.gridLayout_7.addWidget(self.labelActions, 3, 3, 1, 1)
        self.label_3 = QtGui.QLabel(self.grbPartyActions)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_7.addWidget(self.label_3, 1, 1, 1, 1)
        self.edtBegDatePartyActions = CDateEdit(self.grbPartyActions)
        self.edtBegDatePartyActions.setCalendarPopup(True)
        self.edtBegDatePartyActions.setObjectName(_fromUtf8("edtBegDatePartyActions"))
        self.gridLayout_7.addWidget(self.edtBegDatePartyActions, 1, 2, 1, 1)
        self.labelActions_4 = QtGui.QLabel(self.grbPartyActions)
        self.labelActions_4.setObjectName(_fromUtf8("labelActions_4"))
        self.gridLayout_7.addWidget(self.labelActions_4, 1, 3, 1, 1)
        self.label_7 = QtGui.QLabel(self.grbPartyActions)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_7.addWidget(self.label_7, 3, 1, 1, 1)
        self.edtNumberToActions = QtGui.QSpinBox(self.grbPartyActions)
        self.edtNumberToActions.setMaximum(99999999)
        self.edtNumberToActions.setObjectName(_fromUtf8("edtNumberToActions"))
        self.gridLayout_7.addWidget(self.edtNumberToActions, 3, 4, 1, 2)
        spacerItem4 = QtGui.QSpacerItem(118, 13, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem4, 1, 6, 1, 2)
        self.edtSerialPartyActions = QtGui.QLineEdit(self.grbPartyActions)
        self.edtSerialPartyActions.setObjectName(_fromUtf8("edtSerialPartyActions"))
        self.gridLayout_7.addWidget(self.edtSerialPartyActions, 2, 1, 1, 7)
        self.cmbPersonPartyActions = CPersonComboBoxEx(self.grbPartyActions)
        self.cmbPersonPartyActions.setObjectName(_fromUtf8("cmbPersonPartyActions"))
        self.gridLayout_7.addWidget(self.cmbPersonPartyActions, 0, 1, 1, 7)
        spacerItem5 = QtGui.QSpacerItem(89, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem5, 3, 6, 1, 1)
        self.edtEndDatePartyActions = CDateEdit(self.grbPartyActions)
        self.edtEndDatePartyActions.setObjectName(_fromUtf8("edtEndDatePartyActions"))
        self.gridLayout_7.addWidget(self.edtEndDatePartyActions, 1, 4, 1, 2)
        self.gridLayout_8.addWidget(self.grbPartyActions, 0, 0, 1, 1)
        self.grbSubPartyActions = QtGui.QGroupBox(self.grbActionsFilter)
        self.grbSubPartyActions.setObjectName(_fromUtf8("grbSubPartyActions"))
        self.gridLayout_5 = QtGui.QGridLayout(self.grbSubPartyActions)
        self.gridLayout_5.setMargin(4)
        self.gridLayout_5.setSpacing(4)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.lblOrgStructureSubPartyActions = QtGui.QLabel(self.grbSubPartyActions)
        self.lblOrgStructureSubPartyActions.setObjectName(_fromUtf8("lblOrgStructureSubPartyActions"))
        self.gridLayout_5.addWidget(self.lblOrgStructureSubPartyActions, 0, 0, 1, 1)
        self.lblPersonSubPartyActions = QtGui.QLabel(self.grbSubPartyActions)
        self.lblPersonSubPartyActions.setObjectName(_fromUtf8("lblPersonSubPartyActions"))
        self.gridLayout_5.addWidget(self.lblPersonSubPartyActions, 1, 0, 1, 1)
        self.lblDateSubPartyActions = QtGui.QLabel(self.grbSubPartyActions)
        self.lblDateSubPartyActions.setObjectName(_fromUtf8("lblDateSubPartyActions"))
        self.gridLayout_5.addWidget(self.lblDateSubPartyActions, 2, 0, 1, 1)
        self.edtBegDateSubPartyActions = CDateEdit(self.grbSubPartyActions)
        self.edtBegDateSubPartyActions.setCalendarPopup(True)
        self.edtBegDateSubPartyActions.setObjectName(_fromUtf8("edtBegDateSubPartyActions"))
        self.gridLayout_5.addWidget(self.edtBegDateSubPartyActions, 2, 2, 1, 1)
        spacerItem6 = QtGui.QSpacerItem(108, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem6, 2, 5, 1, 1)
        self.label_4 = QtGui.QLabel(self.grbSubPartyActions)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_5.addWidget(self.label_4, 2, 3, 1, 1)
        self.edtEndDateSubPartyActions = CDateEdit(self.grbSubPartyActions)
        self.edtEndDateSubPartyActions.setObjectName(_fromUtf8("edtEndDateSubPartyActions"))
        self.gridLayout_5.addWidget(self.edtEndDateSubPartyActions, 2, 4, 1, 1)
        self.label_8 = QtGui.QLabel(self.grbSubPartyActions)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_5.addWidget(self.label_8, 2, 1, 1, 1)
        self.cmbOrgStructureSubPartyActions = COrgStructureComboBox(self.grbSubPartyActions)
        self.cmbOrgStructureSubPartyActions.setObjectName(_fromUtf8("cmbOrgStructureSubPartyActions"))
        self.gridLayout_5.addWidget(self.cmbOrgStructureSubPartyActions, 0, 1, 1, 5)
        self.cmbPersonSubPartyActions = CPersonComboBoxEx(self.grbSubPartyActions)
        self.cmbPersonSubPartyActions.setObjectName(_fromUtf8("cmbPersonSubPartyActions"))
        self.gridLayout_5.addWidget(self.cmbPersonSubPartyActions, 1, 1, 1, 5)
        self.gridLayout_8.addWidget(self.grbSubPartyActions, 1, 0, 1, 1)
        self.buttonBoxFilterActions = QtGui.QDialogButtonBox(self.grbActionsFilter)
        self.buttonBoxFilterActions.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBoxFilterActions.setObjectName(_fromUtf8("buttonBoxFilterActions"))
        self.gridLayout_8.addWidget(self.buttonBoxFilterActions, 3, 0, 1, 1)
        spacerItem7 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_8.addItem(spacerItem7, 2, 0, 1, 1)
        self.splitter_4 = QtGui.QSplitter(self.splitter_6)
        self.splitter_4.setOrientation(QtCore.Qt.Vertical)
        self.splitter_4.setObjectName(_fromUtf8("splitter_4"))
        self.tblBlankActionsParty = CInDocTableView(self.splitter_4)
        self.tblBlankActionsParty.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblBlankActionsParty.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblBlankActionsParty.setObjectName(_fromUtf8("tblBlankActionsParty"))
        self.tblBlankActionsMoving = CInDocTableView(self.splitter_4)
        self.tblBlankActionsMoving.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblBlankActionsMoving.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblBlankActionsMoving.setObjectName(_fromUtf8("tblBlankActionsMoving"))
        self.gridLayout_2.addWidget(self.splitter_6, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabTypeActions, _fromUtf8(""))
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(BlanksDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(BlanksDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), BlanksDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), BlanksDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(BlanksDialog)

    def retranslateUi(self, BlanksDialog):
        BlanksDialog.setWindowTitle(_translate("BlanksDialog", "Учет бланков", None))
        self.grbTempInvalidFilter.setTitle(_translate("BlanksDialog", "Фильтр", None))
        self.grbParty.setTitle(_translate("BlanksDialog", "Партия", None))
        self.lblPersonParty.setText(_translate("BlanksDialog", "Получатель", None))
        self.lblDateParty.setText(_translate("BlanksDialog", "Дата", None))
        self.lblSerialParty.setText(_translate("BlanksDialog", "Серия", None))
        self.lblNumber.setText(_translate("BlanksDialog", "Номер", None))
        self.labelActions_3.setText(_translate("BlanksDialog", "с", None))
        self.label_5.setText(_translate("BlanksDialog", "с", None))
        self.label.setText(_translate("BlanksDialog", "по", None))
        self.labelActions_2.setText(_translate("BlanksDialog", "по", None))
        self.grbSubParty.setTitle(_translate("BlanksDialog", "Подпартия", None))
        self.lblOrgStructureSubParty.setText(_translate("BlanksDialog", "Подразделение", None))
        self.lblPersonSubParty.setText(_translate("BlanksDialog", "Персона", None))
        self.lblDateSubParty.setText(_translate("BlanksDialog", "Дата", None))
        self.label_2.setText(_translate("BlanksDialog", "по", None))
        self.label_6.setText(_translate("BlanksDialog", "с", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTypeTempInvalid), _translate("BlanksDialog", "ВУТ", None))
        self.grbActionsFilter.setTitle(_translate("BlanksDialog", "Фильтр", None))
        self.grbPartyActions.setTitle(_translate("BlanksDialog", "Партия", None))
        self.lblSerialPartyActions.setText(_translate("BlanksDialog", "Серия", None))
        self.lblPersonPartyActions.setText(_translate("BlanksDialog", "Получатель", None))
        self.lblDatePartyActions.setText(_translate("BlanksDialog", "Дата", None))
        self.lblNumberActions.setText(_translate("BlanksDialog", "Номер", None))
        self.labelActions.setText(_translate("BlanksDialog", "по", None))
        self.label_3.setText(_translate("BlanksDialog", "с", None))
        self.labelActions_4.setText(_translate("BlanksDialog", "по", None))
        self.label_7.setText(_translate("BlanksDialog", "с", None))
        self.grbSubPartyActions.setTitle(_translate("BlanksDialog", "Подпартия", None))
        self.lblOrgStructureSubPartyActions.setText(_translate("BlanksDialog", "Подразделение", None))
        self.lblPersonSubPartyActions.setText(_translate("BlanksDialog", "Персона", None))
        self.lblDateSubPartyActions.setText(_translate("BlanksDialog", "Дата", None))
        self.label_4.setText(_translate("BlanksDialog", "по", None))
        self.label_8.setText(_translate("BlanksDialog", "с", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTypeActions), _translate("BlanksDialog", "Прочие", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from library.InDocTable import CInDocTableView
from library.TreeView import CTreeView
