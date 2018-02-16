# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PrevActionChooserDialog.ui'
#
# Created: Fri Mar 29 16:41:42 2013
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

class Ui_PrevActionChooserDialog(object):
    def setupUi(self, PrevActionChooserDialog):
        PrevActionChooserDialog.setObjectName(_fromUtf8("PrevActionChooserDialog"))
        PrevActionChooserDialog.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(PrevActionChooserDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblPrevActions = CTableView(PrevActionChooserDialog)
        self.tblPrevActions.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tblPrevActions.setObjectName(_fromUtf8("tblPrevActions"))
        self.gridLayout.addWidget(self.tblPrevActions, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PrevActionChooserDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(PrevActionChooserDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PrevActionChooserDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PrevActionChooserDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PrevActionChooserDialog)

    def retranslateUi(self, PrevActionChooserDialog):
        PrevActionChooserDialog.setWindowTitle(_translate("PrevActionChooserDialog", "Dialog", None))

from library.TableView import CTableView
