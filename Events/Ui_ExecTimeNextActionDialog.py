# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Events\ExecTimeNextActionDialog.ui'
#
# Created: Fri Jun 15 12:17:51 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExecTimeNextActionDialog(object):
    def setupUi(self, ExecTimeNextActionDialog):
        ExecTimeNextActionDialog.setObjectName(_fromUtf8("ExecTimeNextActionDialog"))
        ExecTimeNextActionDialog.resize(349, 98)
        self.gridLayout = QtGui.QGridLayout(ExecTimeNextActionDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtExecTimeNew = QtGui.QTimeEdit(ExecTimeNextActionDialog)
        self.edtExecTimeNew.setObjectName(_fromUtf8("edtExecTimeNew"))
        self.gridLayout.addWidget(self.edtExecTimeNew, 0, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 2, 1, 1)
        self.btnExecTimeOld = QtGui.QPushButton(ExecTimeNextActionDialog)
        self.btnExecTimeOld.setText(_fromUtf8(""))
        self.btnExecTimeOld.setObjectName(_fromUtf8("btnExecTimeOld"))
        self.gridLayout.addWidget(self.btnExecTimeOld, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ExecTimeNextActionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 2, 1, 2)
        self.lblExecTimeNew = QtGui.QLabel(ExecTimeNextActionDialog)
        self.lblExecTimeNew.setObjectName(_fromUtf8("lblExecTimeNew"))
        self.gridLayout.addWidget(self.lblExecTimeNew, 0, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ExecTimeNextActionDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 1, 1, 1, 3)
        self.label = QtGui.QLabel(ExecTimeNextActionDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.retranslateUi(ExecTimeNextActionDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ExecTimeNextActionDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ExecTimeNextActionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ExecTimeNextActionDialog)

    def retranslateUi(self, ExecTimeNextActionDialog):
        ExecTimeNextActionDialog.setWindowTitle(QtGui.QApplication.translate("ExecTimeNextActionDialog", "Время выполнения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblExecTimeNew.setText(QtGui.QApplication.translate("ExecTimeNextActionDialog", "Время выполнения", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ExecTimeNextActionDialog", "Исполнитель", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExecTimeNextActionDialog = QtGui.QDialog()
    ui = Ui_ExecTimeNextActionDialog()
    ui.setupUi(ExecTimeNextActionDialog)
    ExecTimeNextActionDialog.show()
    sys.exit(app.exec_())

