# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RLSComboBoxPopup.ui'
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

class Ui_RLSComboBoxPopup(object):
    def setupUi(self, RLSComboBoxPopup):
        RLSComboBoxPopup.setObjectName(_fromUtf8("RLSComboBoxPopup"))
        RLSComboBoxPopup.resize(400, 299)
        self.gridlayout = QtGui.QGridLayout(RLSComboBoxPopup)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.tabWidget = QtGui.QTabWidget(RLSComboBoxPopup)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabRLS = QtGui.QWidget()
        self.tabRLS.setObjectName(_fromUtf8("tabRLS"))
        self.vboxlayout = QtGui.QVBoxLayout(self.tabRLS)
        self.vboxlayout.setMargin(4)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.tblRLS = CTableView(self.tabRLS)
        self.tblRLS.setObjectName(_fromUtf8("tblRLS"))
        self.vboxlayout.addWidget(self.tblRLS)
        self.tabWidget.addTab(self.tabRLS, _fromUtf8(""))
        self.tabSearch = QtGui.QWidget()
        self.tabSearch.setObjectName(_fromUtf8("tabSearch"))
        self.gridlayout1 = QtGui.QGridLayout(self.tabSearch)
        self.gridlayout1.setMargin(4)
        self.gridlayout1.setSpacing(4)
        self.gridlayout1.setObjectName(_fromUtf8("gridlayout1"))
        self.lblTradeName = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblTradeName.sizePolicy().hasHeightForWidth())
        self.lblTradeName.setSizePolicy(sizePolicy)
        self.lblTradeName.setObjectName(_fromUtf8("lblTradeName"))
        self.gridlayout1.addWidget(self.lblTradeName, 0, 0, 1, 1)
        self.edtTradeName = QtGui.QLineEdit(self.tabSearch)
        self.edtTradeName.setObjectName(_fromUtf8("edtTradeName"))
        self.gridlayout1.addWidget(self.edtTradeName, 0, 1, 1, 2)
        self.lblINN = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblINN.sizePolicy().hasHeightForWidth())
        self.lblINN.setSizePolicy(sizePolicy)
        self.lblINN.setObjectName(_fromUtf8("lblINN"))
        self.gridlayout1.addWidget(self.lblINN, 1, 0, 1, 1)
        self.edtINN = QtGui.QLineEdit(self.tabSearch)
        self.edtINN.setObjectName(_fromUtf8("edtINN"))
        self.gridlayout1.addWidget(self.edtINN, 1, 1, 1, 2)
        self.lblPharmGroup = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPharmGroup.sizePolicy().hasHeightForWidth())
        self.lblPharmGroup.setSizePolicy(sizePolicy)
        self.lblPharmGroup.setObjectName(_fromUtf8("lblPharmGroup"))
        self.gridlayout1.addWidget(self.lblPharmGroup, 2, 0, 1, 1)
        self.cmbPharmGroup = CPharmGroupComboBox(self.tabSearch)
        self.cmbPharmGroup.setObjectName(_fromUtf8("cmbPharmGroup"))
        self.gridlayout1.addWidget(self.cmbPharmGroup, 2, 1, 1, 2)
        self.lblATC = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblATC.sizePolicy().hasHeightForWidth())
        self.lblATC.setSizePolicy(sizePolicy)
        self.lblATC.setObjectName(_fromUtf8("lblATC"))
        self.gridlayout1.addWidget(self.lblATC, 3, 0, 1, 1)
        self.cmbATC = CATCComboBox(self.tabSearch)
        self.cmbATC.setObjectName(_fromUtf8("cmbATC"))
        self.gridlayout1.addWidget(self.cmbATC, 3, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 141, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem, 6, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(231, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem1, 7, 0, 1, 2)
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
        self.gridlayout1.addWidget(self.buttonBox, 7, 2, 1, 1)
        self.chkShowAnnulated = QtGui.QCheckBox(self.tabSearch)
        self.chkShowAnnulated.setObjectName(_fromUtf8("chkShowAnnulated"))
        self.gridlayout1.addWidget(self.chkShowAnnulated, 4, 1, 1, 2)
        self.chkShowDisabled = QtGui.QCheckBox(self.tabSearch)
        self.chkShowDisabled.setObjectName(_fromUtf8("chkShowDisabled"))
        self.gridlayout1.addWidget(self.chkShowDisabled, 5, 1, 1, 2)
        self.tabWidget.addTab(self.tabSearch, _fromUtf8(""))
        self.gridlayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.lblTradeName.setBuddy(self.edtTradeName)
        self.lblINN.setBuddy(self.edtINN)
        self.lblPharmGroup.setBuddy(self.cmbPharmGroup)
        self.lblATC.setBuddy(self.cmbATC)

        self.retranslateUi(RLSComboBoxPopup)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(RLSComboBoxPopup)
        RLSComboBoxPopup.setTabOrder(self.tabWidget, self.tblRLS)
        RLSComboBoxPopup.setTabOrder(self.tblRLS, self.edtTradeName)
        RLSComboBoxPopup.setTabOrder(self.edtTradeName, self.edtINN)
        RLSComboBoxPopup.setTabOrder(self.edtINN, self.cmbPharmGroup)
        RLSComboBoxPopup.setTabOrder(self.cmbPharmGroup, self.cmbATC)
        RLSComboBoxPopup.setTabOrder(self.cmbATC, self.chkShowAnnulated)
        RLSComboBoxPopup.setTabOrder(self.chkShowAnnulated, self.chkShowDisabled)
        RLSComboBoxPopup.setTabOrder(self.chkShowDisabled, self.buttonBox)

    def retranslateUi(self, RLSComboBoxPopup):
        RLSComboBoxPopup.setWindowTitle(_translate("RLSComboBoxPopup", "Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabRLS), _translate("RLSComboBoxPopup", "&Номенклатура", None))
        self.lblTradeName.setText(_translate("RLSComboBoxPopup", "&Наименование", None))
        self.lblINN.setText(_translate("RLSComboBoxPopup", "&МНН", None))
        self.lblPharmGroup.setText(_translate("RLSComboBoxPopup", "&Фарм.группа", None))
        self.lblATC.setText(_translate("RLSComboBoxPopup", "&АТХ", None))
        self.chkShowAnnulated.setText(_translate("RLSComboBoxPopup", "Показывать анну&лированные", None))
        self.chkShowDisabled.setText(_translate("RLSComboBoxPopup", "Показывать &большие упаковки", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSearch), _translate("RLSComboBoxPopup", "&Поиск", None))

from library.RLS.ATCComboBox import CATCComboBox
from library.RLS.PharmGroupComboBox import CPharmGroupComboBox
from library.TableView import CTableView
