# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\SimplePrintDialog.ui'
#
# Created: Fri Jun 15 12:17:03 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(196, 72)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout.setContentsMargins(9, 9, -1, 9)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.navigLayout = QtGui.QHBoxLayout()
        self.navigLayout.setObjectName(_fromUtf8("navigLayout"))
        self.btnPrev = QtGui.QPushButton(Dialog)
        self.btnPrev.setEnabled(False)
        self.btnPrev.setObjectName(_fromUtf8("btnPrev"))
        self.navigLayout.addWidget(self.btnPrev)
        self.btnNext = QtGui.QPushButton(Dialog)
        self.btnNext.setEnabled(False)
        self.btnNext.setObjectName(_fromUtf8("btnNext"))
        self.navigLayout.addWidget(self.btnNext)
        self.verticalLayout.addLayout(self.navigLayout)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.btnPrev, QtCore.SIGNAL(_fromUtf8("pressed()")), Dialog.toPrev)
        QtCore.QObject.connect(self.btnNext, QtCore.SIGNAL(_fromUtf8("pressed()")), Dialog.toNext)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPrev.setText(QtGui.QApplication.translate("Dialog", "<<  Назад", None, QtGui.QApplication.UnicodeUTF8))
        self.btnNext.setText(QtGui.QApplication.translate("Dialog", "Вперёд  >>", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

