# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FormularyItemComboBoxPopup.ui'
#
# Created: Thu Feb 19 18:29:16 2015
#      by: PyQt4 UI code generator 4.11
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

class Ui_FormularyItemComboBoxPopup(object):
    def setupUi(self, FormularyItemComboBoxPopup):
        FormularyItemComboBoxPopup.setObjectName(_fromUtf8("FormularyItemComboBoxPopup"))
        FormularyItemComboBoxPopup.resize(400, 276)
        self.gridlayout = QtGui.QGridLayout(FormularyItemComboBoxPopup)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.tabWidget = QtGui.QTabWidget(FormularyItemComboBoxPopup)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabFormularyItem = QtGui.QWidget()
        self.tabFormularyItem.setObjectName(_fromUtf8("tabFormularyItem"))
        self.vboxlayout = QtGui.QVBoxLayout(self.tabFormularyItem)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setMargin(4)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.tblFormularyItem = CTableView(self.tabFormularyItem)
        self.tblFormularyItem.setObjectName(_fromUtf8("tblFormularyItem"))
        self.vboxlayout.addWidget(self.tblFormularyItem)
        self.tabWidget.addTab(self.tabFormularyItem, _fromUtf8(""))
        self.tabSearch = QtGui.QWidget()
        self.tabSearch.setObjectName(_fromUtf8("tabSearch"))
        self.gridLayout = QtGui.QGridLayout(self.tabSearch)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtCode = QtGui.QLineEdit(self.tabSearch)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 2)
        self.lblCode = QtGui.QLabel(self.tabSearch)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(178, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 2)
        self.edtName = QtGui.QLineEdit(self.tabSearch)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 2)
        self.lblName = QtGui.QLabel(self.tabSearch)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 2, 1, 1)
        self.tabWidget.addTab(self.tabSearch, _fromUtf8(""))
        self.gridlayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(FormularyItemComboBoxPopup)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(FormularyItemComboBoxPopup)
        FormularyItemComboBoxPopup.setTabOrder(self.tabWidget, self.tblFormularyItem)
        FormularyItemComboBoxPopup.setTabOrder(self.tblFormularyItem, self.edtCode)
        FormularyItemComboBoxPopup.setTabOrder(self.edtCode, self.edtName)
        FormularyItemComboBoxPopup.setTabOrder(self.edtName, self.buttonBox)

    def retranslateUi(self, FormularyItemComboBoxPopup):
        FormularyItemComboBoxPopup.setWindowTitle(_translate("FormularyItemComboBoxPopup", "Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFormularyItem), _translate("FormularyItemComboBoxPopup", "&Номенклатура", None))
        self.lblCode.setText(_translate("FormularyItemComboBoxPopup", "&Код", None))
        self.lblName.setText(_translate("FormularyItemComboBoxPopup", "&Наименование", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSearch), _translate("FormularyItemComboBoxPopup", "&Поиск", None))

from library.TableView import CTableView
