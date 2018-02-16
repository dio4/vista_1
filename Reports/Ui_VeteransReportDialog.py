# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\VeteransReportDialog.ui'
#
# Created: Fri Jun 15 12:17:59 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_VeteransReportDialog(object):
    def setupUi(self, VeteransReportDialog):
        VeteransReportDialog.setObjectName(_fromUtf8("VeteransReportDialog"))
        VeteransReportDialog.resize(400, 335)
        self.buttonBox = QtGui.QDialogButtonBox(VeteransReportDialog)
        self.buttonBox.setGeometry(QtCore.QRect(220, 300, 176, 27))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(VeteransReportDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), VeteransReportDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), VeteransReportDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(VeteransReportDialog)

    def retranslateUi(self, VeteransReportDialog):
        VeteransReportDialog.setWindowTitle(QtGui.QApplication.translate("VeteransReportDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    VeteransReportDialog = QtGui.QDialog()
    ui = Ui_VeteransReportDialog()
    ui.setupUi(VeteransReportDialog)
    VeteransReportDialog.show()
    sys.exit(app.exec_())

