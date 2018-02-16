# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportTariff_Wizard_1.ui'
#
# Created: Fri Jun 15 12:16:08 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportTariff_Wizard_1(object):
    def setupUi(self, ExportTariff_Wizard_1):
        ExportTariff_Wizard_1.setObjectName(_fromUtf8("ExportTariff_Wizard_1"))
        ExportTariff_Wizard_1.setWindowModality(QtCore.Qt.NonModal)
        ExportTariff_Wizard_1.resize(400, 272)
        self.gridLayout = QtGui.QGridLayout(ExportTariff_Wizard_1)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkExportAll = QtGui.QCheckBox(ExportTariff_Wizard_1)
        self.chkExportAll.setObjectName(_fromUtf8("chkExportAll"))
        self.gridLayout.addWidget(self.chkExportAll, 0, 0, 1, 2)
        self.tblItems = CInDocTableView(ExportTariff_Wizard_1)
        self.tblItems.setTabKeyNavigation(False)
        self.tblItems.setAlternatingRowColors(True)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 1, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(229, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.btnSelectAll = QtGui.QPushButton(ExportTariff_Wizard_1)
        self.btnSelectAll.setObjectName(_fromUtf8("btnSelectAll"))
        self.gridLayout.addWidget(self.btnSelectAll, 2, 1, 1, 1)
        self.btnClearSelection = QtGui.QPushButton(ExportTariff_Wizard_1)
        self.btnClearSelection.setObjectName(_fromUtf8("btnClearSelection"))
        self.gridLayout.addWidget(self.btnClearSelection, 2, 2, 1, 1)

        self.retranslateUi(ExportTariff_Wizard_1)
        QtCore.QMetaObject.connectSlotsByName(ExportTariff_Wizard_1)
        ExportTariff_Wizard_1.setTabOrder(self.chkExportAll, self.tblItems)
        ExportTariff_Wizard_1.setTabOrder(self.tblItems, self.btnSelectAll)
        ExportTariff_Wizard_1.setTabOrder(self.btnSelectAll, self.btnClearSelection)

    def retranslateUi(self, ExportTariff_Wizard_1):
        ExportTariff_Wizard_1.setWindowTitle(QtGui.QApplication.translate("ExportTariff_Wizard_1", "Выбор экспортируемых тарифов", None, QtGui.QApplication.UnicodeUTF8))
        self.chkExportAll.setText(QtGui.QApplication.translate("ExportTariff_Wizard_1", "Выгружать всё", None, QtGui.QApplication.UnicodeUTF8))
        self.tblItems.setWhatsThis(QtGui.QApplication.translate("ExportTariff_Wizard_1", "список записей", "ура!", QtGui.QApplication.UnicodeUTF8))
        self.btnSelectAll.setText(QtGui.QApplication.translate("ExportTariff_Wizard_1", "Выбрать все", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClearSelection.setText(QtGui.QApplication.translate("ExportTariff_Wizard_1", "Очистить", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportTariff_Wizard_1 = QtGui.QDialog()
    ui = Ui_ExportTariff_Wizard_1()
    ui.setupUi(ExportTariff_Wizard_1)
    ExportTariff_Wizard_1.show()
    sys.exit(app.exec_())

