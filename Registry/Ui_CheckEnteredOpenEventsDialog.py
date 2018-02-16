# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Registry\CheckEnteredOpenEventsDialog.ui'
#
# Created: Wed Jun 26 16:39:36 2013
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_CheckEnteredOpenEventsDialog(object):
    def setupUi(self, CheckEnteredOpenEventsDialog):
        CheckEnteredOpenEventsDialog.setObjectName(_fromUtf8("CheckEnteredOpenEventsDialog"))
        CheckEnteredOpenEventsDialog.resize(580, 478)
        self.gridLayout = QtGui.QGridLayout(CheckEnteredOpenEventsDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(CheckEnteredOpenEventsDialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.txtClientInfoEventsBrowser = CTextBrowser(self.splitter)
        self.txtClientInfoEventsBrowser.setFocusPolicy(QtCore.Qt.NoFocus)
        self.txtClientInfoEventsBrowser.setObjectName(_fromUtf8("txtClientInfoEventsBrowser"))
        self.tblOpenEvents = CTableView(self.splitter)
        self.tblOpenEvents.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tblOpenEvents.setObjectName(_fromUtf8("tblOpenEvents"))
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 4)
        self.btnCreate = QtGui.QPushButton(CheckEnteredOpenEventsDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnCreate.sizePolicy().hasHeightForWidth())
        self.btnCreate.setSizePolicy(sizePolicy)
        self.btnCreate.setMinimumSize(QtCore.QSize(100, 0))
        self.btnCreate.setFocusPolicy(QtCore.Qt.TabFocus)
        self.btnCreate.setDefault(True)
        self.btnCreate.setObjectName(_fromUtf8("btnCreate"))
        self.gridLayout.addWidget(self.btnCreate, 1, 0, 1, 1)
        self.btnOpen = QtGui.QPushButton(CheckEnteredOpenEventsDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnOpen.sizePolicy().hasHeightForWidth())
        self.btnOpen.setSizePolicy(sizePolicy)
        self.btnOpen.setMinimumSize(QtCore.QSize(100, 0))
        self.btnOpen.setFocusPolicy(QtCore.Qt.TabFocus)
        self.btnOpen.setObjectName(_fromUtf8("btnOpen"))
        self.gridLayout.addWidget(self.btnOpen, 1, 1, 1, 1)
        self.btnReverse = QtGui.QPushButton(CheckEnteredOpenEventsDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnReverse.sizePolicy().hasHeightForWidth())
        self.btnReverse.setSizePolicy(sizePolicy)
        self.btnReverse.setMinimumSize(QtCore.QSize(100, 0))
        self.btnReverse.setFocusPolicy(QtCore.Qt.TabFocus)
        self.btnReverse.setObjectName(_fromUtf8("btnReverse"))
        self.gridLayout.addWidget(self.btnReverse, 1, 2, 1, 1)
        self.btnClose = QtGui.QPushButton(CheckEnteredOpenEventsDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnClose.sizePolicy().hasHeightForWidth())
        self.btnClose.setSizePolicy(sizePolicy)
        self.btnClose.setMinimumSize(QtCore.QSize(100, 0))
        self.btnClose.setFocusPolicy(QtCore.Qt.TabFocus)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 1, 3, 1, 1)

        self.retranslateUi(CheckEnteredOpenEventsDialog)
        QtCore.QMetaObject.connectSlotsByName(CheckEnteredOpenEventsDialog)
        CheckEnteredOpenEventsDialog.setTabOrder(self.btnCreate, self.btnOpen)
        CheckEnteredOpenEventsDialog.setTabOrder(self.btnOpen, self.btnReverse)
        CheckEnteredOpenEventsDialog.setTabOrder(self.btnReverse, self.btnClose)

    def retranslateUi(self, CheckEnteredOpenEventsDialog):
        CheckEnteredOpenEventsDialog.setWindowTitle(_translate("CheckEnteredOpenEventsDialog", "Открытые события", None))
        self.btnCreate.setText(_translate("CheckEnteredOpenEventsDialog", "Создать", None))
        self.btnOpen.setText(_translate("CheckEnteredOpenEventsDialog", "Открыть", None))
        self.btnReverse.setText(_translate("CheckEnteredOpenEventsDialog", "Повторить", None))
        self.btnClose.setText(_translate("CheckEnteredOpenEventsDialog", "Отмена", None))

from library.TextBrowser import CTextBrowser
from library.TableView import CTableView
