# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ClientPolicyComboBoxPopup.ui'
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

class Ui_ClientPolicyComboBoxPopup(object):
    def setupUi(self, ClientPolicyComboBoxPopup):
        ClientPolicyComboBoxPopup.setObjectName(_fromUtf8("ClientPolicyComboBoxPopup"))
        ClientPolicyComboBoxPopup.resize(400, 200)
        self.gridLayout = QtGui.QGridLayout(ClientPolicyComboBoxPopup)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(ClientPolicyComboBoxPopup)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabClientPolicy = QtGui.QWidget()
        self.tabClientPolicy.setObjectName(_fromUtf8("tabClientPolicy"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tabClientPolicy)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tblClientPolicy = CTableView(self.tabClientPolicy)
        self.tblClientPolicy.setObjectName(_fromUtf8("tblClientPolicy"))
        self.gridLayout_3.addWidget(self.tblClientPolicy, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabClientPolicy, _fromUtf8(""))
        self.tabSearch = QtGui.QWidget()
        self.tabSearch.setObjectName(_fromUtf8("tabSearch"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tabSearch)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout_2.addLayout(self.horizontalLayout, 3, 0, 1, 2)
        self.lblPolicyType = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPolicyType.sizePolicy().hasHeightForWidth())
        self.lblPolicyType.setSizePolicy(sizePolicy)
        self.lblPolicyType.setObjectName(_fromUtf8("lblPolicyType"))
        self.gridLayout_2.addWidget(self.lblPolicyType, 0, 0, 1, 1)
        self.lblPolicyKind = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPolicyKind.sizePolicy().hasHeightForWidth())
        self.lblPolicyKind.setSizePolicy(sizePolicy)
        self.lblPolicyKind.setObjectName(_fromUtf8("lblPolicyKind"))
        self.gridLayout_2.addWidget(self.lblPolicyKind, 1, 0, 1, 1)
        self.cmbPolicyType = CRBComboBox(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbPolicyType.sizePolicy().hasHeightForWidth())
        self.cmbPolicyType.setSizePolicy(sizePolicy)
        self.cmbPolicyType.setObjectName(_fromUtf8("cmbPolicyType"))
        self.gridLayout_2.addWidget(self.cmbPolicyType, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 2, 0, 1, 1)
        self.cmbPolicyKind = CRBComboBox(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbPolicyKind.sizePolicy().hasHeightForWidth())
        self.cmbPolicyKind.setSizePolicy(sizePolicy)
        self.cmbPolicyKind.setObjectName(_fromUtf8("cmbPolicyKind"))
        self.gridLayout_2.addWidget(self.cmbPolicyKind, 1, 1, 1, 1)
        self.tabWidget.addTab(self.tabSearch, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(ClientPolicyComboBoxPopup)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(ClientPolicyComboBoxPopup)

    def retranslateUi(self, ClientPolicyComboBoxPopup):
        ClientPolicyComboBoxPopup.setWindowTitle(_translate("ClientPolicyComboBoxPopup", "Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabClientPolicy), _translate("ClientPolicyComboBoxPopup", "&Полисы пациента", None))
        self.lblPolicyType.setText(_translate("ClientPolicyComboBoxPopup", "Тип полиса", None))
        self.lblPolicyKind.setText(_translate("ClientPolicyComboBoxPopup", "Вид полиса", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSearch), _translate("ClientPolicyComboBoxPopup", "П&оиск", None))

from library.TableView import CTableView
from library.crbcombobox import CRBComboBox
