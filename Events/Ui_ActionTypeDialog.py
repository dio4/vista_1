# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Events\ActionTypeDialog.ui'
#
# Created: Fri Jun 15 12:16:36 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ActionTypeDialog(object):
    def setupUi(self, ActionTypeDialog):
        ActionTypeDialog.setObjectName(_fromUtf8("ActionTypeDialog"))
        ActionTypeDialog.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(ActionTypeDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblActionType = CTableView(ActionTypeDialog)
        self.tblActionType.setObjectName(_fromUtf8("tblActionType"))
        self.gridLayout.addWidget(self.tblActionType, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ActionTypeDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(ActionTypeDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ActionTypeDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ActionTypeDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ActionTypeDialog)

    def retranslateUi(self, ActionTypeDialog):
        ActionTypeDialog.setWindowTitle(QtGui.QApplication.translate("ActionTypeDialog", "Типы действий", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ActionTypeDialog = QtGui.QDialog()
    ui = Ui_ActionTypeDialog()
    ui.setupUi(ActionTypeDialog)
    ActionTypeDialog.show()
    sys.exit(app.exec_())

