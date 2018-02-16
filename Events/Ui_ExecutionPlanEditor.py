# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Events\ExecutionPlanEditor.ui'
#
# Created: Fri Jun 15 12:17:53 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExecutionPlanEditor(object):
    def setupUi(self, ExecutionPlanEditor):
        ExecutionPlanEditor.setObjectName(_fromUtf8("ExecutionPlanEditor"))
        ExecutionPlanEditor.resize(373, 272)
        self.gridLayout = QtGui.QGridLayout(ExecutionPlanEditor)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblPlanEditor = CExecutionPlanEditorTable(ExecutionPlanEditor)
        self.tblPlanEditor.setObjectName(_fromUtf8("tblPlanEditor"))
        self.gridLayout.addWidget(self.tblPlanEditor, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ExecutionPlanEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(ExecutionPlanEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ExecutionPlanEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ExecutionPlanEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(ExecutionPlanEditor)

    def retranslateUi(self, ExecutionPlanEditor):
        ExecutionPlanEditor.setWindowTitle(QtGui.QApplication.translate("ExecutionPlanEditor", "Выбранное время", None, QtGui.QApplication.UnicodeUTF8))

from ExecutionPlanEditorTable import CExecutionPlanEditorTable

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExecutionPlanEditor = QtGui.QDialog()
    ui = Ui_ExecutionPlanEditor()
    ui.setupUi(ExecutionPlanEditor)
    ExecutionPlanEditor.show()
    sys.exit(app.exec_())

