# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportHL7_Wizard_1.ui'
#
# Created: Fri Jun 15 12:15:11 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportHL7_Wizard_1(object):
    def setupUi(self, ExportHL7_Wizard_1):
        ExportHL7_Wizard_1.setObjectName(_fromUtf8("ExportHL7_Wizard_1"))
        ExportHL7_Wizard_1.setWindowModality(QtCore.Qt.NonModal)
        ExportHL7_Wizard_1.resize(593, 450)
        self.gridlayout = QtGui.QGridLayout(ExportHL7_Wizard_1)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.checkExportAll = QtGui.QCheckBox(ExportHL7_Wizard_1)
        self.checkExportAll.setObjectName(_fromUtf8("checkExportAll"))
        self.hboxlayout.addWidget(self.checkExportAll)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.checkOnlyOwn = QtGui.QCheckBox(ExportHL7_Wizard_1)
        self.checkOnlyOwn.setChecked(True)
        self.checkOnlyOwn.setObjectName(_fromUtf8("checkOnlyOwn"))
        self.hboxlayout1.addWidget(self.checkOnlyOwn)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.btnClearSelection = QtGui.QPushButton(ExportHL7_Wizard_1)
        self.btnClearSelection.setObjectName(_fromUtf8("btnClearSelection"))
        self.hboxlayout1.addWidget(self.btnClearSelection)
        self.gridlayout.addLayout(self.hboxlayout1, 4, 0, 1, 1)
        self.statusBar = QtGui.QStatusBar(ExportHL7_Wizard_1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusBar.sizePolicy().hasHeightForWidth())
        self.statusBar.setSizePolicy(sizePolicy)
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        self.gridlayout.addWidget(self.statusBar, 6, 0, 1, 1)
        self.splitterTree = QtGui.QSplitter(ExportHL7_Wizard_1)
        self.splitterTree.setOrientation(QtCore.Qt.Horizontal)
        self.splitterTree.setObjectName(_fromUtf8("splitterTree"))
        self.tblItems = CTableView(self.splitterTree)
        self.tblItems.setTabKeyNavigation(False)
        self.tblItems.setAlternatingRowColors(True)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridlayout.addWidget(self.splitterTree, 2, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(ExportHL7_Wizard_1)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.rbAddPers = QtGui.QRadioButton(self.groupBox)
        self.rbAddPers.setObjectName(_fromUtf8("rbAddPers"))
        self.verticalLayout.addWidget(self.rbAddPers)
        self.rbUpdatePers = QtGui.QRadioButton(self.groupBox)
        self.rbUpdatePers.setChecked(True)
        self.rbUpdatePers.setObjectName(_fromUtf8("rbUpdatePers"))
        self.verticalLayout.addWidget(self.rbUpdatePers)
        self.rbDeletePers = QtGui.QRadioButton(self.groupBox)
        self.rbDeletePers.setObjectName(_fromUtf8("rbDeletePers"))
        self.verticalLayout.addWidget(self.rbDeletePers)
        self.rbTerminatePers = QtGui.QRadioButton(self.groupBox)
        self.rbTerminatePers.setObjectName(_fromUtf8("rbTerminatePers"))
        self.verticalLayout.addWidget(self.rbTerminatePers)
        self.gridlayout.addWidget(self.groupBox, 5, 0, 1, 1)

        self.retranslateUi(ExportHL7_Wizard_1)
        QtCore.QMetaObject.connectSlotsByName(ExportHL7_Wizard_1)

    def retranslateUi(self, ExportHL7_Wizard_1):
        ExportHL7_Wizard_1.setWindowTitle(QtGui.QApplication.translate("ExportHL7_Wizard_1", "Список сотрудников", None, QtGui.QApplication.UnicodeUTF8))
        self.checkExportAll.setText(QtGui.QApplication.translate("ExportHL7_Wizard_1", "Выгружать всё", None, QtGui.QApplication.UnicodeUTF8))
        self.checkOnlyOwn.setText(QtGui.QApplication.translate("ExportHL7_Wizard_1", "Только свои", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClearSelection.setText(QtGui.QApplication.translate("ExportHL7_Wizard_1", "Очистить", None, QtGui.QApplication.UnicodeUTF8))
        self.statusBar.setToolTip(QtGui.QApplication.translate("ExportHL7_Wizard_1", "A status bar", None, QtGui.QApplication.UnicodeUTF8))
        self.statusBar.setWhatsThis(QtGui.QApplication.translate("ExportHL7_Wizard_1", "A status bar.", None, QtGui.QApplication.UnicodeUTF8))
        self.tblItems.setWhatsThis(QtGui.QApplication.translate("ExportHL7_Wizard_1", "список записей", "ура!", QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("ExportHL7_Wizard_1", "Тип события для выгрузки", None, QtGui.QApplication.UnicodeUTF8))
        self.rbAddPers.setText(QtGui.QApplication.translate("ExportHL7_Wizard_1", "B01 Добавить личное дело сотрудника", None, QtGui.QApplication.UnicodeUTF8))
        self.rbUpdatePers.setText(QtGui.QApplication.translate("ExportHL7_Wizard_1", "B02 Обновить личное дело сотрудника", None, QtGui.QApplication.UnicodeUTF8))
        self.rbDeletePers.setText(QtGui.QApplication.translate("ExportHL7_Wizard_1", "B03 Удалить личное дело сотрудника", None, QtGui.QApplication.UnicodeUTF8))
        self.rbTerminatePers.setText(QtGui.QApplication.translate("ExportHL7_Wizard_1", "B06 Закрыть личное дело сотрудника", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportHL7_Wizard_1 = QtGui.QDialog()
    ui = Ui_ExportHL7_Wizard_1()
    ui.setupUi(ExportHL7_Wizard_1)
    ExportHL7_Wizard_1.show()
    sys.exit(app.exec_())

