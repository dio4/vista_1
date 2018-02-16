# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'OrgStructureEditor_AddAddressesDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_AddAddressesDialog(object):
    def setupUi(self, AddAddressesDialog):
        AddAddressesDialog.setObjectName(_fromUtf8("AddAddressesDialog"))
        AddAddressesDialog.resize(428, 215)
        self.gridLayout = QtGui.QGridLayout(AddAddressesDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblNumbers = QtGui.QLabel(AddAddressesDialog)
        self.lblNumbers.setObjectName(_fromUtf8("lblNumbers"))
        self.gridLayout.addWidget(self.lblNumbers, 9, 0, 1, 1)
        self.lblCity = QtGui.QLabel(AddAddressesDialog)
        self.lblCity.setObjectName(_fromUtf8("lblCity"))
        self.gridLayout.addWidget(self.lblCity, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 35, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 13, 0, 1, 1)
        self.lblHouseTo = QtGui.QLabel(AddAddressesDialog)
        self.lblHouseTo.setObjectName(_fromUtf8("lblHouseTo"))
        self.gridLayout.addWidget(self.lblHouseTo, 2, 3, 1, 1)
        self.lblHouse = QtGui.QLabel(AddAddressesDialog)
        self.lblHouse.setObjectName(_fromUtf8("lblHouse"))
        self.gridLayout.addWidget(self.lblHouse, 2, 0, 1, 1)
        self.lblHouseFrom = QtGui.QLabel(AddAddressesDialog)
        self.lblHouseFrom.setObjectName(_fromUtf8("lblHouseFrom"))
        self.gridLayout.addWidget(self.lblHouseFrom, 2, 1, 1, 1)
        self.edtHouseTo = QtGui.QSpinBox(AddAddressesDialog)
        self.edtHouseTo.setMaximum(999)
        self.edtHouseTo.setProperty("value", 1)
        self.edtHouseTo.setObjectName(_fromUtf8("edtHouseTo"))
        self.gridLayout.addWidget(self.edtHouseTo, 2, 4, 1, 1)
        self.lblStreet = QtGui.QLabel(AddAddressesDialog)
        self.lblStreet.setObjectName(_fromUtf8("lblStreet"))
        self.gridLayout.addWidget(self.lblStreet, 1, 0, 1, 1)
        self.edtHouseFrom = QtGui.QSpinBox(AddAddressesDialog)
        self.edtHouseFrom.setMaximum(999)
        self.edtHouseFrom.setProperty("value", 1)
        self.edtHouseFrom.setObjectName(_fromUtf8("edtHouseFrom"))
        self.gridLayout.addWidget(self.edtHouseFrom, 2, 2, 1, 1)
        self.lblFlat = QtGui.QLabel(AddAddressesDialog)
        self.lblFlat.setObjectName(_fromUtf8("lblFlat"))
        self.gridLayout.addWidget(self.lblFlat, 4, 0, 1, 1)
        self.lblFlatFrom = QtGui.QLabel(AddAddressesDialog)
        self.lblFlatFrom.setObjectName(_fromUtf8("lblFlatFrom"))
        self.gridLayout.addWidget(self.lblFlatFrom, 4, 1, 1, 1)
        self.edtFlatFrom = QtGui.QSpinBox(AddAddressesDialog)
        self.edtFlatFrom.setMaximum(999)
        self.edtFlatFrom.setObjectName(_fromUtf8("edtFlatFrom"))
        self.gridLayout.addWidget(self.edtFlatFrom, 4, 2, 1, 1)
        self.lblFlatTo = QtGui.QLabel(AddAddressesDialog)
        self.lblFlatTo.setObjectName(_fromUtf8("lblFlatTo"))
        self.gridLayout.addWidget(self.lblFlatTo, 4, 3, 1, 1)
        self.edtFlatTo = QtGui.QSpinBox(AddAddressesDialog)
        self.edtFlatTo.setMaximum(999)
        self.edtFlatTo.setObjectName(_fromUtf8("edtFlatTo"))
        self.gridLayout.addWidget(self.edtFlatTo, 4, 4, 1, 1)
        self.cmbCity = CKLADRComboBox(AddAddressesDialog)
        self.cmbCity.setObjectName(_fromUtf8("cmbCity"))
        self.gridLayout.addWidget(self.cmbCity, 0, 1, 1, 4)
        self.cmbStreet = CStreetComboBox(AddAddressesDialog)
        self.cmbStreet.setObjectName(_fromUtf8("cmbStreet"))
        self.gridLayout.addWidget(self.cmbStreet, 1, 1, 1, 4)
        self.cmbNumbers = QtGui.QComboBox(AddAddressesDialog)
        self.cmbNumbers.setObjectName(_fromUtf8("cmbNumbers"))
        self.cmbNumbers.addItem(_fromUtf8(""))
        self.cmbNumbers.addItem(_fromUtf8(""))
        self.cmbNumbers.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbNumbers, 9, 1, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(AddAddressesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 14, 0, 1, 5)

        self.retranslateUi(AddAddressesDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AddAddressesDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AddAddressesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddAddressesDialog)

    def retranslateUi(self, AddAddressesDialog):
        AddAddressesDialog.setWindowTitle(_translate("AddAddressesDialog", "Добавление адресов", None))
        self.lblNumbers.setText(_translate("AddAddressesDialog", "Четность номеров домов", None))
        self.lblCity.setText(_translate("AddAddressesDialog", "Населенный пункт", None))
        self.lblHouseTo.setText(_translate("AddAddressesDialog", "по", None))
        self.lblHouse.setText(_translate("AddAddressesDialog", "Номера домов:", None))
        self.lblHouseFrom.setText(_translate("AddAddressesDialog", "с", None))
        self.lblStreet.setText(_translate("AddAddressesDialog", "Улица", None))
        self.lblFlat.setText(_translate("AddAddressesDialog", "Номера квартир:", None))
        self.lblFlatFrom.setText(_translate("AddAddressesDialog", "с", None))
        self.lblFlatTo.setText(_translate("AddAddressesDialog", "по", None))
        self.cmbNumbers.setItemText(0, _translate("AddAddressesDialog", "все", None))
        self.cmbNumbers.setItemText(1, _translate("AddAddressesDialog", "только нечетные", None))
        self.cmbNumbers.setItemText(2, _translate("AddAddressesDialog", "только четные", None))

from KLADR.kladrComboxes import CKLADRComboBox, CStreetComboBox
