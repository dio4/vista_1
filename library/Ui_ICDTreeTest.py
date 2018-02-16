# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\ICDTreeTest.ui'
#
# Created: Fri Jun 15 12:15:29 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TestDialog(object):
    def setupUi(self, TestDialog):
        TestDialog.setObjectName(_fromUtf8("TestDialog"))
        TestDialog.resize(400, 103)
        self.gridlayout = QtGui.QGridLayout(TestDialog)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.edtD3 = CICDCodeEditEx(TestDialog)
        self.edtD3.setObjectName(_fromUtf8("edtD3"))
        self.gridlayout.addWidget(self.edtD3, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(241, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 131, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(TestDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 2, 0, 1, 2)

        self.retranslateUi(TestDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TestDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TestDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TestDialog)

    def retranslateUi(self, TestDialog):
        TestDialog.setWindowTitle(QtGui.QApplication.translate("TestDialog", "Коды МКБ", None, QtGui.QApplication.UnicodeUTF8))

from library.ICDCodeEdit import CICDCodeEditEx

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TestDialog = QtGui.QDialog()
    ui = Ui_TestDialog()
    ui.setupUi(TestDialog)
    TestDialog.show()
    sys.exit(app.exec_())

