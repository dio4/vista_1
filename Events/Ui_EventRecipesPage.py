# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EventRecipesPage.ui'
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

class Ui_EventRecipesPageWidget(object):
    def setupUi(self, EventRecipesPageWidget):
        EventRecipesPageWidget.setObjectName(_fromUtf8("EventRecipesPageWidget"))
        EventRecipesPageWidget.resize(645, 370)
        self.verticalLayout = QtGui.QVBoxLayout(EventRecipesPageWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(EventRecipesPageWidget)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 633, 358))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tblItems = CTableView(self.scrollAreaWidgetContents)
        self.tblItems.setMinimumSize(QtCore.QSize(0, 300))
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.verticalLayout_2.addWidget(self.tblItems)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(EventRecipesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(EventRecipesPageWidget)

    def retranslateUi(self, EventRecipesPageWidget):
        EventRecipesPageWidget.setWindowTitle(_translate("EventRecipesPageWidget", "Form", None))

from library.TableView import CTableView
