# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\Progress.ui'
#
# Created: Fri Jun 15 12:15:30 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        ProgressDialog.setObjectName(_fromUtf8("ProgressDialog"))
        ProgressDialog.resize(428, 76)
        self.vboxlayout = QtGui.QVBoxLayout(ProgressDialog)
        self.vboxlayout.setMargin(4)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.lblStage = QtGui.QLabel(ProgressDialog)
        self.lblStage.setText(_fromUtf8(""))
        self.lblStage.setObjectName(_fromUtf8("lblStage"))
        self.vboxlayout.addWidget(self.lblStage)
        self.progressBar = QtGui.QProgressBar(ProgressDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.vboxlayout.addWidget(self.progressBar)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        spacerItem = QtGui.QSpacerItem(331, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.btnCancel = QtGui.QPushButton(ProgressDialog)
        self.btnCancel.setDefault(True)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.hboxlayout.addWidget(self.btnCancel)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.retranslateUi(ProgressDialog)
        QtCore.QObject.connect(self.btnCancel, QtCore.SIGNAL(_fromUtf8("clicked()")), ProgressDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(ProgressDialog)

    def retranslateUi(self, ProgressDialog):
        ProgressDialog.setWindowTitle(QtGui.QApplication.translate("ProgressDialog", "Процесс выгрузки в EIS OMS", None, QtGui.QApplication.UnicodeUTF8))
        self.progressBar.setFormat(QtGui.QApplication.translate("ProgressDialog", "%v из %m", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("ProgressDialog", "Отмена", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ProgressDialog = QtGui.QDialog()
    ui = Ui_ProgressDialog()
    ui.setupUi(ProgressDialog)
    ProgressDialog.show()
    sys.exit(app.exec_())

