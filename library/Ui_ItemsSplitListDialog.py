# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './library/ItemsSplitListDialog.ui'
#
# Created: Wed Aug  8 18:46:33 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ItemsSplitListDialog(object):
    def setupUi(self, ItemsSplitListDialog):
        ItemsSplitListDialog.setObjectName(_fromUtf8("ItemsSplitListDialog"))
        ItemsSplitListDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ItemsSplitListDialog.resize(689, 500)
        ItemsSplitListDialog.setSizeGripEnabled(True)
        ItemsSplitListDialog.setModal(True)
        self.gridLayout_2 = QtGui.QGridLayout(ItemsSplitListDialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.grp = QtGui.QWidget(ItemsSplitListDialog)
        self.grp.setObjectName(_fromUtf8("grp"))
        self.gridLayout = QtGui.QGridLayout(self.grp)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(self.grp)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tblItems = CTableView(self.splitter)
        self.tblItems.setTabKeyNavigation(False)
        self.tblItems.setAlternatingRowColors(True)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.tblItemGroups = CTableView(self.splitter)
        self.tblItemGroups.setTabKeyNavigation(False)
        self.tblItemGroups.setAlternatingRowColors(True)
        self.tblItemGroups.setObjectName(_fromUtf8("tblItemGroups"))
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.grp, 0, 0, 1, 3)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(4)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(ItemsSplitListDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.hboxlayout, 1, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ItemsSplitListDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 2, 1, 1)
        self.statusBar = QtGui.QStatusBar(ItemsSplitListDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusBar.sizePolicy().hasHeightForWidth())
        self.statusBar.setSizePolicy(sizePolicy)
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        self.gridLayout_2.addWidget(self.statusBar, 2, 0, 1, 3)

        self.retranslateUi(ItemsSplitListDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemsSplitListDialog.close)
        QtCore.QMetaObject.connectSlotsByName(ItemsSplitListDialog)

    def retranslateUi(self, ItemsSplitListDialog):
        ItemsSplitListDialog.setWindowTitle(QtGui.QApplication.translate("ItemsSplitListDialog", "Список записей", None, QtGui.QApplication.UnicodeUTF8))
        self.tblItems.setWhatsThis(QtGui.QApplication.translate("ItemsSplitListDialog", "список записей", "ура!", QtGui.QApplication.UnicodeUTF8))
        self.tblItemGroups.setWhatsThis(QtGui.QApplication.translate("ItemsSplitListDialog", "список записей", "ура!", QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ItemsSplitListDialog", "всего: ", None, QtGui.QApplication.UnicodeUTF8))
        self.statusBar.setToolTip(QtGui.QApplication.translate("ItemsSplitListDialog", "A status bar", None, QtGui.QApplication.UnicodeUTF8))
        self.statusBar.setWhatsThis(QtGui.QApplication.translate("ItemsSplitListDialog", "A status bar.", None, QtGui.QApplication.UnicodeUTF8))

from TableView import CTableView
