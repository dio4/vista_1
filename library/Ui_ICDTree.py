# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\ICDTree.ui'
#
# Created: Fri Jun 15 12:15:29 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ICDTreePopup(object):
    def setupUi(self, ICDTreePopup):
        ICDTreePopup.setObjectName(_fromUtf8("ICDTreePopup"))
        ICDTreePopup.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ICDTreePopup)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.tabWidget = QtGui.QTabWidget(ICDTreePopup)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabTree = QtGui.QWidget()
        self.tabTree.setObjectName(_fromUtf8("tabTree"))
        self.vboxlayout = QtGui.QVBoxLayout(self.tabTree)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setMargin(4)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.treeView = CICDTreeView(self.tabTree)
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.vboxlayout.addWidget(self.treeView)
        self.tabWidget.addTab(self.tabTree, _fromUtf8(""))
        self.tabSearch = QtGui.QWidget()
        self.tabSearch.setObjectName(_fromUtf8("tabSearch"))
        self.gridlayout1 = QtGui.QGridLayout(self.tabSearch)
        self.gridlayout1.setMargin(4)
        self.gridlayout1.setSpacing(4)
        self.gridlayout1.setObjectName(_fromUtf8("gridlayout1"))
        self.edtWords = QtGui.QLineEdit(self.tabSearch)
        self.edtWords.setObjectName(_fromUtf8("edtWords"))
        self.gridlayout1.addWidget(self.edtWords, 0, 0, 1, 1)
        self.btnSearch = QtGui.QToolButton(self.tabSearch)
        self.btnSearch.setAutoRaise(False)
        self.btnSearch.setObjectName(_fromUtf8("btnSearch"))
        self.gridlayout1.addWidget(self.btnSearch, 0, 1, 1, 1)
        self.tblSearchResult = CICDSearchResult(self.tabSearch)
        self.tblSearchResult.setObjectName(_fromUtf8("tblSearchResult"))
        self.gridlayout1.addWidget(self.tblSearchResult, 1, 0, 1, 2)
        self.tabWidget.addTab(self.tabSearch, _fromUtf8(""))
        self.gridlayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(ICDTreePopup)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ICDTreePopup)

    def retranslateUi(self, ICDTreePopup):
        ICDTreePopup.setWindowTitle(QtGui.QApplication.translate("ICDTreePopup", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTree), QtGui.QApplication.translate("ICDTreePopup", "&Номенклатура", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSearch.setText(QtGui.QApplication.translate("ICDTreePopup", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSearch.setShortcut(QtGui.QApplication.translate("ICDTreePopup", "Return", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSearch), QtGui.QApplication.translate("ICDTreePopup", "&Поиск", None, QtGui.QApplication.UnicodeUTF8))

from library.ICDTreeViews import CICDSearchResult, CICDTreeView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ICDTreePopup = QtGui.QWidget()
    ui = Ui_ICDTreePopup()
    ui.setupUi(ICDTreePopup)
    ICDTreePopup.show()
    sys.exit(app.exec_())

