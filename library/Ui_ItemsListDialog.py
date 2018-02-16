# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\ItemsListDialog.ui'
#
# Created: Fri Jun 15 12:15:30 2012
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
        ItemsListDialog.resize(689, 450)
        ItemsListDialog.setSizeGripEnabled(True)
        ItemsListDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(ItemsListDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblItems = CTableView(ItemsListDialog)
        self.tblItems.setTabKeyNavigation(False)
        self.tblItems.setAlternatingRowColors(True)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 0, 0, 1, 2)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(ItemsListDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.hboxlayout, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemsListDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)
        self.statusBar = QtGui.QStatusBar(ItemsListDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusBar.sizePolicy().hasHeightForWidth())
        self.statusBar.setSizePolicy(sizePolicy)
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        self.gridLayout.addWidget(self.statusBar, 2, 0, 1, 2)

        self.retranslateUi(ItemsListDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemsListDialog.close)
        QtCore.QMetaObject.connectSlotsByName(ItemsListDialog)

    def retranslateUi(self, ItemsListDialog):
        ItemsListDialog.setWindowTitle(QtGui.QApplication.translate("ItemsListDialog", "Список записей", None, QtGui.QApplication.UnicodeUTF8))
        self.tblItems.setWhatsThis(QtGui.QApplication.translate("ItemsListDialog", "список записей", "ура!", QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ItemsListDialog", "всего: ", None, QtGui.QApplication.UnicodeUTF8))
        self.statusBar.setToolTip(QtGui.QApplication.translate("ItemsListDialog", "A status bar", None, QtGui.QApplication.UnicodeUTF8))
        self.statusBar.setWhatsThis(QtGui.QApplication.translate("ItemsListDialog", "A status bar.", None, QtGui.QApplication.UnicodeUTF8))

from TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemsListDialog = QtGui.QDialog()
    ui = Ui_ItemsListDialog()
    ui.setupUi(ItemsListDialog)
    ItemsListDialog.show()
    sys.exit(app.exec_())

