# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Events\PropertyHistoryDialog.ui'
#
# Created: Fri Jun 15 12:15:06 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PropertyHistoryDialog(object):
    def setupUi(self, PropertyHistoryDialog):
        PropertyHistoryDialog.setObjectName(_fromUtf8("PropertyHistoryDialog"))
        PropertyHistoryDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PropertyHistoryDialog.resize(651, 291)
        self.gridlayout = QtGui.QGridLayout(PropertyHistoryDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.buttonBox = QtGui.QDialogButtonBox(PropertyHistoryDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tblValues = CInDocTableView(PropertyHistoryDialog)
        self.tblValues.setObjectName(_fromUtf8("tblValues"))
        self.gridlayout.addWidget(self.tblValues, 0, 0, 1, 1)

        self.retranslateUi(PropertyHistoryDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PropertyHistoryDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PropertyHistoryDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PropertyHistoryDialog)

    def retranslateUi(self, PropertyHistoryDialog):
        PropertyHistoryDialog.setWindowTitle(QtGui.QApplication.translate("PropertyHistoryDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PropertyHistoryDialog = QtGui.QDialog()
    ui = Ui_PropertyHistoryDialog()
    ui.setupUi(PropertyHistoryDialog)
    PropertyHistoryDialog.show()
    sys.exit(app.exec_())

