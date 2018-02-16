# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportRbUnit_Wizard_2.ui'
#
# Created: Fri Jun 15 12:16:02 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportRbUnit_Wizard_2(object):
    def setupUi(self, ImportRbUnit_Wizard_2):
        ImportRbUnit_Wizard_2.setObjectName(_fromUtf8("ImportRbUnit_Wizard_2"))
        ImportRbUnit_Wizard_2.setWindowModality(QtCore.Qt.NonModal)
        ImportRbUnit_Wizard_2.resize(593, 450)
        self.gridlayout = QtGui.QGridLayout(ImportRbUnit_Wizard_2)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.splitterTree = QtGui.QSplitter(ImportRbUnit_Wizard_2)
        self.splitterTree.setOrientation(QtCore.Qt.Horizontal)
        self.splitterTree.setObjectName(_fromUtf8("splitterTree"))
        self.tblEvents = QtGui.QTableWidget(self.splitterTree)
        self.tblEvents.setObjectName(_fromUtf8("tblEvents"))
        self.tblEvents.setColumnCount(0)
        self.tblEvents.setRowCount(0)
        self.gridlayout.addWidget(self.splitterTree, 2, 0, 1, 1)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.btnClearSelection = QtGui.QPushButton(ImportRbUnit_Wizard_2)
        self.btnClearSelection.setObjectName(_fromUtf8("btnClearSelection"))
        self.hboxlayout.addWidget(self.btnClearSelection)
        self.gridlayout.addLayout(self.hboxlayout, 3, 0, 1, 1)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.chkImportAll = QtGui.QCheckBox(ImportRbUnit_Wizard_2)
        self.chkImportAll.setObjectName(_fromUtf8("chkImportAll"))
        self.hboxlayout1.addWidget(self.chkImportAll)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.gridlayout.addLayout(self.hboxlayout1, 0, 0, 1, 1)
        self.statusLabel = QtGui.QLabel(ImportRbUnit_Wizard_2)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridlayout.addWidget(self.statusLabel, 4, 0, 1, 1)

        self.retranslateUi(ImportRbUnit_Wizard_2)
        QtCore.QMetaObject.connectSlotsByName(ImportRbUnit_Wizard_2)

    def retranslateUi(self, ImportRbUnit_Wizard_2):
        ImportRbUnit_Wizard_2.setWindowTitle(QtGui.QApplication.translate("ImportRbUnit_Wizard_2", "Список записей", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClearSelection.setText(QtGui.QApplication.translate("ImportRbUnit_Wizard_2", "Очистить", None, QtGui.QApplication.UnicodeUTF8))
        self.chkImportAll.setText(QtGui.QApplication.translate("ImportRbUnit_Wizard_2", "Загружать всё", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportRbUnit_Wizard_2 = QtGui.QDialog()
    ui = Ui_ImportRbUnit_Wizard_2()
    ui.setupUi(ImportRbUnit_Wizard_2)
    ImportRbUnit_Wizard_2.show()
    sys.exit(app.exec_())

