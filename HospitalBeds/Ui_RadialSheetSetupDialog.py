# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\HospitalBeds\RadialSheetSetupDialog.ui'
#
# Created: Fri Jun 15 12:17:58 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_dialogSetupRadialSheet(object):
    def setupUi(self, dialogSetupRadialSheet):
        dialogSetupRadialSheet.setObjectName(_fromUtf8("dialogSetupRadialSheet"))
        dialogSetupRadialSheet.resize(198, 167)
        self.spinFields = QtGui.QSpinBox(dialogSetupRadialSheet)
        self.spinFields.setGeometry(QtCore.QRect(140, 30, 55, 25))
        self.spinFields.setObjectName(_fromUtf8("spinFields"))
        self.spinPoints = QtGui.QSpinBox(dialogSetupRadialSheet)
        self.spinPoints.setGeometry(QtCore.QRect(140, 70, 55, 25))
        self.spinPoints.setObjectName(_fromUtf8("spinPoints"))
        self.label = QtGui.QLabel(dialogSetupRadialSheet)
        self.label.setGeometry(QtCore.QRect(10, 30, 121, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(dialogSetupRadialSheet)
        self.label_2.setGeometry(QtCore.QRect(10, 70, 121, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.btnOK = QtGui.QPushButton(dialogSetupRadialSheet)
        self.btnOK.setGeometry(QtCore.QRect(110, 130, 80, 26))
        self.btnOK.setObjectName(_fromUtf8("btnOK"))

        self.retranslateUi(dialogSetupRadialSheet)
        QtCore.QMetaObject.connectSlotsByName(dialogSetupRadialSheet)

    def retranslateUi(self, dialogSetupRadialSheet):
        dialogSetupRadialSheet.setWindowTitle(QtGui.QApplication.translate("dialogSetupRadialSheet", "Настройки", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("dialogSetupRadialSheet", "Количество полей", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("dialogSetupRadialSheet", "Количество точек", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOK.setText(QtGui.QApplication.translate("dialogSetupRadialSheet", "OK", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dialogSetupRadialSheet = QtGui.QDialog()
    ui = Ui_dialogSetupRadialSheet()
    ui.setupUi(dialogSetupRadialSheet)
    dialogSetupRadialSheet.show()
    sys.exit(app.exec_())

