# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Accounting\PayStatusDialog.ui'
#
# Created: Fri Jun 15 12:15:00 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PayStatusDialog(object):
    def setupUi(self, PayStatusDialog):
        PayStatusDialog.setObjectName(_fromUtf8("PayStatusDialog"))
        PayStatusDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PayStatusDialog.resize(266, 202)
        self.gridlayout = QtGui.QGridLayout(PayStatusDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        spacerItem = QtGui.QSpacerItem(201, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 2, 1, 1, 2)
        self.edtNumber = QtGui.QLineEdit(PayStatusDialog)
        self.edtNumber.setMaxLength(20)
        self.edtNumber.setObjectName(_fromUtf8("edtNumber"))
        self.gridlayout.addWidget(self.edtNumber, 1, 1, 1, 1)
        self.rbnAccepted = QtGui.QRadioButton(PayStatusDialog)
        self.rbnAccepted.setChecked(True)
        self.rbnAccepted.setObjectName(_fromUtf8("rbnAccepted"))
        self.gridlayout.addWidget(self.rbnAccepted, 2, 0, 1, 1)
        self.lblNumber = QtGui.QLabel(PayStatusDialog)
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.gridlayout.addWidget(self.lblNumber, 1, 0, 1, 1)
        self.lblDate = QtGui.QLabel(PayStatusDialog)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridlayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.rbnRefused = QtGui.QRadioButton(PayStatusDialog)
        self.rbnRefused.setObjectName(_fromUtf8("rbnRefused"))
        self.gridlayout.addWidget(self.rbnRefused, 3, 0, 1, 1)
        self.lblPayRefuseType = QtGui.QLabel(PayStatusDialog)
        self.lblPayRefuseType.setEnabled(False)
        self.lblPayRefuseType.setObjectName(_fromUtf8("lblPayRefuseType"))
        self.gridlayout.addWidget(self.lblPayRefuseType, 4, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(81, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 0, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(81, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 1, 2, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(201, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem3, 3, 1, 1, 2)
        spacerItem4 = QtGui.QSpacerItem(20, 21, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem4, 6, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PayStatusDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 7, 0, 1, 3)
        self.cmbRefuseType = CRBComboBox(PayStatusDialog)
        self.cmbRefuseType.setEnabled(False)
        self.cmbRefuseType.setObjectName(_fromUtf8("cmbRefuseType"))
        self.gridlayout.addWidget(self.cmbRefuseType, 4, 1, 1, 2)
        self.edtDate = CDateEdit(PayStatusDialog)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridlayout.addWidget(self.edtDate, 0, 1, 1, 1)
        self.edtNote = QtGui.QLineEdit(PayStatusDialog)
        self.edtNote.setObjectName(_fromUtf8("edtNote"))
        self.gridlayout.addWidget(self.edtNote, 5, 1, 1, 2)
        self.lblNote = QtGui.QLabel(PayStatusDialog)
        self.lblNote.setObjectName(_fromUtf8("lblNote"))
        self.gridlayout.addWidget(self.lblNote, 5, 0, 1, 1)
        self.lblNumber.setBuddy(self.edtNumber)
        self.lblDate.setBuddy(self.edtDate)
        self.lblPayRefuseType.setBuddy(self.cmbRefuseType)

        self.retranslateUi(PayStatusDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PayStatusDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PayStatusDialog.reject)
        QtCore.QObject.connect(self.rbnRefused, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbRefuseType.setEnabled)
        QtCore.QObject.connect(self.rbnRefused, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblPayRefuseType.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(PayStatusDialog)
        PayStatusDialog.setTabOrder(self.edtDate, self.edtNumber)
        PayStatusDialog.setTabOrder(self.edtNumber, self.rbnAccepted)
        PayStatusDialog.setTabOrder(self.rbnAccepted, self.rbnRefused)
        PayStatusDialog.setTabOrder(self.rbnRefused, self.cmbRefuseType)
        PayStatusDialog.setTabOrder(self.cmbRefuseType, self.buttonBox)

    def retranslateUi(self, PayStatusDialog):
        PayStatusDialog.setWindowTitle(QtGui.QApplication.translate("PayStatusDialog", "Подтверждение оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.rbnAccepted.setText(QtGui.QApplication.translate("PayStatusDialog", "Оплачено", None, QtGui.QApplication.UnicodeUTF8))
        self.lblNumber.setText(QtGui.QApplication.translate("PayStatusDialog", "Документ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDate.setText(QtGui.QApplication.translate("PayStatusDialog", "Дата", None, QtGui.QApplication.UnicodeUTF8))
        self.rbnRefused.setText(QtGui.QApplication.translate("PayStatusDialog", "Отказано", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPayRefuseType.setText(QtGui.QApplication.translate("PayStatusDialog", "Причина отказа", None, QtGui.QApplication.UnicodeUTF8))
        self.lblNote.setText(QtGui.QApplication.translate("PayStatusDialog", "Примечание", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PayStatusDialog = QtGui.QDialog()
    ui = Ui_PayStatusDialog()
    ui.setupUi(PayStatusDialog)
    PayStatusDialog.show()
    sys.exit(app.exec_())

