# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBEquipmentEditor.ui'
#
# Created: Fri Jun 15 12:17:21 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RBEquipmentEditorDialog(object):
    def setupUi(self, RBEquipmentEditorDialog):
        RBEquipmentEditorDialog.setObjectName(_fromUtf8("RBEquipmentEditorDialog"))
        RBEquipmentEditorDialog.resize(511, 413)
        self.gridLayout_2 = QtGui.QGridLayout(RBEquipmentEditorDialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.buttonBox = QtGui.QDialogButtonBox(RBEquipmentEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(RBEquipmentEditorDialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabEquipment = QtGui.QWidget()
        self.tabEquipment.setObjectName(_fromUtf8("tabEquipment"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tabEquipment)
        self.gridLayout_3.setMargin(4)
        self.gridLayout_3.setSpacing(4)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lblCode = QtGui.QLabel(self.tabEquipment)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout_3.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(self.tabEquipment)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout_3.addWidget(self.edtCode, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(self.tabEquipment)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout_3.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(self.tabEquipment)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout_3.addWidget(self.edtName, 1, 1, 1, 1)
        self.lblEquipmentType = QtGui.QLabel(self.tabEquipment)
        self.lblEquipmentType.setObjectName(_fromUtf8("lblEquipmentType"))
        self.gridLayout_3.addWidget(self.lblEquipmentType, 2, 0, 1, 1)
        self.cmbEquipmentType = CRBComboBox(self.tabEquipment)
        self.cmbEquipmentType.setObjectName(_fromUtf8("cmbEquipmentType"))
        self.gridLayout_3.addWidget(self.cmbEquipmentType, 2, 1, 1, 1)
        self.lblInventoryNumber = QtGui.QLabel(self.tabEquipment)
        self.lblInventoryNumber.setObjectName(_fromUtf8("lblInventoryNumber"))
        self.gridLayout_3.addWidget(self.lblInventoryNumber, 5, 0, 1, 1)
        self.edtInventoryNumber = QtGui.QLineEdit(self.tabEquipment)
        self.edtInventoryNumber.setObjectName(_fromUtf8("edtInventoryNumber"))
        self.gridLayout_3.addWidget(self.edtInventoryNumber, 5, 1, 1, 1)
        self.lblModel = QtGui.QLabel(self.tabEquipment)
        self.lblModel.setObjectName(_fromUtf8("lblModel"))
        self.gridLayout_3.addWidget(self.lblModel, 6, 0, 1, 1)
        self.edtModel = QtGui.QLineEdit(self.tabEquipment)
        self.edtModel.setObjectName(_fromUtf8("edtModel"))
        self.gridLayout_3.addWidget(self.edtModel, 6, 1, 1, 1)
        self.lblReleaseDate = QtGui.QLabel(self.tabEquipment)
        self.lblReleaseDate.setObjectName(_fromUtf8("lblReleaseDate"))
        self.gridLayout_3.addWidget(self.lblReleaseDate, 7, 0, 1, 1)
        self.edtReleaseDate = CDateEdit(self.tabEquipment)
        self.edtReleaseDate.setObjectName(_fromUtf8("edtReleaseDate"))
        self.gridLayout_3.addWidget(self.edtReleaseDate, 7, 1, 1, 1)
        self.lblStartupDate = QtGui.QLabel(self.tabEquipment)
        self.lblStartupDate.setObjectName(_fromUtf8("lblStartupDate"))
        self.gridLayout_3.addWidget(self.lblStartupDate, 8, 0, 1, 1)
        self.edtStartupDate = CDateEdit(self.tabEquipment)
        self.edtStartupDate.setObjectName(_fromUtf8("edtStartupDate"))
        self.gridLayout_3.addWidget(self.edtStartupDate, 8, 1, 1, 1)
        self.lblStatus = QtGui.QLabel(self.tabEquipment)
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.gridLayout_3.addWidget(self.lblStatus, 9, 0, 1, 1)
        self.cmbStatus = QtGui.QComboBox(self.tabEquipment)
        self.cmbStatus.setObjectName(_fromUtf8("cmbStatus"))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.cmbStatus.addItem(_fromUtf8(""))
        self.gridLayout_3.addWidget(self.cmbStatus, 9, 1, 1, 1)
        self.lblEmploymentTerm = QtGui.QLabel(self.tabEquipment)
        self.lblEmploymentTerm.setObjectName(_fromUtf8("lblEmploymentTerm"))
        self.gridLayout_3.addWidget(self.lblEmploymentTerm, 10, 0, 1, 1)
        self.edtEmploymentTerm = QtGui.QSpinBox(self.tabEquipment)
        self.edtEmploymentTerm.setObjectName(_fromUtf8("edtEmploymentTerm"))
        self.gridLayout_3.addWidget(self.edtEmploymentTerm, 10, 1, 1, 1)
        self.lblWarrantyTerm = QtGui.QLabel(self.tabEquipment)
        self.lblWarrantyTerm.setObjectName(_fromUtf8("lblWarrantyTerm"))
        self.gridLayout_3.addWidget(self.lblWarrantyTerm, 11, 0, 1, 1)
        self.edtWarrantyTerm = QtGui.QSpinBox(self.tabEquipment)
        self.edtWarrantyTerm.setObjectName(_fromUtf8("edtWarrantyTerm"))
        self.gridLayout_3.addWidget(self.edtWarrantyTerm, 11, 1, 1, 1)
        self.lblMaintenancePeriod = QtGui.QLabel(self.tabEquipment)
        self.lblMaintenancePeriod.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblMaintenancePeriod.setFrameShadow(QtGui.QFrame.Plain)
        self.lblMaintenancePeriod.setLineWidth(1)
        self.lblMaintenancePeriod.setObjectName(_fromUtf8("lblMaintenancePeriod"))
        self.gridLayout_3.addWidget(self.lblMaintenancePeriod, 12, 0, 1, 1)
        self.widget = QtGui.QWidget(self.tabEquipment)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout.setMargin(0)
        self.gridLayout.setMargin(0)
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtMaintenancePeriod = QtGui.QSpinBox(self.widget)
        self.edtMaintenancePeriod.setObjectName(_fromUtf8("edtMaintenancePeriod"))
        self.gridLayout.addWidget(self.edtMaintenancePeriod, 0, 0, 1, 1)
        self.lblMaintenanceSingleInPeriod = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMaintenanceSingleInPeriod.sizePolicy().hasHeightForWidth())
        self.lblMaintenanceSingleInPeriod.setSizePolicy(sizePolicy)
        self.lblMaintenanceSingleInPeriod.setObjectName(_fromUtf8("lblMaintenanceSingleInPeriod"))
        self.gridLayout.addWidget(self.lblMaintenanceSingleInPeriod, 0, 1, 1, 1)
        self.cmbMaintenanceSingleInPeriod = QtGui.QComboBox(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbMaintenanceSingleInPeriod.sizePolicy().hasHeightForWidth())
        self.cmbMaintenanceSingleInPeriod.setSizePolicy(sizePolicy)
        self.cmbMaintenanceSingleInPeriod.setObjectName(_fromUtf8("cmbMaintenanceSingleInPeriod"))
        self.cmbMaintenanceSingleInPeriod.addItem(_fromUtf8(""))
        self.cmbMaintenanceSingleInPeriod.addItem(_fromUtf8(""))
        self.cmbMaintenanceSingleInPeriod.addItem(_fromUtf8(""))
        self.cmbMaintenanceSingleInPeriod.addItem(_fromUtf8(""))
        self.cmbMaintenanceSingleInPeriod.addItem(_fromUtf8(""))
        self.cmbMaintenanceSingleInPeriod.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbMaintenanceSingleInPeriod, 0, 2, 1, 1)
        self.gridLayout_3.addWidget(self.widget, 12, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 14, 1, 1, 1)
        self.lblTripod = QtGui.QLabel(self.tabEquipment)
        self.lblTripod.setObjectName(_fromUtf8("lblTripod"))
        self.gridLayout_3.addWidget(self.lblTripod, 3, 0, 1, 1)
        self.lblTripodCapacity = QtGui.QLabel(self.tabEquipment)
        self.lblTripodCapacity.setObjectName(_fromUtf8("lblTripodCapacity"))
        self.gridLayout_3.addWidget(self.lblTripodCapacity, 4, 0, 1, 1)
        self.edtTripod = QtGui.QSpinBox(self.tabEquipment)
        self.edtTripod.setMaximum(100000)
        self.edtTripod.setObjectName(_fromUtf8("edtTripod"))
        self.gridLayout_3.addWidget(self.edtTripod, 3, 1, 1, 1)
        self.edtTripodCapacity = QtGui.QSpinBox(self.tabEquipment)
        self.edtTripodCapacity.setMaximum(100000)
        self.edtTripodCapacity.setObjectName(_fromUtf8("edtTripodCapacity"))
        self.gridLayout_3.addWidget(self.edtTripodCapacity, 4, 1, 1, 1)
        self.lblManufacturer = QtGui.QLabel(self.tabEquipment)
        self.lblManufacturer.setObjectName(_fromUtf8("lblManufacturer"))
        self.gridLayout_3.addWidget(self.lblManufacturer, 13, 0, 1, 1)
        self.edtManufacturer = QtGui.QLineEdit(self.tabEquipment)
        self.edtManufacturer.setObjectName(_fromUtf8("edtManufacturer"))
        self.gridLayout_3.addWidget(self.edtManufacturer, 13, 1, 1, 1)
        self.tabWidget.addTab(self.tabEquipment, _fromUtf8(""))
        self.tabInterface = QtGui.QWidget()
        self.tabInterface.setObjectName(_fromUtf8("tabInterface"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tabInterface)
        self.gridLayout_5.setMargin(4)
        self.gridLayout_5.setSpacing(4)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.lblProtocol = QtGui.QLabel(self.tabInterface)
        self.lblProtocol.setObjectName(_fromUtf8("lblProtocol"))
        self.gridLayout_5.addWidget(self.lblProtocol, 0, 0, 1, 1)
        self.cmbProtocol = QtGui.QComboBox(self.tabInterface)
        self.cmbProtocol.setObjectName(_fromUtf8("cmbProtocol"))
        self.cmbProtocol.addItem(_fromUtf8(""))
        self.cmbProtocol.addItem(_fromUtf8(""))
        self.gridLayout_5.addWidget(self.cmbProtocol, 0, 1, 1, 1)
        self.lblAddress = QtGui.QLabel(self.tabInterface)
        self.lblAddress.setObjectName(_fromUtf8("lblAddress"))
        self.gridLayout_5.addWidget(self.lblAddress, 1, 0, 1, 1)
        self.edtAddress = QtGui.QLineEdit(self.tabInterface)
        self.edtAddress.setObjectName(_fromUtf8("edtAddress"))
        self.gridLayout_5.addWidget(self.edtAddress, 1, 1, 1, 1)
        self.lblOwnName = QtGui.QLabel(self.tabInterface)
        self.lblOwnName.setObjectName(_fromUtf8("lblOwnName"))
        self.gridLayout_5.addWidget(self.lblOwnName, 2, 0, 1, 1)
        self.edtOwnName = QtGui.QLineEdit(self.tabInterface)
        self.edtOwnName.setObjectName(_fromUtf8("edtOwnName"))
        self.gridLayout_5.addWidget(self.edtOwnName, 2, 1, 1, 1)
        self.lblLabName = QtGui.QLabel(self.tabInterface)
        self.lblLabName.setObjectName(_fromUtf8("lblLabName"))
        self.gridLayout_5.addWidget(self.lblLabName, 3, 0, 1, 1)
        self.edtLabName = QtGui.QLineEdit(self.tabInterface)
        self.edtLabName.setObjectName(_fromUtf8("edtLabName"))
        self.gridLayout_5.addWidget(self.edtLabName, 3, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 239, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_5.addItem(spacerItem1, 4, 0, 1, 1)
        self.tabWidget.addTab(self.tabInterface, _fromUtf8(""))
        self.tabTests = QtGui.QWidget()
        self.tabTests.setObjectName(_fromUtf8("tabTests"))
        self.gridLayout_4 = QtGui.QGridLayout(self.tabTests)
        self.gridLayout_4.setMargin(4)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.tblTests = CInDocTableView(self.tabTests)
        self.tblTests.setObjectName(_fromUtf8("tblTests"))
        self.gridLayout_4.addWidget(self.tblTests, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabTests, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.tabWidget, 1, 0, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblEquipmentType.setBuddy(self.cmbEquipmentType)
        self.lblInventoryNumber.setBuddy(self.edtInventoryNumber)
        self.lblModel.setBuddy(self.edtModel)
        self.lblReleaseDate.setBuddy(self.edtReleaseDate)
        self.lblStartupDate.setBuddy(self.edtStartupDate)
        self.lblStatus.setBuddy(self.cmbStatus)
        self.lblEmploymentTerm.setBuddy(self.edtEmploymentTerm)
        self.lblWarrantyTerm.setBuddy(self.edtWarrantyTerm)
        self.lblMaintenancePeriod.setBuddy(self.edtMaintenancePeriod)
        self.lblMaintenanceSingleInPeriod.setBuddy(self.cmbMaintenanceSingleInPeriod)
        self.lblTripod.setBuddy(self.edtTripod)
        self.lblTripodCapacity.setBuddy(self.edtTripodCapacity)
        self.lblManufacturer.setBuddy(self.edtManufacturer)
        self.lblProtocol.setBuddy(self.cmbProtocol)
        self.lblAddress.setBuddy(self.edtAddress)
        self.lblOwnName.setBuddy(self.edtOwnName)
        self.lblLabName.setBuddy(self.edtLabName)

        self.retranslateUi(RBEquipmentEditorDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBEquipmentEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBEquipmentEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RBEquipmentEditorDialog)
        RBEquipmentEditorDialog.setTabOrder(self.tabWidget, self.edtCode)
        RBEquipmentEditorDialog.setTabOrder(self.edtCode, self.edtName)
        RBEquipmentEditorDialog.setTabOrder(self.edtName, self.cmbEquipmentType)
        RBEquipmentEditorDialog.setTabOrder(self.cmbEquipmentType, self.edtTripod)
        RBEquipmentEditorDialog.setTabOrder(self.edtTripod, self.edtTripodCapacity)
        RBEquipmentEditorDialog.setTabOrder(self.edtTripodCapacity, self.edtInventoryNumber)
        RBEquipmentEditorDialog.setTabOrder(self.edtInventoryNumber, self.edtModel)
        RBEquipmentEditorDialog.setTabOrder(self.edtModel, self.edtReleaseDate)
        RBEquipmentEditorDialog.setTabOrder(self.edtReleaseDate, self.edtStartupDate)
        RBEquipmentEditorDialog.setTabOrder(self.edtStartupDate, self.cmbStatus)
        RBEquipmentEditorDialog.setTabOrder(self.cmbStatus, self.edtEmploymentTerm)
        RBEquipmentEditorDialog.setTabOrder(self.edtEmploymentTerm, self.edtWarrantyTerm)
        RBEquipmentEditorDialog.setTabOrder(self.edtWarrantyTerm, self.edtMaintenancePeriod)
        RBEquipmentEditorDialog.setTabOrder(self.edtMaintenancePeriod, self.cmbMaintenanceSingleInPeriod)
        RBEquipmentEditorDialog.setTabOrder(self.cmbMaintenanceSingleInPeriod, self.edtManufacturer)
        RBEquipmentEditorDialog.setTabOrder(self.edtManufacturer, self.cmbProtocol)
        RBEquipmentEditorDialog.setTabOrder(self.cmbProtocol, self.edtAddress)
        RBEquipmentEditorDialog.setTabOrder(self.edtAddress, self.edtOwnName)
        RBEquipmentEditorDialog.setTabOrder(self.edtOwnName, self.edtLabName)
        RBEquipmentEditorDialog.setTabOrder(self.edtLabName, self.tblTests)
        RBEquipmentEditorDialog.setTabOrder(self.tblTests, self.buttonBox)

    def retranslateUi(self, RBEquipmentEditorDialog):
        RBEquipmentEditorDialog.setWindowTitle(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEquipmentType.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Т&ип оборудования", None, QtGui.QApplication.UnicodeUTF8))
        self.lblInventoryNumber.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "&Инвентаризационный номер", None, QtGui.QApplication.UnicodeUTF8))
        self.lblModel.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Мо&дель", None, QtGui.QApplication.UnicodeUTF8))
        self.lblReleaseDate.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Дата &выпуска", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStartupDate.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Дата ввода в &эксплуатацию", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStatus.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "&Статус", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbStatus.setItemText(0, QtGui.QApplication.translate("RBEquipmentEditorDialog", "Не работает", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbStatus.setItemText(1, QtGui.QApplication.translate("RBEquipmentEditorDialog", "Работает", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEmploymentTerm.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Срок службы", None, QtGui.QApplication.UnicodeUTF8))
        self.lblWarrantyTerm.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Срок гарантии", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMaintenancePeriod.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Период ТО (месяцев)", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMaintenanceSingleInPeriod.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "или раз в", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbMaintenanceSingleInPeriod.setItemText(0, QtGui.QApplication.translate("RBEquipmentEditorDialog", "Нет", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbMaintenanceSingleInPeriod.setItemText(1, QtGui.QApplication.translate("RBEquipmentEditorDialog", "Неделя", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbMaintenanceSingleInPeriod.setItemText(2, QtGui.QApplication.translate("RBEquipmentEditorDialog", "Месяц", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbMaintenanceSingleInPeriod.setItemText(3, QtGui.QApplication.translate("RBEquipmentEditorDialog", "Квартал", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbMaintenanceSingleInPeriod.setItemText(4, QtGui.QApplication.translate("RBEquipmentEditorDialog", "Полугодие", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbMaintenanceSingleInPeriod.setItemText(5, QtGui.QApplication.translate("RBEquipmentEditorDialog", "Год", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTripod.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Количество &штативов", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTripodCapacity.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Количество &мест в штативе", None, QtGui.QApplication.UnicodeUTF8))
        self.lblManufacturer.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Производитель", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabEquipment), QtGui.QApplication.translate("RBEquipmentEditorDialog", "&Оборудование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblProtocol.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "&Протокол", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbProtocol.setItemText(0, QtGui.QApplication.translate("RBEquipmentEditorDialog", "hl2.5 через SOAP по предложению AKSi", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbProtocol.setItemText(1, QtGui.QApplication.translate("RBEquipmentEditorDialog", "Обмен файлами по ASTM E-1381 и E-1394", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAddress.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "&Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.edtAddress.setToolTip(QtGui.QApplication.translate("RBEquipmentEditorDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Tahoma\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">URL для обмена базирующегося на SOAP;</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">JSON-описание параметров соединения,</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">например</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">{</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">    &quot;<span style=\" font-weight:600;\">dir</span>&quot;:&quot;/var/lab/exchange/out&quot;,</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">    &quot;<span style=\" font-weight:600;\">prefix</span>&quot;:&quot;req&quot;,</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">    &quot;<span style=\" font-weight:600;\">dataExt</span>&quot;:&quot;.req&quot;,</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">    &quot;<span style=\" font-weight:600;\">signalExt</span>&quot;:&quot;.ok&quot;, </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">    &quot;<span style=\" font-weight:600;\">encoding</span>&quot;:&quot;cp1251&quot;</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">}</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">для файлового обмена по протоколу ASTM E-1381</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOwnName.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Наименование &своей стороны", None, QtGui.QApplication.UnicodeUTF8))
        self.edtOwnName.setToolTip(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Если про протоколу требуется \"представиться\"", None, QtGui.QApplication.UnicodeUTF8))
        self.lblLabName.setText(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Наименование стороны &ЛИС", None, QtGui.QApplication.UnicodeUTF8))
        self.edtLabName.setToolTip(QtGui.QApplication.translate("RBEquipmentEditorDialog", "Если по протоколу требуется \"назвать\" другую сторону", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabInterface), QtGui.QApplication.translate("RBEquipmentEditorDialog", "&Интерфейс", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTests), QtGui.QApplication.translate("RBEquipmentEditorDialog", "&Тесты", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    RBEquipmentEditorDialog = QtGui.QDialog()
    ui = Ui_RBEquipmentEditorDialog()
    ui.setupUi(RBEquipmentEditorDialog)
    RBEquipmentEditorDialog.show()
    sys.exit(app.exec_())
