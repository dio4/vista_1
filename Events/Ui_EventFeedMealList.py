# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EventFeedMealList.ui'
#
# Created: Fri Apr 10 17:34:24 2015
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

class Ui_EventFeedMealListDialog(object):
    def setupUi(self, EventFeedMealListDialog):
        EventFeedMealListDialog.setObjectName(_fromUtf8("EventFeedMealListDialog"))
        EventFeedMealListDialog.resize(400, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(EventFeedMealListDialog.sizePolicy().hasHeightForWidth())
        EventFeedMealListDialog.setSizePolicy(sizePolicy)
        EventFeedMealListDialog.setMinimumSize(QtCore.QSize(400, 300))
        EventFeedMealListDialog.setMaximumSize(QtCore.QSize(400, 300))
        self.buttonBox = QtGui.QDialogButtonBox(EventFeedMealListDialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.tblMeals = CInDocTableView(EventFeedMealListDialog)
        self.tblMeals.setGeometry(QtCore.QRect(10, 10, 381, 221))
        self.tblMeals.setObjectName(_fromUtf8("tblMeals"))

        self.retranslateUi(EventFeedMealListDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EventFeedMealListDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EventFeedMealListDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EventFeedMealListDialog)

    def retranslateUi(self, EventFeedMealListDialog):
        EventFeedMealListDialog.setWindowTitle(_translate("EventFeedMealListDialog", "Список блюд", None))

from library.InDocTable import CInDocTableView
