# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Stock\FinTransfer.ui'
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

class Ui_FinTransferDialog(object):
    def setupUi(self, FinTransferDialog):
        FinTransferDialog.setObjectName(_fromUtf8("FinTransferDialog"))
        FinTransferDialog.resize(542, 452)
        self.gridLayout = QtGui.QGridLayout(FinTransferDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDate = QtGui.QLabel(FinTransferDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblDate.sizePolicy().hasHeightForWidth())
        self.lblDate.setSizePolicy(sizePolicy)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.edtDate = CDateEdit(FinTransferDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDate.sizePolicy().hasHeightForWidth())
        self.edtDate.setSizePolicy(sizePolicy)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 0, 1, 1, 1)
        self.edtTime = QtGui.QTimeEdit(FinTransferDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtTime.sizePolicy().hasHeightForWidth())
        self.edtTime.setSizePolicy(sizePolicy)
        self.edtTime.setObjectName(_fromUtf8("edtTime"))
        self.gridLayout.addWidget(self.edtTime, 0, 2, 1, 1)
        self.lblSupplier = QtGui.QLabel(FinTransferDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblSupplier.sizePolicy().hasHeightForWidth())
        self.lblSupplier.setSizePolicy(sizePolicy)
        self.lblSupplier.setObjectName(_fromUtf8("lblSupplier"))
        self.gridLayout.addWidget(self.lblSupplier, 1, 0, 1, 1)
        self.cmbSupplier = CStorageComboBox(FinTransferDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSupplier.sizePolicy().hasHeightForWidth())
        self.cmbSupplier.setSizePolicy(sizePolicy)
        self.cmbSupplier.setObjectName(_fromUtf8("cmbSupplier"))
        self.gridLayout.addWidget(self.cmbSupplier, 1, 1, 1, 3)
        self.lblNote = QtGui.QLabel(FinTransferDialog)
        self.lblNote.setObjectName(_fromUtf8("lblNote"))
        self.gridLayout.addWidget(self.lblNote, 3, 0, 1, 1)
        self.edtNote = QtGui.QLineEdit(FinTransferDialog)
        self.edtNote.setObjectName(_fromUtf8("edtNote"))
        self.gridLayout.addWidget(self.edtNote, 3, 1, 1, 3)
        self.tblItems = CInDocTableView(FinTransferDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblItems.sizePolicy().hasHeightForWidth())
        self.tblItems.setSizePolicy(sizePolicy)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 4, 0, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(FinTransferDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 4)
        self.cmbSupplierPerson = CPersonComboBoxEx(FinTransferDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSupplierPerson.sizePolicy().hasHeightForWidth())
        self.cmbSupplierPerson.setSizePolicy(sizePolicy)
        self.cmbSupplierPerson.setObjectName(_fromUtf8("cmbSupplierPerson"))
        self.gridLayout.addWidget(self.cmbSupplierPerson, 2, 1, 1, 3)
        self.lblSupplierPerson = QtGui.QLabel(FinTransferDialog)
        self.lblSupplierPerson.setObjectName(_fromUtf8("lblSupplierPerson"))
        self.gridLayout.addWidget(self.lblSupplierPerson, 2, 0, 1, 1)
        self.lblDate.setBuddy(self.edtDate)
        self.lblSupplier.setBuddy(self.cmbSupplier)
        self.lblNote.setBuddy(self.edtNote)
        self.lblSupplierPerson.setBuddy(self.cmbSupplierPerson)

        self.retranslateUi(FinTransferDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FinTransferDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FinTransferDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FinTransferDialog)
        FinTransferDialog.setTabOrder(self.edtDate, self.edtTime)
        FinTransferDialog.setTabOrder(self.edtTime, self.cmbSupplier)
        FinTransferDialog.setTabOrder(self.cmbSupplier, self.cmbSupplierPerson)
        FinTransferDialog.setTabOrder(self.cmbSupplierPerson, self.edtNote)
        FinTransferDialog.setTabOrder(self.edtNote, self.tblItems)
        FinTransferDialog.setTabOrder(self.tblItems, self.buttonBox)

    def retranslateUi(self, FinTransferDialog):
        FinTransferDialog.setWindowTitle(QtGui.QApplication.translate("FinTransferDialog", "Акт изменения типа финансирования ЛСиИМН", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDate.setText(QtGui.QApplication.translate("FinTransferDialog", "Дата", None, QtGui.QApplication.UnicodeUTF8))
        self.edtTime.setDisplayFormat(QtGui.QApplication.translate("FinTransferDialog", "HH:mm", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSupplier.setText(QtGui.QApplication.translate("FinTransferDialog", "Подразденение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblNote.setText(QtGui.QApplication.translate("FinTransferDialog", "Примечания", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSupplierPerson.setText(QtGui.QApplication.translate("FinTransferDialog", "Ответственный", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import CStorageComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    FinTransferDialog = QtGui.QDialog()
    ui = Ui_FinTransferDialog()
    ui.setupUi(FinTransferDialog)
    FinTransferDialog.show()
    sys.exit(app.exec_())

