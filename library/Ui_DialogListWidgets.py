# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\DialogListWidgets.ui'
#
# Created: Fri Jun 15 12:17:31 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DialogListWidgets(object):
    def setupUi(self, DialogListWidgets):
        DialogListWidgets.setObjectName(_fromUtf8("DialogListWidgets"))
        DialogListWidgets.resize(400, 300)

        self.retranslateUi(DialogListWidgets)
        QtCore.QMetaObject.connectSlotsByName(DialogListWidgets)

    def retranslateUi(self, DialogListWidgets):
        DialogListWidgets.setWindowTitle(QtGui.QApplication.translate("DialogListWidgets", "Form", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DialogListWidgets = QtGui.QWidget()
    ui = Ui_DialogListWidgets()
    ui.setupUi(DialogListWidgets)
    DialogListWidgets.show()
    sys.exit(app.exec_())

