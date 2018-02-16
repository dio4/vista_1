# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Stock\Inventory.ui'
#
# Created: Fri Jun 15 12:17:10 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_InventoryDialog(object):
    def setupUi(self, InventoryDialog):
        InventoryDialog.setObjectName(_fromUtf8("InventoryDialog"))
        InventoryDialog.resize(542, 452)
        self.gridLayout = QtGui.QGridLayout(InventoryDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDate = QtGui.QLabel(InventoryDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblDate.sizePolicy().hasHeightForWidth())
        self.lblDate.setSizePolicy(sizePolicy)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.edtDate = CDateEdit(InventoryDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDate.sizePolicy().hasHeightForWidth())
        self.edtDate.setSizePolicy(sizePolicy)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 0, 1, 1, 1)
        self.edtTime = QtGui.QTimeEdit(InventoryDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtTime.sizePolicy().hasHeightForWidth())
        self.edtTime.setSizePolicy(sizePolicy)
        self.edtTime.setObjectName(_fromUtf8("edtTime"))
        self.gridLayout.addWidget(self.edtTime, 0, 2, 1, 1)
        self.lblSupplier = QtGui.QLabel(InventoryDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblSupplier.sizePolicy().hasHeightForWidth())
        self.lblSupplier.setSizePolicy(sizePolicy)
        self.lblSupplier.setObjectName(_fromUtf8("lblSupplier"))
        self.gridLayout.addWidget(self.lblSupplier, 2, 0, 1, 1)
        self.cmbSupplier = CStorageComboBox(InventoryDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSupplier.sizePolicy().hasHeightForWidth())
        self.cmbSupplier.setSizePolicy(sizePolicy)
        self.cmbSupplier.setObjectName(_fromUtf8("cmbSupplier"))
        self.gridLayout.addWidget(self.cmbSupplier, 2, 1, 1, 3)
        self.lblNote = QtGui.QLabel(InventoryDialog)
        self.lblNote.setObjectName(_fromUtf8("lblNote"))
        self.gridLayout.addWidget(self.lblNote, 4, 0, 1, 1)
        self.edtNote = QtGui.QLineEdit(InventoryDialog)
        self.edtNote.setObjectName(_fromUtf8("edtNote"))
        self.gridLayout.addWidget(self.edtNote, 4, 1, 1, 3)
        self.tblItems = CInDocTableView(InventoryDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblItems.sizePolicy().hasHeightForWidth())
        self.tblItems.setSizePolicy(sizePolicy)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 5, 0, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(InventoryDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 4)
        self.cmbSupplierPerson = CPersonComboBoxEx(InventoryDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSupplierPerson.sizePolicy().hasHeightForWidth())
        self.cmbSupplierPerson.setSizePolicy(sizePolicy)
        self.cmbSupplierPerson.setObjectName(_fromUtf8("cmbSupplierPerson"))
        self.gridLayout.addWidget(self.cmbSupplierPerson, 3, 1, 1, 3)
        self.lblSupplierPerson = QtGui.QLabel(InventoryDialog)
        self.lblSupplierPerson.setObjectName(_fromUtf8("lblSupplierPerson"))
        self.gridLayout.addWidget(self.lblSupplierPerson, 3, 0, 1, 1)
        self.lblDate.setBuddy(self.edtDate)
        self.lblSupplier.setBuddy(self.cmbSupplier)
        self.lblNote.setBuddy(self.edtNote)
        self.lblSupplierPerson.setBuddy(self.cmbSupplierPerson)

        self.retranslateUi(InventoryDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), InventoryDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), InventoryDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(InventoryDialog)
        InventoryDialog.setTabOrder(self.edtDate, self.edtTime)
        InventoryDialog.setTabOrder(self.edtTime, self.cmbSupplier)
        InventoryDialog.setTabOrder(self.cmbSupplier, self.cmbSupplierPerson)
        InventoryDialog.setTabOrder(self.cmbSupplierPerson, self.edtNote)
        InventoryDialog.setTabOrder(self.edtNote, self.tblItems)
        InventoryDialog.setTabOrder(self.tblItems, self.buttonBox)

    def retranslateUi(self, InventoryDialog):
        InventoryDialog.setWindowTitle(QtGui.QApplication.translate("InventoryDialog", "Акт инвентаризации ЛСиИМН", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDate.setText(QtGui.QApplication.translate("InventoryDialog", "Дата", None, QtGui.QApplication.UnicodeUTF8))
        self.edtTime.setDisplayFormat(QtGui.QApplication.translate("InventoryDialog", "HH:mm", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSupplier.setText(QtGui.QApplication.translate("InventoryDialog", "Подразденение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblNote.setText(QtGui.QApplication.translate("InventoryDialog", "Примечания", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSupplierPerson.setText(QtGui.QApplication.translate("InventoryDialog", "Ответственный", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import CStorageComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    InventoryDialog = QtGui.QDialog()
    ui = Ui_InventoryDialog()
    ui.setupUi(InventoryDialog)
    InventoryDialog.show()
    sys.exit(app.exec_())

