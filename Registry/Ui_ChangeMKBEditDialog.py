# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Registry\ChangeMKBEditDialog.ui'
#
# Created: Fri Jun 15 12:15:48 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ChangeMKBEditDialog(object):
    def setupUi(self, ChangeMKBEditDialog):
        ChangeMKBEditDialog.setObjectName(_fromUtf8("ChangeMKBEditDialog"))
        ChangeMKBEditDialog.resize(168, 62)
        self.gridLayout = QtGui.QGridLayout(ChangeMKBEditDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ChangeMKBEditDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edtMKB = CICDCodeEditEx(ChangeMKBEditDialog)
        self.edtMKB.setObjectName(_fromUtf8("edtMKB"))
        self.gridLayout.addWidget(self.edtMKB, 0, 1, 1, 1)
        self.edtMKBEx = CICDCodeEditEx(ChangeMKBEditDialog)
        self.edtMKBEx.setObjectName(_fromUtf8("edtMKBEx"))
        self.gridLayout.addWidget(self.edtMKBEx, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(61, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 19, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ChangeMKBEditDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 4)
        self.label.setBuddy(self.edtMKB)

        self.retranslateUi(ChangeMKBEditDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ChangeMKBEditDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ChangeMKBEditDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ChangeMKBEditDialog)
        ChangeMKBEditDialog.setTabOrder(self.edtMKB, self.edtMKBEx)
        ChangeMKBEditDialog.setTabOrder(self.edtMKBEx, self.buttonBox)

    def retranslateUi(self, ChangeMKBEditDialog):
        ChangeMKBEditDialog.setWindowTitle(QtGui.QApplication.translate("ChangeMKBEditDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ChangeMKBEditDialog", "Код МКБ", None, QtGui.QApplication.UnicodeUTF8))

from library.ICDCodeEdit import CICDCodeEditEx

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ChangeMKBEditDialog = QtGui.QDialog()
    ui = Ui_ChangeMKBEditDialog()
    ui.setupUi(ChangeMKBEditDialog)
    ChangeMKBEditDialog.show()
    sys.exit(app.exec_())

