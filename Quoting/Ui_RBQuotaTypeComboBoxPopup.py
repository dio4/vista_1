# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Quoting/RBQuotaTypeComboBoxPopup.ui'
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

class Ui_RBQuotaTypeComboBoxPopup(object):
    def setupUi(self, RBQuotaTypeComboBoxPopup):
        RBQuotaTypeComboBoxPopup.setObjectName(_fromUtf8("RBQuotaTypeComboBoxPopup"))
        RBQuotaTypeComboBoxPopup.resize(394, 265)
        self.verticalLayout = QtGui.QVBoxLayout(RBQuotaTypeComboBoxPopup)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(RBQuotaTypeComboBoxPopup)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabQuotaType = QtGui.QWidget()
        self.tabQuotaType.setObjectName(_fromUtf8("tabQuotaType"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tabQuotaType)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tblQuotaType = CQuotaTypeComboBoxPopupView(self.tabQuotaType)
        self.tblQuotaType.setObjectName(_fromUtf8("tblQuotaType"))
        self.verticalLayout_2.addWidget(self.tblQuotaType)
        self.tabWidget.addTab(self.tabQuotaType, _fromUtf8(""))
        self.tabFind = QtGui.QWidget()
        self.tabFind.setObjectName(_fromUtf8("tabFind"))
        self.gridLayout = QtGui.QGridLayout(self.tabFind)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.chkVTMPClass = QtGui.QCheckBox(self.tabFind)
        self.chkVTMPClass.setChecked(True)
        self.chkVTMPClass.setTristate(False)
        self.chkVTMPClass.setObjectName(_fromUtf8("chkVTMPClass"))
        self.verticalLayout_4.addWidget(self.chkVTMPClass)
        self.chkLimits = QtGui.QCheckBox(self.tabFind)
        self.chkLimits.setChecked(False)
        self.chkLimits.setObjectName(_fromUtf8("chkLimits"))
        self.verticalLayout_4.addWidget(self.chkLimits)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.cmbVTMPClass = QtGui.QComboBox(self.tabFind)
        self.cmbVTMPClass.setEnabled(True)
        self.cmbVTMPClass.setObjectName(_fromUtf8("cmbVTMPClass"))
        self.verticalLayout_3.addWidget(self.cmbVTMPClass)
        self.cmbLimits = QtGui.QComboBox(self.tabFind)
        self.cmbLimits.setEnabled(True)
        self.cmbLimits.setObjectName(_fromUtf8("cmbLimits"))
        self.cmbLimits.addItem(_fromUtf8(""))
        self.cmbLimits.addItem(_fromUtf8(""))
        self.verticalLayout_3.addWidget(self.cmbLimits)
        self.edtDate = QtGui.QDateEdit(self.tabFind)
        self.edtDate.setEnabled(True)
        self.edtDate.setCalendarPopup(True)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.verticalLayout_3.addWidget(self.edtDate)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 1, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.buttonBox = QtGui.QDialogButtonBox(self.tabFind)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 2)
        self.tabWidget.addTab(self.tabFind, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi(RBQuotaTypeComboBoxPopup)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.chkVTMPClass, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cmbVTMPClass.setEnabled)
        QtCore.QObject.connect(self.chkLimits, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cmbLimits.setEnabled)
        QtCore.QObject.connect(self.chkLimits, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.edtDate.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(RBQuotaTypeComboBoxPopup)

    def retranslateUi(self, RBQuotaTypeComboBoxPopup):
        RBQuotaTypeComboBoxPopup.setWindowTitle(_translate("RBQuotaTypeComboBoxPopup", "Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabQuotaType), _translate("RBQuotaTypeComboBoxPopup", "&Квоты", None))
        self.chkVTMPClass.setText(_translate("RBQuotaTypeComboBoxPopup", "Класс", None))
        self.chkLimits.setText(_translate("RBQuotaTypeComboBoxPopup", "Лимиты", None))
        self.cmbLimits.setItemText(0, _translate("RBQuotaTypeComboBoxPopup", "Да", None))
        self.cmbLimits.setItemText(1, _translate("RBQuotaTypeComboBoxPopup", "Нет", None))
        self.edtDate.setDisplayFormat(_translate("RBQuotaTypeComboBoxPopup", "dd.MM.yyyy", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFind), _translate("RBQuotaTypeComboBoxPopup", "&Поиск", None))

from Quoting.Utils import CQuotaTypeComboBoxPopupView
