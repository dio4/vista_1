# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Accounting\CashDialog.ui'
#
# Created: Fri Jun 15 12:17:04 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_CashDialog(object):
    def setupUi(self, CashDialog):
        CashDialog.setObjectName(_fromUtf8("CashDialog"))
        CashDialog.resize(231, 112)
        CashDialog.setSizeGripEnabled(True)
        CashDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(CashDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDate = QtGui.QLabel(CashDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblDate.sizePolicy().hasHeightForWidth())
        self.lblDate.setSizePolicy(sizePolicy)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.edtDate = CDateEdit(CashDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDate.sizePolicy().hasHeightForWidth())
        self.edtDate.setSizePolicy(sizePolicy)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 0, 1, 1, 1)
        self.lblCashOperation = QtGui.QLabel(CashDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblCashOperation.sizePolicy().hasHeightForWidth())
        self.lblCashOperation.setSizePolicy(sizePolicy)
        self.lblCashOperation.setObjectName(_fromUtf8("lblCashOperation"))
        self.gridLayout.addWidget(self.lblCashOperation, 1, 0, 1, 1)
        self.cmbCashOperation = CRBComboBox(CashDialog)
        self.cmbCashOperation.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbCashOperation.sizePolicy().hasHeightForWidth())
        self.cmbCashOperation.setSizePolicy(sizePolicy)
        self.cmbCashOperation.setObjectName(_fromUtf8("cmbCashOperation"))
        self.gridLayout.addWidget(self.cmbCashOperation, 1, 1, 1, 1)
        self.lblSum = QtGui.QLabel(CashDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblSum.sizePolicy().hasHeightForWidth())
        self.lblSum.setSizePolicy(sizePolicy)
        self.lblSum.setObjectName(_fromUtf8("lblSum"))
        self.gridLayout.addWidget(self.lblSum, 2, 0, 1, 1)
        self.edtSum = QtGui.QDoubleSpinBox(CashDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtSum.sizePolicy().hasHeightForWidth())
        self.edtSum.setSizePolicy(sizePolicy)
        self.edtSum.setMaximum(9999999.99)
        self.edtSum.setObjectName(_fromUtf8("edtSum"))
        self.gridLayout.addWidget(self.edtSum, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(CashDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.lblDate.setBuddy(self.edtDate)
        self.lblCashOperation.setBuddy(self.cmbCashOperation)
        self.lblSum.setBuddy(self.edtSum)

        self.retranslateUi(CashDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CashDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CashDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CashDialog)
        CashDialog.setTabOrder(self.edtDate, self.cmbCashOperation)
        CashDialog.setTabOrder(self.cmbCashOperation, self.edtSum)
        CashDialog.setTabOrder(self.edtSum, self.buttonBox)

    def retranslateUi(self, CashDialog):
        CashDialog.setWindowTitle(QtGui.QApplication.translate("CashDialog", "Приём оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDate.setText(QtGui.QApplication.translate("CashDialog", "&Дата", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCashOperation.setText(QtGui.QApplication.translate("CashDialog", "&Кассовая операция", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSum.setText(QtGui.QApplication.translate("CashDialog", "&Сумма", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    CashDialog = QtGui.QDialog()
    ui = Ui_CashDialog()
    ui.setupUi(CashDialog)
    CashDialog.show()
    sys.exit(app.exec_())

