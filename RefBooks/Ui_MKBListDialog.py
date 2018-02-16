# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\MKBListDialog.ui'
#
# Created: Fri Jun 15 12:15:37 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ItemsListDialog(object):
    def setupUi(self, ItemsListDialog):
        ItemsListDialog.setObjectName(_fromUtf8("ItemsListDialog"))
        ItemsListDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ItemsListDialog.resize(1002, 499)
        ItemsListDialog.setSizeGripEnabled(True)
        ItemsListDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(ItemsListDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(ItemsListDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.tblItems = CTableView(ItemsListDialog)
        self.tblItems.setTabKeyNavigation(False)
        self.tblItems.setAlternatingRowColors(True)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 1, 0, 1, 5)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(4)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(ItemsListDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.btnCharacters = QtGui.QPushButton(ItemsListDialog)
        self.btnCharacters.setObjectName(_fromUtf8("btnCharacters"))
        self.hboxlayout.addWidget(self.btnCharacters)
        self.btnSex = QtGui.QPushButton(ItemsListDialog)
        self.btnSex.setObjectName(_fromUtf8("btnSex"))
        self.hboxlayout.addWidget(self.btnSex)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.btnEdit = QtGui.QPushButton(ItemsListDialog)
        self.btnEdit.setDefault(True)
        self.btnEdit.setObjectName(_fromUtf8("btnEdit"))
        self.hboxlayout.addWidget(self.btnEdit)
        self.btnNew = QtGui.QPushButton(ItemsListDialog)
        self.btnNew.setObjectName(_fromUtf8("btnNew"))
        self.hboxlayout.addWidget(self.btnNew)
        self.btnPrint = QtGui.QPushButton(ItemsListDialog)
        self.btnPrint.setObjectName(_fromUtf8("btnPrint"))
        self.hboxlayout.addWidget(self.btnPrint)
        self.btnPrintSelected = QtGui.QPushButton(ItemsListDialog)
        self.btnPrintSelected.setObjectName(_fromUtf8("btnPrintSelected"))
        self.hboxlayout.addWidget(self.btnPrintSelected)
        self.btnCancel = QtGui.QPushButton(ItemsListDialog)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.hboxlayout.addWidget(self.btnCancel)
        self.gridLayout.addLayout(self.hboxlayout, 2, 0, 1, 5)
        self.edtCode = QtGui.QLineEdit(ItemsListDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemsListDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 0, 3, 1, 1)
        self.label_3 = QtGui.QLabel(ItemsListDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 4, 1, 1)

        self.retranslateUi(ItemsListDialog)
        QtCore.QObject.connect(self.btnCancel, QtCore.SIGNAL(_fromUtf8("clicked()")), ItemsListDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemsListDialog)
        ItemsListDialog.setTabOrder(self.tblItems, self.btnEdit)
        ItemsListDialog.setTabOrder(self.btnEdit, self.btnNew)
        ItemsListDialog.setTabOrder(self.btnNew, self.btnPrint)
        ItemsListDialog.setTabOrder(self.btnPrint, self.btnPrintSelected)
        ItemsListDialog.setTabOrder(self.btnPrintSelected, self.btnCancel)
        ItemsListDialog.setTabOrder(self.btnCancel, self.edtCode)
        ItemsListDialog.setTabOrder(self.edtCode, self.edtName)
        ItemsListDialog.setTabOrder(self.edtName, self.btnCharacters)
        ItemsListDialog.setTabOrder(self.btnCharacters, self.btnSex)

    def retranslateUi(self, ItemsListDialog):
        ItemsListDialog.setWindowTitle(QtGui.QApplication.translate("ItemsListDialog", "Список записей", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ItemsListDialog", "код начинается на", None, QtGui.QApplication.UnicodeUTF8))
        self.tblItems.setWhatsThis(QtGui.QApplication.translate("ItemsListDialog", "список пользователей", "ура!", QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ItemsListDialog", "всего: ", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCharacters.setText(QtGui.QApplication.translate("ItemsListDialog", "Групповое изменение характера", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSex.setText(QtGui.QApplication.translate("ItemsListDialog", "Групповое изменение пола", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEdit.setText(QtGui.QApplication.translate("ItemsListDialog", "Правка F4", None, QtGui.QApplication.UnicodeUTF8))
        self.btnNew.setText(QtGui.QApplication.translate("ItemsListDialog", "Вставка F9", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPrint.setText(QtGui.QApplication.translate("ItemsListDialog", "Печать F6", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPrintSelected.setText(QtGui.QApplication.translate("ItemsListDialog", "Печать выделенных", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setWhatsThis(QtGui.QApplication.translate("ItemsListDialog", "выйти из списка без выбора", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("ItemsListDialog", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ItemsListDialog", "название диагноза содержит", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemsListDialog = QtGui.QDialog()
    ui = Ui_ItemsListDialog()
    ui.setupUi(ItemsListDialog)
    ItemsListDialog.show()
    sys.exit(app.exec_())

