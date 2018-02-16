# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\ItemsSplitListDialog.ui'
#
# Created: Fri Jun 15 12:16:49 2012
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
        ItemsListDialog.resize(593, 556)
        ItemsListDialog.setSizeGripEnabled(True)
        ItemsListDialog.setModal(True)
        self.gridlayout = QtGui.QGridLayout(ItemsListDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(4)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(ItemsListDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.btnSelect = QtGui.QPushButton(ItemsListDialog)
        self.btnSelect.setObjectName(_fromUtf8("btnSelect"))
        self.hboxlayout.addWidget(self.btnSelect)
        self.btnFilter = QtGui.QPushButton(ItemsListDialog)
        self.btnFilter.setObjectName(_fromUtf8("btnFilter"))
        self.hboxlayout.addWidget(self.btnFilter)
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
        self.btnCancel = QtGui.QPushButton(ItemsListDialog)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.hboxlayout.addWidget(self.btnCancel)
        self.gridlayout.addLayout(self.hboxlayout, 1, 0, 1, 1)
        self.statusBar = QtGui.QStatusBar(ItemsListDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusBar.sizePolicy().hasHeightForWidth())
        self.statusBar.setSizePolicy(sizePolicy)
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        self.gridlayout.addWidget(self.statusBar, 2, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(ItemsListDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.groupBox)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tblItems = CTableView(self.splitter)
        self.tblItems.setTabKeyNavigation(False)
        self.tblItems.setAlternatingRowColors(True)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.tblItemGroups = CTableView(self.splitter)
        self.tblItemGroups.setObjectName(_fromUtf8("tblItemGroups"))
        self.verticalLayout.addWidget(self.splitter)
        self.gridlayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(ItemsListDialog)
        QtCore.QObject.connect(self.btnCancel, QtCore.SIGNAL(_fromUtf8("clicked()")), ItemsListDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemsListDialog)
        ItemsListDialog.setTabOrder(self.btnSelect, self.btnFilter)
        ItemsListDialog.setTabOrder(self.btnFilter, self.btnEdit)
        ItemsListDialog.setTabOrder(self.btnEdit, self.btnNew)
        ItemsListDialog.setTabOrder(self.btnNew, self.btnCancel)

    def retranslateUi(self, ItemsListDialog):
        ItemsListDialog.setWindowTitle(QtGui.QApplication.translate("ItemsListDialog", "Список записей", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ItemsListDialog", "всего: ", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelect.setWhatsThis(QtGui.QApplication.translate("ItemsListDialog", "выбрать текущую запись", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelect.setText(QtGui.QApplication.translate("ItemsListDialog", "Выбор", None, QtGui.QApplication.UnicodeUTF8))
        self.btnFilter.setWhatsThis(QtGui.QApplication.translate("ItemsListDialog", "изменить условие отбора записей для показа в списке", None, QtGui.QApplication.UnicodeUTF8))
        self.btnFilter.setText(QtGui.QApplication.translate("ItemsListDialog", "Фильтр", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEdit.setWhatsThis(QtGui.QApplication.translate("ItemsListDialog", "изменить текущую запись", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEdit.setText(QtGui.QApplication.translate("ItemsListDialog", "Правка F4", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEdit.setShortcut(QtGui.QApplication.translate("ItemsListDialog", "F4", None, QtGui.QApplication.UnicodeUTF8))
        self.btnNew.setWhatsThis(QtGui.QApplication.translate("ItemsListDialog", "добавить новую запись", None, QtGui.QApplication.UnicodeUTF8))
        self.btnNew.setText(QtGui.QApplication.translate("ItemsListDialog", "Вставка F9", None, QtGui.QApplication.UnicodeUTF8))
        self.btnNew.setShortcut(QtGui.QApplication.translate("ItemsListDialog", "F9", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPrint.setText(QtGui.QApplication.translate("ItemsListDialog", "Печать F6", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setWhatsThis(QtGui.QApplication.translate("ItemsListDialog", "выйти из списка без выбора", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("ItemsListDialog", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.statusBar.setToolTip(QtGui.QApplication.translate("ItemsListDialog", "A status bar", None, QtGui.QApplication.UnicodeUTF8))
        self.statusBar.setWhatsThis(QtGui.QApplication.translate("ItemsListDialog", "A status bar.", None, QtGui.QApplication.UnicodeUTF8))
        self.tblItems.setWhatsThis(QtGui.QApplication.translate("ItemsListDialog", "список записей", "ура!", QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemsListDialog = QtGui.QDialog()
    ui = Ui_ItemsListDialog()
    ui.setupUi(ItemsListDialog)
    ItemsListDialog.show()
    sys.exit(app.exec_())

