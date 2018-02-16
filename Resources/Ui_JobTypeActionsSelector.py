# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Resources\JobTypeActionsSelector.ui'
#
# Created: Fri Jun 15 12:17:44 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_JobTypeActionsSelectorDialog(object):
    def setupUi(self, JobTypeActionsSelectorDialog):
        JobTypeActionsSelectorDialog.setObjectName(_fromUtf8("JobTypeActionsSelectorDialog"))
        JobTypeActionsSelectorDialog.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(JobTypeActionsSelectorDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tblActionTypes = CInDocTableView(JobTypeActionsSelectorDialog)
        self.tblActionTypes.setObjectName(_fromUtf8("tblActionTypes"))
        self.verticalLayout.addWidget(self.tblActionTypes)
        self.buttonBox = CApplyResetDialogButtonBox(JobTypeActionsSelectorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(JobTypeActionsSelectorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), JobTypeActionsSelectorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), JobTypeActionsSelectorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(JobTypeActionsSelectorDialog)

    def retranslateUi(self, JobTypeActionsSelectorDialog):
        JobTypeActionsSelectorDialog.setWindowTitle(QtGui.QApplication.translate("JobTypeActionsSelectorDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView
from library.DialogButtonBox import CApplyResetDialogButtonBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    JobTypeActionsSelectorDialog = QtGui.QDialog()
    ui = Ui_JobTypeActionsSelectorDialog()
    ui.setupUi(JobTypeActionsSelectorDialog)
    JobTypeActionsSelectorDialog.show()
    sys.exit(app.exec_())

