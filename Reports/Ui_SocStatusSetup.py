# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SocStatusSetup.ui'
#
# Created: Wed Mar 26 19:26:05 2014
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

class Ui_SocStatusSetupDialog(object):
    def setupUi(self, SocStatusSetupDialog):
        SocStatusSetupDialog.setObjectName(_fromUtf8("SocStatusSetupDialog"))
        SocStatusSetupDialog.resize(607, 403)
        self.gridLayout_2 = QtGui.QGridLayout(SocStatusSetupDialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.edtBegDate = CDateEdit(SocStatusSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout_2.addWidget(self.edtBegDate, 0, 3, 1, 2)
        spacerItem = QtGui.QSpacerItem(58, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 5, 1, 2)
        self.lblEndDate = QtGui.QLabel(SocStatusSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout_2.addWidget(self.lblEndDate, 1, 2, 1, 1)
        self.groupBox = QtGui.QGroupBox(SocStatusSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.btnStatusInPeriod = QtGui.QRadioButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnStatusInPeriod.sizePolicy().hasHeightForWidth())
        self.btnStatusInPeriod.setSizePolicy(sizePolicy)
        self.btnStatusInPeriod.setChecked(True)
        self.btnStatusInPeriod.setObjectName(_fromUtf8("btnStatusInPeriod"))
        self.verticalLayout.addWidget(self.btnStatusInPeriod)
        self.btnStatusStart = QtGui.QRadioButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnStatusStart.sizePolicy().hasHeightForWidth())
        self.btnStatusStart.setSizePolicy(sizePolicy)
        self.btnStatusStart.setObjectName(_fromUtf8("btnStatusStart"))
        self.verticalLayout.addWidget(self.btnStatusStart)
        self.btnStatusFinish = QtGui.QRadioButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnStatusFinish.sizePolicy().hasHeightForWidth())
        self.btnStatusFinish.setSizePolicy(sizePolicy)
        self.btnStatusFinish.setObjectName(_fromUtf8("btnStatusFinish"))
        self.verticalLayout.addWidget(self.btnStatusFinish)
        self.gridLayout_2.addWidget(self.groupBox, 2, 2, 1, 5)
        self.frmAge = QtGui.QFrame(SocStatusSetupDialog)
        self.frmAge.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAge.setFrameShadow(QtGui.QFrame.Raised)
        self.frmAge.setObjectName(_fromUtf8("frmAge"))
        self._2 = QtGui.QHBoxLayout(self.frmAge)
        self._2.setSpacing(4)
        self._2.setMargin(0)
        self._2.setObjectName(_fromUtf8("_2"))
        self.edtAgeFrom = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeFrom.sizePolicy().hasHeightForWidth())
        self.edtAgeFrom.setSizePolicy(sizePolicy)
        self.edtAgeFrom.setMaximum(150)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self._2.addWidget(self.edtAgeFrom)
        self.lblAgeTo = QtGui.QLabel(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblAgeTo.sizePolicy().hasHeightForWidth())
        self.lblAgeTo.setSizePolicy(sizePolicy)
        self.lblAgeTo.setObjectName(_fromUtf8("lblAgeTo"))
        self._2.addWidget(self.lblAgeTo)
        self.edtAgeTo = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeTo.sizePolicy().hasHeightForWidth())
        self.edtAgeTo.setSizePolicy(sizePolicy)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self._2.addWidget(self.edtAgeTo)
        self.lblAgeYears = QtGui.QLabel(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblAgeYears.sizePolicy().hasHeightForWidth())
        self.lblAgeYears.setSizePolicy(sizePolicy)
        self.lblAgeYears.setObjectName(_fromUtf8("lblAgeYears"))
        self._2.addWidget(self.lblAgeYears)
        self.gridLayout_2.addWidget(self.frmAge, 5, 3, 1, 3)
        self.grbOrgStructure = QtGui.QGroupBox(SocStatusSetupDialog)
        self.grbOrgStructure.setCheckable(True)
        self.grbOrgStructure.setChecked(False)
        self.grbOrgStructure.setObjectName(_fromUtf8("grbOrgStructure"))
        self.gridLayout = QtGui.QGridLayout(self.grbOrgStructure)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblOrgStructure = QtGui.QLabel(self.grbOrgStructure)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 0, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(self.grbOrgStructure)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 0, 1, 1, 1)
        self.lblAreaAddressType = QtGui.QLabel(self.grbOrgStructure)
        self.lblAreaAddressType.setObjectName(_fromUtf8("lblAreaAddressType"))
        self.gridLayout.addWidget(self.lblAreaAddressType, 1, 0, 1, 1)
        self.cmbAreaAddressType = QtGui.QComboBox(self.grbOrgStructure)
        self.cmbAreaAddressType.setObjectName(_fromUtf8("cmbAreaAddressType"))
        self.cmbAreaAddressType.addItem(_fromUtf8(""))
        self.cmbAreaAddressType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbAreaAddressType, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.grbOrgStructure, 6, 2, 1, 5)
        self.treeItems = CTreeView(SocStatusSetupDialog)
        self.treeItems.setObjectName(_fromUtf8("treeItems"))
        self.gridLayout_2.addWidget(self.treeItems, 0, 0, 13, 1)
        self.lblBegDate = QtGui.QLabel(SocStatusSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout_2.addWidget(self.lblBegDate, 0, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(58, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 1, 5, 1, 2)
        self.edtEndDate = CDateEdit(SocStatusSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout_2.addWidget(self.edtEndDate, 1, 3, 1, 2)
        self.chkOnlyPermanentAttach = QtGui.QCheckBox(SocStatusSetupDialog)
        self.chkOnlyPermanentAttach.setObjectName(_fromUtf8("chkOnlyPermanentAttach"))
        self.gridLayout_2.addWidget(self.chkOnlyPermanentAttach, 3, 2, 1, 5)
        self.cmbSex = QtGui.QComboBox(SocStatusSetupDialog)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.cmbSex, 4, 3, 1, 1)
        self.lblSex = QtGui.QLabel(SocStatusSetupDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout_2.addWidget(self.lblSex, 4, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(96, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 4, 4, 1, 3)
        self.lblAge = QtGui.QLabel(SocStatusSetupDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout_2.addWidget(self.lblAge, 5, 2, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(4, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 5, 6, 1, 1)
        self.chkAddMKB = QtGui.QCheckBox(SocStatusSetupDialog)
        self.chkAddMKB.setObjectName(_fromUtf8("chkAddMKB"))
        self.gridLayout_2.addWidget(self.chkAddMKB, 8, 2, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(SocStatusSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 13, 0, 1, 7)
        self.chkGroupBySocStatus = QtGui.QCheckBox(SocStatusSetupDialog)
        self.chkGroupBySocStatus.setObjectName(_fromUtf8("chkGroupBySocStatus"))
        self.gridLayout_2.addWidget(self.chkGroupBySocStatus, 10, 2, 1, 2)
        spacerItem4 = QtGui.QSpacerItem(20, 87, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem4, 12, 2, 1, 5)
        self.chkAddDeathDate = QtGui.QCheckBox(SocStatusSetupDialog)
        self.chkAddDeathDate.setObjectName(_fromUtf8("chkAddDeathDate"))
        self.gridLayout_2.addWidget(self.chkAddDeathDate, 9, 2, 1, 2)
        self.lstItems = CRBListBox(SocStatusSetupDialog)
        self.lstItems.setObjectName(_fromUtf8("lstItems"))
        self.gridLayout_2.addWidget(self.lstItems, 0, 1, 13, 1)
        self.chkOutcome = QtGui.QCheckBox(SocStatusSetupDialog)
        self.chkOutcome.setObjectName(_fromUtf8("chkOutcome"))
        self.gridLayout_2.addWidget(self.chkOutcome, 11, 2, 1, 1)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblAgeTo.setBuddy(self.edtAgeTo)
        self.lblAgeYears.setBuddy(self.edtAgeTo)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblAge.setBuddy(self.edtAgeFrom)

        self.retranslateUi(SocStatusSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SocStatusSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SocStatusSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SocStatusSetupDialog)
        SocStatusSetupDialog.setTabOrder(self.treeItems, self.edtBegDate)
        SocStatusSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        SocStatusSetupDialog.setTabOrder(self.edtEndDate, self.btnStatusInPeriod)
        SocStatusSetupDialog.setTabOrder(self.btnStatusInPeriod, self.btnStatusStart)
        SocStatusSetupDialog.setTabOrder(self.btnStatusStart, self.btnStatusFinish)
        SocStatusSetupDialog.setTabOrder(self.btnStatusFinish, self.chkOnlyPermanentAttach)
        SocStatusSetupDialog.setTabOrder(self.chkOnlyPermanentAttach, self.cmbSex)
        SocStatusSetupDialog.setTabOrder(self.cmbSex, self.edtAgeFrom)
        SocStatusSetupDialog.setTabOrder(self.edtAgeFrom, self.edtAgeTo)
        SocStatusSetupDialog.setTabOrder(self.edtAgeTo, self.grbOrgStructure)
        SocStatusSetupDialog.setTabOrder(self.grbOrgStructure, self.cmbOrgStructure)
        SocStatusSetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbAreaAddressType)
        SocStatusSetupDialog.setTabOrder(self.cmbAreaAddressType, self.chkAddMKB)
        SocStatusSetupDialog.setTabOrder(self.chkAddMKB, self.chkGroupBySocStatus)
        SocStatusSetupDialog.setTabOrder(self.chkGroupBySocStatus, self.buttonBox)

    def retranslateUi(self, SocStatusSetupDialog):
        SocStatusSetupDialog.setWindowTitle(_translate("SocStatusSetupDialog", "Dialog", None))
        self.lblEndDate.setText(_translate("SocStatusSetupDialog", "Дата &окончания периода", None))
        self.groupBox.setTitle(_translate("SocStatusSetupDialog", "способ фильтрации", None))
        self.btnStatusInPeriod.setText(_translate("SocStatusSetupDialog", "статус присутствует в периоде", None))
        self.btnStatusStart.setText(_translate("SocStatusSetupDialog", "статус начал действовать в периоде", None))
        self.btnStatusFinish.setText(_translate("SocStatusSetupDialog", "статус прекратил действовать в периоде", None))
        self.lblAgeTo.setText(_translate("SocStatusSetupDialog", "по", None))
        self.lblAgeYears.setText(_translate("SocStatusSetupDialog", "лет", None))
        self.grbOrgStructure.setTitle(_translate("SocStatusSetupDialog", "зона обслуживания", None))
        self.lblOrgStructure.setText(_translate("SocStatusSetupDialog", "Подразделение", None))
        self.lblAreaAddressType.setText(_translate("SocStatusSetupDialog", "Участок по адресу", None))
        self.cmbAreaAddressType.setItemText(0, _translate("SocStatusSetupDialog", "проживания", None))
        self.cmbAreaAddressType.setItemText(1, _translate("SocStatusSetupDialog", "регистрации", None))
        self.lblBegDate.setText(_translate("SocStatusSetupDialog", "Дата &начала периода", None))
        self.chkOnlyPermanentAttach.setText(_translate("SocStatusSetupDialog", "&Прикреплённые к базовому ЛПУ", None))
        self.cmbSex.setItemText(1, _translate("SocStatusSetupDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("SocStatusSetupDialog", "Ж", None))
        self.lblSex.setText(_translate("SocStatusSetupDialog", "По&л", None))
        self.lblAge.setText(_translate("SocStatusSetupDialog", "Возраст с", None))
        self.chkAddMKB.setText(_translate("SocStatusSetupDialog", "Добавить графу \"Заболевание\"", None))
        self.chkGroupBySocStatus.setText(_translate("SocStatusSetupDialog", "Группировать по соц. статусу", None))
        self.chkAddDeathDate.setText(_translate("SocStatusSetupDialog", "Добавить графу \"Дата смерти\"", None))
        self.chkOutcome.setText(_translate("SocStatusSetupDialog", "Исключить выбывших", None))

from library.RBListBox import CRBListBox
from library.TreeView import CTreeView
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
