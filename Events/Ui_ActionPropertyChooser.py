# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Events\ActionPropertyChooser.ui'
#
# Created: Fri Jun 15 12:15:03 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ActionPropertyChooserDialog(object):
    def setupUi(self, ActionPropertyChooserDialog):
        ActionPropertyChooserDialog.setObjectName(_fromUtf8("ActionPropertyChooserDialog"))
        ActionPropertyChooserDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ActionPropertyChooserDialog.resize(233, 320)
        self.gridlayout = QtGui.QGridLayout(ActionPropertyChooserDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ActionPropertyChooserDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.tblChoose = CInDocTableView(ActionPropertyChooserDialog)
        self.tblChoose.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tblChoose.setDragEnabled(True)
        self.tblChoose.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.tblChoose.setObjectName(_fromUtf8("tblChoose"))
        self.gridlayout.addWidget(self.tblChoose, 0, 0, 1, 1)
        self.chkShowUnit = QtGui.QCheckBox(ActionPropertyChooserDialog)
        self.chkShowUnit.setTristate(True)
        self.chkShowUnit.setObjectName(_fromUtf8("chkShowUnit"))
        self.gridlayout.addWidget(self.chkShowUnit, 1, 0, 1, 1)
        self.chkShowNorm = QtGui.QCheckBox(ActionPropertyChooserDialog)
        self.chkShowNorm.setTristate(True)
        self.chkShowNorm.setObjectName(_fromUtf8("chkShowNorm"))
        self.gridlayout.addWidget(self.chkShowNorm, 2, 0, 1, 1)

        self.retranslateUi(ActionPropertyChooserDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ActionPropertyChooserDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ActionPropertyChooserDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ActionPropertyChooserDialog)
        ActionPropertyChooserDialog.setTabOrder(self.tblChoose, self.chkShowUnit)
        ActionPropertyChooserDialog.setTabOrder(self.chkShowUnit, self.chkShowNorm)
        ActionPropertyChooserDialog.setTabOrder(self.chkShowNorm, self.buttonBox)

    def retranslateUi(self, ActionPropertyChooserDialog):
        ActionPropertyChooserDialog.setWindowTitle(QtGui.QApplication.translate("ActionPropertyChooserDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.chkShowUnit.setText(QtGui.QApplication.translate("ActionPropertyChooserDialog", "Показывать единицы измерения", None, QtGui.QApplication.UnicodeUTF8))
        self.chkShowNorm.setText(QtGui.QApplication.translate("ActionPropertyChooserDialog", "Показывать норму", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ActionPropertyChooserDialog = QtGui.QDialog()
    ui = Ui_ActionPropertyChooserDialog()
    ui.setupUi(ActionPropertyChooserDialog)
    ActionPropertyChooserDialog.show()
    sys.exit(app.exec_())

