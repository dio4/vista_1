# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ClientAttachMonitoring.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ClientAttachMonitoring(object):
    def setupUi(self, ClientAttachMonitoring):
        ClientAttachMonitoring.setObjectName(_fromUtf8("ClientAttachMonitoring"))
        ClientAttachMonitoring.resize(427, 235)
        self.gridLayout = QtGui.QGridLayout(ClientAttachMonitoring)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(ClientAttachMonitoring)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.treeOrgStructure = CTreeView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeOrgStructure.sizePolicy().hasHeightForWidth())
        self.treeOrgStructure.setSizePolicy(sizePolicy)
        self.treeOrgStructure.setObjectName(_fromUtf8("treeOrgStructure"))
        self.tblOrgStructure = CTableView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblOrgStructure.sizePolicy().hasHeightForWidth())
        self.tblOrgStructure.setSizePolicy(sizePolicy)
        self.tblOrgStructure.setObjectName(_fromUtf8("tblOrgStructure"))
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(ClientAttachMonitoring)
        QtCore.QMetaObject.connectSlotsByName(ClientAttachMonitoring)

    def retranslateUi(self, ClientAttachMonitoring):
        ClientAttachMonitoring.setWindowTitle(_translate("ClientAttachMonitoring", "Form", None))

from library.TableView import CTableView
from library.TreeView import CTreeView
