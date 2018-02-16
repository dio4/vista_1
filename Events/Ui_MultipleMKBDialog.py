# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Events\MultipleMKBDialog.ui'
#
# Created: Fri Jun 15 12:17:59 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MultipleMKBDialog(object):
    def setupUi(self, MultipleMKBDialog):
        MultipleMKBDialog.setObjectName(_fromUtf8("MultipleMKBDialog"))
        MultipleMKBDialog.resize(251, 314)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MultipleMKBDialog.sizePolicy().hasHeightForWidth())
        MultipleMKBDialog.setSizePolicy(sizePolicy)
        self.tblMultipleMKB = CInDocTableView(MultipleMKBDialog)
        self.tblMultipleMKB.setGeometry(QtCore.QRect(0, 0, 251, 271))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblMultipleMKB.sizePolicy().hasHeightForWidth())
        self.tblMultipleMKB.setSizePolicy(sizePolicy)
        self.tblMultipleMKB.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tblMultipleMKB.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.tblMultipleMKB.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tblMultipleMKB.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tblMultipleMKB.setObjectName(_fromUtf8("tblMultipleMKB"))

        self.retranslateUi(MultipleMKBDialog)
        QtCore.QMetaObject.connectSlotsByName(MultipleMKBDialog)

    def retranslateUi(self, MultipleMKBDialog):
        MultipleMKBDialog.setWindowTitle(QtGui.QApplication.translate("MultipleMKBDialog", "Список диагнозов", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MultipleMKBDialog = QtGui.QDialog()
    ui = Ui_MultipleMKBDialog()
    ui.setupUi(MultipleMKBDialog)
    MultipleMKBDialog.show()
    sys.exit(app.exec_())

