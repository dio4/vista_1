# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FormularyComboBoxPopup.ui'
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

class Ui_FormularyComboBoxPopup(object):
    def setupUi(self, FormularyComboBoxPopup):
        FormularyComboBoxPopup.setObjectName(_fromUtf8("FormularyComboBoxPopup"))
        FormularyComboBoxPopup.resize(428, 276)
        self.gridlayout = QtGui.QGridLayout(FormularyComboBoxPopup)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.tabWidget = QtGui.QTabWidget(FormularyComboBoxPopup)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabFormulary = QtGui.QWidget()
        self.tabFormulary.setObjectName(_fromUtf8("tabFormulary"))
        self.vboxlayout = QtGui.QVBoxLayout(self.tabFormulary)
        self.vboxlayout.setMargin(4)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.tblFormulary = CTableView(self.tabFormulary)
        self.tblFormulary.setObjectName(_fromUtf8("tblFormulary"))
        self.vboxlayout.addWidget(self.tblFormulary)
        self.tabWidget.addTab(self.tabFormulary, _fromUtf8(""))
        self.tabSearch = QtGui.QWidget()
        self.tabSearch.setObjectName(_fromUtf8("tabSearch"))
        self.gridLayout = QtGui.QGridLayout(self.tabSearch)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblTradeName = QtGui.QLabel(self.tabSearch)
        self.lblTradeName.setObjectName(_fromUtf8("lblTradeName"))
        self.gridLayout.addWidget(self.lblTradeName, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 2, 1, 1)
        self.edtCode = QtGui.QLineEdit(self.tabSearch)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 2)
        self.lblName = QtGui.QLabel(self.tabSearch)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.lblCode = QtGui.QLabel(self.tabSearch)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(178, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 5, 0, 1, 2)
        self.edtTradeName = QtGui.QLineEdit(self.tabSearch)
        self.edtTradeName.setObjectName(_fromUtf8("edtTradeName"))
        self.gridLayout.addWidget(self.edtTradeName, 2, 1, 1, 2)
        self.edtName = QtGui.QLineEdit(self.tabSearch)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 2)
        self.edtMnn = QtGui.QLineEdit(self.tabSearch)
        self.edtMnn.setObjectName(_fromUtf8("edtMnn"))
        self.gridLayout.addWidget(self.edtMnn, 3, 2, 1, 1)
        self.lblMnn = QtGui.QLabel(self.tabSearch)
        self.lblMnn.setObjectName(_fromUtf8("lblMnn"))
        self.gridLayout.addWidget(self.lblMnn, 3, 0, 1, 1)
        self.tabWidget.addTab(self.tabSearch, _fromUtf8(""))
        self.gridlayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.lblName.setBuddy(self.edtName)
        self.lblCode.setBuddy(self.edtCode)

        self.retranslateUi(FormularyComboBoxPopup)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(FormularyComboBoxPopup)
        FormularyComboBoxPopup.setTabOrder(self.tabWidget, self.tblFormulary)
        FormularyComboBoxPopup.setTabOrder(self.tblFormulary, self.edtCode)
        FormularyComboBoxPopup.setTabOrder(self.edtCode, self.edtName)
        FormularyComboBoxPopup.setTabOrder(self.edtName, self.edtTradeName)
        FormularyComboBoxPopup.setTabOrder(self.edtTradeName, self.buttonBox)

    def retranslateUi(self, FormularyComboBoxPopup):
        FormularyComboBoxPopup.setWindowTitle(_translate("FormularyComboBoxPopup", "Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFormulary), _translate("FormularyComboBoxPopup", "&Формуляр", None))
        self.lblTradeName.setText(_translate("FormularyComboBoxPopup", "Торговое наименование", None))
        self.lblName.setText(_translate("FormularyComboBoxPopup", "&Формулярное наименование", None))
        self.lblCode.setText(_translate("FormularyComboBoxPopup", "&Код", None))
        self.lblMnn.setText(_translate("FormularyComboBoxPopup", "Наименование MNN", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSearch), _translate("FormularyComboBoxPopup", "&Поиск", None))

from library.TableView import CTableView
