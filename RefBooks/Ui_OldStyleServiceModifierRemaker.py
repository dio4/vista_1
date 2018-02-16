# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\OldStyleServiceModirierRemaker.ui'
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

class Ui_OldStyleServiceModifierRemakerDialogForm(object):
    def setupUi(self, OldStyleServiceModifierRemakerDialogForm):
        OldStyleServiceModifierRemakerDialogForm.setObjectName(_fromUtf8("OldStyleServiceModifierRemakerDialogForm"))
        OldStyleServiceModifierRemakerDialogForm.resize(640, 590)
        self.gridLayout = QtGui.QGridLayout(OldStyleServiceModifierRemakerDialogForm)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnStart = QtGui.QPushButton(OldStyleServiceModifierRemakerDialogForm)
        self.btnStart.setObjectName(_fromUtf8("btnStart"))
        self.horizontalLayout.addWidget(self.btnStart)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnClose = QtGui.QPushButton(OldStyleServiceModifierRemakerDialogForm)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.horizontalLayout.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.logBrowser = QtGui.QTextBrowser(OldStyleServiceModifierRemakerDialogForm)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logBrowser.sizePolicy().hasHeightForWidth())
        self.logBrowser.setSizePolicy(sizePolicy)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 0, 0, 1, 2)

        self.retranslateUi(OldStyleServiceModifierRemakerDialogForm)
        QtCore.QMetaObject.connectSlotsByName(OldStyleServiceModifierRemakerDialogForm)

    def retranslateUi(self, OldStyleServiceModifierRemakerDialogForm):
        OldStyleServiceModifierRemakerDialogForm.setWindowTitle(_translate("OldStyleServiceModifierRemakerDialogForm", "Исправить модификаторы услуг старого типа", None))
        self.btnStart.setText(_translate("OldStyleServiceModifierRemakerDialogForm", "Исправить", None))
        self.btnClose.setText(_translate("OldStyleServiceModifierRemakerDialogForm", "Закрыть", None))

