# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Stock\StockRequisitionEditDialog.ui'
#
# Created: Fri Jun 15 12:17:07 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_StockRequisitionDialog(object):
    def setupUi(self, StockRequisitionDialog):
        StockRequisitionDialog.setObjectName(_fromUtf8("StockRequisitionDialog"))
        StockRequisitionDialog.resize(542, 452)
        self.gridLayout = QtGui.QGridLayout(StockRequisitionDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDate = QtGui.QLabel(StockRequisitionDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblDate.sizePolicy().hasHeightForWidth())
        self.lblDate.setSizePolicy(sizePolicy)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.edtDate = CDateEdit(StockRequisitionDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDate.sizePolicy().hasHeightForWidth())
        self.edtDate.setSizePolicy(sizePolicy)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 0, 1, 1, 1)
        self.lblDeadline = QtGui.QLabel(StockRequisitionDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblDeadline.sizePolicy().hasHeightForWidth())
        self.lblDeadline.setSizePolicy(sizePolicy)
        self.lblDeadline.setObjectName(_fromUtf8("lblDeadline"))
        self.gridLayout.addWidget(self.lblDeadline, 0, 2, 1, 1)
        self.edtDeadlineDate = CDateEdit(StockRequisitionDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDeadlineDate.sizePolicy().hasHeightForWidth())
        self.edtDeadlineDate.setSizePolicy(sizePolicy)
        self.edtDeadlineDate.setObjectName(_fromUtf8("edtDeadlineDate"))
        self.gridLayout.addWidget(self.edtDeadlineDate, 0, 3, 1, 1)
        self.edtDeadlineTime = QtGui.QTimeEdit(StockRequisitionDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtDeadlineTime.sizePolicy().hasHeightForWidth())
        self.edtDeadlineTime.setSizePolicy(sizePolicy)
        self.edtDeadlineTime.setObjectName(_fromUtf8("edtDeadlineTime"))
        self.gridLayout.addWidget(self.edtDeadlineTime, 0, 4, 1, 1)
        self.chkRevoked = QtGui.QCheckBox(StockRequisitionDialog)
        self.chkRevoked.setObjectName(_fromUtf8("chkRevoked"))
        self.gridLayout.addWidget(self.chkRevoked, 0, 5, 1, 1)
        self.lblSupplier = QtGui.QLabel(StockRequisitionDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblSupplier.sizePolicy().hasHeightForWidth())
        self.lblSupplier.setSizePolicy(sizePolicy)
        self.lblSupplier.setObjectName(_fromUtf8("lblSupplier"))
        self.gridLayout.addWidget(self.lblSupplier, 1, 0, 1, 1)
        self.cmbSupplier = CStorageComboBox(StockRequisitionDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSupplier.sizePolicy().hasHeightForWidth())
        self.cmbSupplier.setSizePolicy(sizePolicy)
        self.cmbSupplier.setObjectName(_fromUtf8("cmbSupplier"))
        self.gridLayout.addWidget(self.cmbSupplier, 1, 1, 1, 5)
        self.lblRecipient = QtGui.QLabel(StockRequisitionDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblRecipient.sizePolicy().hasHeightForWidth())
        self.lblRecipient.setSizePolicy(sizePolicy)
        self.lblRecipient.setObjectName(_fromUtf8("lblRecipient"))
        self.gridLayout.addWidget(self.lblRecipient, 2, 0, 1, 1)
        self.cmbRecipient = CStorageComboBox(StockRequisitionDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbRecipient.sizePolicy().hasHeightForWidth())
        self.cmbRecipient.setSizePolicy(sizePolicy)
        self.cmbRecipient.setObjectName(_fromUtf8("cmbRecipient"))
        self.gridLayout.addWidget(self.cmbRecipient, 2, 1, 1, 5)
        self.lblNote = QtGui.QLabel(StockRequisitionDialog)
        self.lblNote.setObjectName(_fromUtf8("lblNote"))
        self.gridLayout.addWidget(self.lblNote, 3, 0, 1, 1)
        self.edtNote = QtGui.QLineEdit(StockRequisitionDialog)
        self.edtNote.setObjectName(_fromUtf8("edtNote"))
        self.gridLayout.addWidget(self.edtNote, 3, 1, 1, 5)
        self.tblItems = CInDocTableView(StockRequisitionDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblItems.sizePolicy().hasHeightForWidth())
        self.tblItems.setSizePolicy(sizePolicy)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 4, 0, 1, 6)
        self.buttonBox = QtGui.QDialogButtonBox(StockRequisitionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 6)
        self.lblDate.setBuddy(self.edtDate)
        self.lblDeadline.setBuddy(self.edtDeadlineDate)
        self.lblSupplier.setBuddy(self.cmbSupplier)
        self.lblRecipient.setBuddy(self.cmbRecipient)
        self.lblNote.setBuddy(self.edtNote)

        self.retranslateUi(StockRequisitionDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StockRequisitionDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StockRequisitionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StockRequisitionDialog)
        StockRequisitionDialog.setTabOrder(self.edtDate, self.edtDeadlineDate)
        StockRequisitionDialog.setTabOrder(self.edtDeadlineDate, self.edtDeadlineTime)
        StockRequisitionDialog.setTabOrder(self.edtDeadlineTime, self.chkRevoked)
        StockRequisitionDialog.setTabOrder(self.chkRevoked, self.cmbSupplier)
        StockRequisitionDialog.setTabOrder(self.cmbSupplier, self.cmbRecipient)
        StockRequisitionDialog.setTabOrder(self.cmbRecipient, self.edtNote)
        StockRequisitionDialog.setTabOrder(self.edtNote, self.tblItems)
        StockRequisitionDialog.setTabOrder(self.tblItems, self.buttonBox)

    def retranslateUi(self, StockRequisitionDialog):
        StockRequisitionDialog.setWindowTitle(QtGui.QApplication.translate("StockRequisitionDialog", "Требование на поставку ЛСиИМН", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDate.setText(QtGui.QApplication.translate("StockRequisitionDialog", "Дата", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDeadline.setText(QtGui.QApplication.translate("StockRequisitionDialog", "Срок исполнения", None, QtGui.QApplication.UnicodeUTF8))
        self.edtDeadlineTime.setDisplayFormat(QtGui.QApplication.translate("StockRequisitionDialog", "HH:mm", None, QtGui.QApplication.UnicodeUTF8))
        self.chkRevoked.setText(QtGui.QApplication.translate("StockRequisitionDialog", "Отменено", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSupplier.setText(QtGui.QApplication.translate("StockRequisitionDialog", "Поставщик", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRecipient.setText(QtGui.QApplication.translate("StockRequisitionDialog", "Заказчик", None, QtGui.QApplication.UnicodeUTF8))
        self.lblNote.setText(QtGui.QApplication.translate("StockRequisitionDialog", "Примечания", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import CStorageComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    StockRequisitionDialog = QtGui.QDialog()
    ui = Ui_StockRequisitionDialog()
    ui.setupUi(StockRequisitionDialog)
    StockRequisitionDialog.show()
    sys.exit(app.exec_())

