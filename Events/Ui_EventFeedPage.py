# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EventFeedPage.ui'
#
# Created: Tue Apr 14 18:54:24 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_EventFeedPage(object):
    def setupUi(self, EventFeedPage):
        EventFeedPage.setObjectName(_fromUtf8("EventFeedPage"))
        EventFeedPage.resize(528, 535)
        self.gridLayout = QtGui.QGridLayout(EventFeedPage)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblFeed = CFeedInDocTableView(EventFeedPage)
        self.tblFeed.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblFeed.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblFeed.setObjectName(_fromUtf8("tblFeed"))
        self.gridLayout.addWidget(self.tblFeed, 0, 0, 1, 5)
        self.lblCreateDate = QtGui.QLabel(EventFeedPage)
        self.lblCreateDate.setText(_fromUtf8(""))
        self.lblCreateDate.setObjectName(_fromUtf8("lblCreateDate"))
        self.gridLayout.addWidget(self.lblCreateDate, 1, 1, 1, 1)
        self.lblModifyDate = QtGui.QLabel(EventFeedPage)
        self.lblModifyDate.setText(_fromUtf8(""))
        self.lblModifyDate.setObjectName(_fromUtf8("lblModifyDate"))
        self.gridLayout.addWidget(self.lblModifyDate, 1, 2, 1, 1)
        self.btnFeedPrint = QtGui.QPushButton(EventFeedPage)
        self.btnFeedPrint.setEnabled(True)
        self.btnFeedPrint.setObjectName(_fromUtf8("btnFeedPrint"))
        self.gridLayout.addWidget(self.btnFeedPrint, 1, 3, 1, 1)
        self.btnGetMenu = QtGui.QPushButton(EventFeedPage)
        self.btnGetMenu.setEnabled(True)
        self.btnGetMenu.setObjectName(_fromUtf8("btnGetMenu"))
        self.gridLayout.addWidget(self.btnGetMenu, 1, 4, 1, 1)

        self.retranslateUi(EventFeedPage)
        QtCore.QMetaObject.connectSlotsByName(EventFeedPage)

    def retranslateUi(self, EventFeedPage):
        EventFeedPage.setWindowTitle(_translate("EventFeedPage", "Form", None))
        self.btnFeedPrint.setText(_translate("EventFeedPage", "Печать", None))
        self.btnGetMenu.setText(_translate("EventFeedPage", "Шаблон", None))

from Events.EventFeedModel import CFeedInDocTableView
