# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportActionProperty.ui'
#
# Created: Fri Jun 15 12:15:15 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportActionProperty(object):
    def setupUi(self, ImportActionProperty):
        ImportActionProperty.setObjectName(_fromUtf8("ImportActionProperty"))
        ImportActionProperty.setWindowModality(QtCore.Qt.NonModal)
        ImportActionProperty.resize(593, 450)
        self.gridlayout = QtGui.QGridLayout(ImportActionProperty)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.splitterTree = QtGui.QSplitter(ImportActionProperty)
        self.splitterTree.setOrientation(QtCore.Qt.Horizontal)
        self.splitterTree.setObjectName(_fromUtf8("splitterTree"))
        self.tblNew = CTableView(self.splitterTree)
        self.tblNew.setTabKeyNavigation(False)
        self.tblNew.setAlternatingRowColors(True)
        self.tblNew.setObjectName(_fromUtf8("tblNew"))
        self.gridlayout.addWidget(self.splitterTree, 3, 0, 1, 1)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.btnSelectAll = QtGui.QPushButton(ImportActionProperty)
        self.btnSelectAll.setObjectName(_fromUtf8("btnSelectAll"))
        self.hboxlayout.addWidget(self.btnSelectAll)
        self.btnClearSelection = QtGui.QPushButton(ImportActionProperty)
        self.btnClearSelection.setObjectName(_fromUtf8("btnClearSelection"))
        self.hboxlayout.addWidget(self.btnClearSelection)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.btnReplace = QtGui.QPushButton(ImportActionProperty)
        self.btnReplace.setObjectName(_fromUtf8("btnReplace"))
        self.hboxlayout.addWidget(self.btnReplace)
        self.btnSkip = QtGui.QPushButton(ImportActionProperty)
        self.btnSkip.setObjectName(_fromUtf8("btnSkip"))
        self.hboxlayout.addWidget(self.btnSkip)
        self.gridlayout.addLayout(self.hboxlayout, 4, 0, 1, 1)
        self.statusBar = QtGui.QStatusBar(ImportActionProperty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusBar.sizePolicy().hasHeightForWidth())
        self.statusBar.setSizePolicy(sizePolicy)
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        self.gridlayout.addWidget(self.statusBar, 5, 0, 1, 1)
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.label = QtGui.QLabel(ImportActionProperty)
        self.label.setObjectName(_fromUtf8("label"))
        self.vboxlayout.addWidget(self.label)
        self.gridlayout.addLayout(self.vboxlayout, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(ImportActionProperty)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridlayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.txtActionInfo = QtGui.QTextBrowser(ImportActionProperty)
        self.txtActionInfo.setObjectName(_fromUtf8("txtActionInfo"))
        self.gridlayout.addWidget(self.txtActionInfo, 1, 0, 1, 1)

        self.retranslateUi(ImportActionProperty)
        QtCore.QMetaObject.connectSlotsByName(ImportActionProperty)

    def retranslateUi(self, ImportActionProperty):
        ImportActionProperty.setWindowTitle(QtGui.QApplication.translate("ImportActionProperty", "Список записей", None, QtGui.QApplication.UnicodeUTF8))
        self.tblNew.setWhatsThis(QtGui.QApplication.translate("ImportActionProperty", "список записей", "ура!", QtGui.QApplication.UnicodeUTF8))
        self.btnSelectAll.setText(QtGui.QApplication.translate("ImportActionProperty", "Выбрать все", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClearSelection.setText(QtGui.QApplication.translate("ImportActionProperty", "Очистить", None, QtGui.QApplication.UnicodeUTF8))
        self.btnReplace.setText(QtGui.QApplication.translate("ImportActionProperty", "Добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSkip.setText(QtGui.QApplication.translate("ImportActionProperty", "П&ропустить", None, QtGui.QApplication.UnicodeUTF8))
        self.statusBar.setToolTip(QtGui.QApplication.translate("ImportActionProperty", "A status bar", None, QtGui.QApplication.UnicodeUTF8))
        self.statusBar.setWhatsThis(QtGui.QApplication.translate("ImportActionProperty", "A status bar.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportActionProperty", "Для имортируемого свойства типа действия", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ImportActionProperty", "найдены следующие <b>совпадающие</b> свойства. Выделите свойства для замены", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportActionProperty = QtGui.QDialog()
    ui = Ui_ImportActionProperty()
    ui.setupUi(ImportActionProperty)
    ImportActionProperty.show()
    sys.exit(app.exec_())

