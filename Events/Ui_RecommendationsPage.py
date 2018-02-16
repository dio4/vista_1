# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RecommendationsPage.ui'
#
# Created: Fri Jun 19 17:29:09 2015
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

class Ui_RecommendationsPage(object):
    def setupUi(self, RecommendationsPage):
        RecommendationsPage.setObjectName(_fromUtf8("RecommendationsPage"))
        RecommendationsPage.resize(379, 311)
        self.gridLayout = QtGui.QGridLayout(RecommendationsPage)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblRecommendations = CRecommendationsView(RecommendationsPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblRecommendations.sizePolicy().hasHeightForWidth())
        self.tblRecommendations.setSizePolicy(sizePolicy)
        self.tblRecommendations.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.tblRecommendations.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.tblRecommendations.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblRecommendations.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblRecommendations.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerItem)
        self.tblRecommendations.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerItem)
        self.tblRecommendations.setObjectName(_fromUtf8("tblRecommendations"))
        self.gridLayout.addWidget(self.tblRecommendations, 0, 0, 1, 1)

        self.retranslateUi(RecommendationsPage)
        QtCore.QMetaObject.connectSlotsByName(RecommendationsPage)

    def retranslateUi(self, RecommendationsPage):
        RecommendationsPage.setWindowTitle(_translate("RecommendationsPage", "Form", None))

from Events.Recommendations import CRecommendationsView
