# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\TNMS\TNMSComboBoxTest.ui'
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

class Ui_TestDialog(object):
    def setupUi(self, TestDialog):
        TestDialog.setObjectName(_fromUtf8("TestDialog"))
        TestDialog.resize(400, 100)
        self.gridLayout = QtGui.QGridLayout(TestDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(TestDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        self.lblString = QtGui.QLabel(TestDialog)
        self.lblString.setObjectName(_fromUtf8("lblString"))
        self.gridLayout.addWidget(self.lblString, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.lblTNMS = QtGui.QLabel(TestDialog)
        self.lblTNMS.setObjectName(_fromUtf8("lblTNMS"))
        self.gridLayout.addWidget(self.lblTNMS, 1, 0, 1, 1)
        self.edtString = QtGui.QLineEdit(TestDialog)
        self.edtString.setObjectName(_fromUtf8("edtString"))
        self.gridLayout.addWidget(self.edtString, 0, 1, 1, 1)
        self.cmbTNMS = CTNMSComboBox(TestDialog)
        self.cmbTNMS.setObjectName(_fromUtf8("cmbTNMS"))
        self.gridLayout.addWidget(self.cmbTNMS, 1, 1, 1, 1)
        self.lblString.setBuddy(self.edtString)
        self.lblTNMS.setBuddy(self.cmbTNMS)

        self.retranslateUi(TestDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TestDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TestDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TestDialog)
        TestDialog.setTabOrder(self.edtString, self.cmbTNMS)
        TestDialog.setTabOrder(self.cmbTNMS, self.buttonBox)

    def retranslateUi(self, TestDialog):
        TestDialog.setWindowTitle(QtGui.QApplication.translate("TestDialog", "Испытание TNMS", None, QtGui.QApplication.UnicodeUTF8))
        self.lblString.setText(QtGui.QApplication.translate("TestDialog", "Строка, как она храниться в БД", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTNMS.setText(QtGui.QApplication.translate("TestDialog", "Комбо-бокс TNM+S", None, QtGui.QApplication.UnicodeUTF8))

from library.TNMS.TNMSComboBox import CTNMSComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TestDialog = QtGui.QDialog()
    ui = Ui_TestDialog()
    ui.setupUi(TestDialog)
    TestDialog.show()
    sys.exit(app.exec_())

