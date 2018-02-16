# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/craz/s11_local/RefBooks/RBPatientModelEditor.ui'
#
# Created: Mon Mar  4 15:39:24 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ItemEditorDialog(object):
    def setupUi(self, ItemEditorDialog):
        ItemEditorDialog.setObjectName(_fromUtf8("ItemEditorDialog"))
        ItemEditorDialog.resize(667, 368)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        self.lblCheckingSerial = QtGui.QLabel(ItemEditorDialog)
        self.lblCheckingSerial.setObjectName(_fromUtf8("lblCheckingSerial"))
        self.gridLayout.addWidget(self.lblCheckingSerial, 2, 0, 1, 1)
        self.lblCheckingNumber = QtGui.QLabel(ItemEditorDialog)
        self.lblCheckingNumber.setObjectName(_fromUtf8("lblCheckingNumber"))
        self.gridLayout.addWidget(self.lblCheckingNumber, 3, 0, 1, 1)
        self.cmbQuotaType = CQuotaComboBox(ItemEditorDialog)
        self.cmbQuotaType.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.cmbQuotaType.setObjectName(_fromUtf8("cmbQuotaType"))
        self.gridLayout.addWidget(self.cmbQuotaType, 3, 1, 1, 1)
        self.edtMKB = QtGui.QLineEdit(ItemEditorDialog)
        self.edtMKB.setObjectName(_fromUtf8("edtMKB"))
        self.gridLayout.addWidget(self.edtMKB, 2, 1, 1, 1)
        self.tblItems = CInDocTableView(ItemEditorDialog)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 5, 0, 1, 2)
        self.chkIsObsolete = QtGui.QCheckBox(ItemEditorDialog)
        self.chkIsObsolete.setObjectName(_fromUtf8("chkIsObsolete"))
        self.gridLayout.addWidget(self.chkIsObsolete, 4, 1, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblCheckingSerial.setBuddy(self.edtMKB)
        self.lblCheckingNumber.setBuddy(self.cmbQuotaType)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.edtMKB)
        ItemEditorDialog.setTabOrder(self.edtMKB, self.cmbQuotaType)
        ItemEditorDialog.setTabOrder(self.cmbQuotaType, self.tblItems)
        ItemEditorDialog.setTabOrder(self.tblItems, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(QtGui.QApplication.translate("ItemEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCheckingSerial.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Диагноз", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCheckingNumber.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Тип квоты", None, QtGui.QApplication.UnicodeUTF8))
        self.chkIsObsolete.setText(QtGui.QApplication.translate("ItemEditorDialog", "Устаревший", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView
from Quoting.QuotaComboBox import CQuotaComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemEditorDialog = QtGui.QDialog()
    ui = Ui_ItemEditorDialog()
    ui.setupUi(ItemEditorDialog)
    ItemEditorDialog.show()
    sys.exit(app.exec_())

