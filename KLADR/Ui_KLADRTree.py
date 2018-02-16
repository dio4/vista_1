# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\KLADR\KLADRTree.ui'
#
# Created: Fri Jun 15 12:15:27 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_KLADRTreePopup(object):
    def setupUi(self, KLADRTreePopup):
        KLADRTreePopup.setObjectName(_fromUtf8("KLADRTreePopup"))
        KLADRTreePopup.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(KLADRTreePopup)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.tabWidget = QtGui.QTabWidget(KLADRTreePopup)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabTree = QtGui.QWidget()
        self.tabTree.setObjectName(_fromUtf8("tabTree"))
        self.vboxlayout = QtGui.QVBoxLayout(self.tabTree)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setMargin(4)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.treeView = CKLADRTreeView(self.tabTree)
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
        self.btnSearch.setObjectName(_fromUtf8("btnSearch"))
        self.gridlayout1.addWidget(self.btnSearch, 0, 1, 1, 1)
        self.tblSearchResult = CKLADRSearchResult(self.tabSearch)
        self.tblSearchResult.setObjectName(_fromUtf8("tblSearchResult"))
        self.gridlayout1.addWidget(self.tblSearchResult, 1, 0, 1, 2)
        self.tabWidget.addTab(self.tabSearch, _fromUtf8(""))
        self.gridlayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(KLADRTreePopup)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(KLADRTreePopup)

    def retranslateUi(self, KLADRTreePopup):
        KLADRTreePopup.setWindowTitle(QtGui.QApplication.translate("KLADRTreePopup", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTree), QtGui.QApplication.translate("KLADRTreePopup", "&КЛАДР", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSearch.setText(QtGui.QApplication.translate("KLADRTreePopup", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSearch), QtGui.QApplication.translate("KLADRTreePopup", "&Поиск", None, QtGui.QApplication.UnicodeUTF8))

from KLADRViews import CKLADRTreeView, CKLADRSearchResult

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    KLADRTreePopup = QtGui.QWidget()
    ui = Ui_KLADRTreePopup()
    ui.setupUi(KLADRTreePopup)
    KLADRTreePopup.show()
    sys.exit(app.exec_())

