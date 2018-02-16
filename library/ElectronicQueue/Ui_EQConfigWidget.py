# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EQConfigWidget.ui'
#
# Created: Tue Mar 18 15:42:21 2014
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_EQConfigWidget(object):
    def setupUi(self, EQConfigWidget):
        EQConfigWidget.setObjectName(_fromUtf8("EQConfigWidget"))
        EQConfigWidget.resize(392, 124)
        self.gridLayout = QtGui.QGridLayout(EQConfigWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btnCommit = QtGui.QPushButton(EQConfigWidget)
        self.btnCommit.setObjectName(_fromUtf8("btnCommit"))
        self.gridLayout.addWidget(self.btnCommit, 0, 2, 1, 1)
        self.chkPersonControl = QtGui.QCheckBox(EQConfigWidget)
        self.chkPersonControl.setChecked(True)
        self.chkPersonControl.setObjectName(_fromUtf8("chkPersonControl"))
        self.gridLayout.addWidget(self.chkPersonControl, 1, 1, 1, 1)
        self.cmbGatewayPlace = QtGui.QComboBox(EQConfigWidget)
        self.cmbGatewayPlace.setEditable(False)
        self.cmbGatewayPlace.setObjectName(_fromUtf8("cmbGatewayPlace"))
        self.gridLayout.addWidget(self.cmbGatewayPlace, 1, 0, 1, 1)
        self.chkDateControl = QtGui.QCheckBox(EQConfigWidget)
        self.chkDateControl.setChecked(True)
        self.chkDateControl.setObjectName(_fromUtf8("chkDateControl"))
        self.gridLayout.addWidget(self.chkDateControl, 0, 1, 1, 1)
        self.lblGatewayPlace = QtGui.QLabel(EQConfigWidget)
        self.lblGatewayPlace.setObjectName(_fromUtf8("lblGatewayPlace"))
        self.gridLayout.addWidget(self.lblGatewayPlace, 0, 0, 1, 1)
        self.chkFindByOrgStructure = QtGui.QCheckBox(EQConfigWidget)
        self.chkFindByOrgStructure.setObjectName(_fromUtf8("chkFindByOrgStructure"))
        self.gridLayout.addWidget(self.chkFindByOrgStructure, 2, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblHost = QtGui.QLabel(EQConfigWidget)
        self.lblHost.setObjectName(_fromUtf8("lblHost"))
        self.horizontalLayout.addWidget(self.lblHost)
        self.edtHost = QtGui.QLineEdit(EQConfigWidget)
        self.edtHost.setEnabled(False)
        self.edtHost.setMinimumSize(QtCore.QSize(100, 0))
        self.edtHost.setObjectName(_fromUtf8("edtHost"))
        self.horizontalLayout.addWidget(self.edtHost)
        self.lblPort = QtGui.QLabel(EQConfigWidget)
        self.lblPort.setObjectName(_fromUtf8("lblPort"))
        self.horizontalLayout.addWidget(self.lblPort)
        self.spbPort = QtGui.QSpinBox(EQConfigWidget)
        self.spbPort.setEnabled(False)
        self.spbPort.setMaximum(99999)
        self.spbPort.setProperty("value", 5000)
        self.spbPort.setObjectName(_fromUtf8("spbPort"))
        self.horizontalLayout.addWidget(self.spbPort)
        self.stackedWidget = QtGui.QStackedWidget(EQConfigWidget)
        self.stackedWidget.setLineWidth(0)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.pagePanelAddress = QtGui.QWidget()
        self.pagePanelAddress.setObjectName(_fromUtf8("pagePanelAddress"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.pagePanelAddress)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lblPanelAddress = QtGui.QLabel(self.pagePanelAddress)
        self.lblPanelAddress.setEnabled(True)
        self.lblPanelAddress.setObjectName(_fromUtf8("lblPanelAddress"))
        self.horizontalLayout_2.addWidget(self.lblPanelAddress)
        self.spbPanelAddress = QtGui.QSpinBox(self.pagePanelAddress)
        self.spbPanelAddress.setEnabled(False)
        self.spbPanelAddress.setMinimum(0)
        self.spbPanelAddress.setMaximum(255)
        self.spbPanelAddress.setProperty("value", 255)
        self.spbPanelAddress.setObjectName(_fromUtf8("spbPanelAddress"))
        self.horizontalLayout_2.addWidget(self.spbPanelAddress)
        self.stackedWidget.addWidget(self.pagePanelAddress)
        self.pageOffice = QtGui.QWidget()
        self.pageOffice.setObjectName(_fromUtf8("pageOffice"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.pageOffice)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.lblOffice = QtGui.QLabel(self.pageOffice)
        self.lblOffice.setObjectName(_fromUtf8("lblOffice"))
        self.horizontalLayout_3.addWidget(self.lblOffice)
        self.cmbOffice = CDbComboBox(self.pageOffice)
        self.cmbOffice.setObjectName(_fromUtf8("cmbOffice"))
        self.horizontalLayout_3.addWidget(self.cmbOffice)
        self.stackedWidget.addWidget(self.pageOffice)
        self.horizontalLayout.addWidget(self.stackedWidget)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 3)
        self.btnReset = QtGui.QPushButton(EQConfigWidget)
        self.btnReset.setObjectName(_fromUtf8("btnReset"))
        self.gridLayout.addWidget(self.btnReset, 2, 2, 1, 1)
        self.btnShowAllAddresses = QtGui.QPushButton(EQConfigWidget)
        self.btnShowAllAddresses.setObjectName(_fromUtf8("btnShowAllAddresses"))
        self.gridLayout.addWidget(self.btnShowAllAddresses, 1, 2, 1, 1)
        self.lblGatewayPlace.setBuddy(self.cmbGatewayPlace)
        self.lblHost.setBuddy(self.edtHost)
        self.lblPort.setBuddy(self.spbPort)
        self.lblPanelAddress.setBuddy(self.spbPanelAddress)

        self.retranslateUi(EQConfigWidget)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(EQConfigWidget)

    def retranslateUi(self, EQConfigWidget):
        EQConfigWidget.setWindowTitle(_translate("EQConfigWidget", "Конфигурация табло эл. очереди", None))
        self.btnCommit.setText(_translate("EQConfigWidget", "Установить", None))
        self.chkPersonControl.setToolTip(_translate("EQConfigWidget", "Вызов пациентов только из очереди текущего врача-пользователя", None))
        self.chkPersonControl.setText(_translate("EQConfigWidget", "Контроль врача", None))
        self.chkDateControl.setToolTip(_translate("EQConfigWidget", "Вызов пациентов только из сегодняшней очереди", None))
        self.chkDateControl.setText(_translate("EQConfigWidget", "Контроль даты", None))
        self.lblGatewayPlace.setText(_translate("EQConfigWidget", "&Выберите конфигурацию/объект", None))
        self.chkFindByOrgStructure.setText(_translate("EQConfigWidget", "Учитывать подразделение текущего пользователя", None))
        self.lblHost.setText(_translate("EQConfigWidget", "&Шлюз:", None))
        self.edtHost.setText(_translate("EQConfigWidget", "192.168.222.222", None))
        self.lblPort.setText(_translate("EQConfigWidget", "&Порт:", None))
        self.lblPanelAddress.setText(_translate("EQConfigWidget", "&Табло:", None))
        self.lblOffice.setText(_translate("EQConfigWidget", "Каб.:", None))
        self.btnReset.setText(_translate("EQConfigWidget", "Сбросить", None))
        self.btnShowAllAddresses.setText(_translate("EQConfigWidget", "Показать адреса", None))

from library.DbComboBox import CDbComboBox
