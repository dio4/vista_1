# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/green/work/s11/Exchange/ExportR53NativePage3.ui'
#
# Created: Tue Jan 11 21:02:34 2011
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ExportPage3(object):
    def setupUi(self, ExportPage3):
        ExportPage3.setObjectName("ExportPage3")
        ExportPage3.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportPage3)
        self.gridlayout.setObjectName("gridlayout")
        self.lblDir = QtGui.QLabel(ExportPage3)
        self.lblDir.setObjectName("lblDir")
        self.gridlayout.addWidget(self.lblDir, 0, 0, 1, 1)
        self.edtDir = QtGui.QLineEdit(ExportPage3)
        self.edtDir.setObjectName("edtDir")
        self.gridlayout.addWidget(self.edtDir, 0, 1, 1, 1)
        self.btnSelectDir = QtGui.QToolButton(ExportPage3)
        self.btnSelectDir.setObjectName("btnSelectDir")
        self.gridlayout.addWidget(self.btnSelectDir, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(128, 241, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(ExportPage3)
        QtCore.QMetaObject.connectSlotsByName(ExportPage3)

    def retranslateUi(self, ExportPage3):
        ExportPage3.setWindowTitle(QtGui.QApplication.translate("ExportPage3", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDir.setText(QtGui.QApplication.translate("ExportPage3", "Сохранить в директорий", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectDir.setText(QtGui.QApplication.translate("ExportPage3", "...", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportPage3 = QtGui.QWidget()
    ui = Ui_ExportPage3()
    ui.setupUi(ExportPage3)
    ExportPage3.show()
    sys.exit(app.exec_())

