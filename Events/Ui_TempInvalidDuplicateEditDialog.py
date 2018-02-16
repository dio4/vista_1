# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TempInvalidDuplicateEditDialog.ui'
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

class Ui_TempInvalidDuplicateEditDialog(object):
    def setupUi(self, TempInvalidDuplicateEditDialog):
        TempInvalidDuplicateEditDialog.setObjectName(_fromUtf8("TempInvalidDuplicateEditDialog"))
        TempInvalidDuplicateEditDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        TempInvalidDuplicateEditDialog.resize(324, 392)
        self.gridLayout = QtGui.QGridLayout(TempInvalidDuplicateEditDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblNote = QtGui.QLabel(TempInvalidDuplicateEditDialog)
        self.lblNote.setObjectName(_fromUtf8("lblNote"))
        self.gridLayout.addWidget(self.lblNote, 8, 0, 1, 1)
        self.lblSerial = QtGui.QLabel(TempInvalidDuplicateEditDialog)
        self.lblSerial.setObjectName(_fromUtf8("lblSerial"))
        self.gridLayout.addWidget(self.lblSerial, 0, 0, 1, 1)
        self.edtNote = QtGui.QPlainTextEdit(TempInvalidDuplicateEditDialog)
        self.edtNote.setObjectName(_fromUtf8("edtNote"))
        self.gridLayout.addWidget(self.edtNote, 8, 1, 2, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 0, 1, 1)
        self.edtNumber = QtGui.QLineEdit(TempInvalidDuplicateEditDialog)
        self.edtNumber.setObjectName(_fromUtf8("edtNumber"))
        self.gridLayout.addWidget(self.edtNumber, 1, 1, 1, 2)
        self.cmbPerson = CPersonComboBoxEx(TempInvalidDuplicateEditDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 3, 1, 1, 2)
        self.edtSerial = CBlankComboBox(TempInvalidDuplicateEditDialog)
        self.edtSerial.setEditable(True)
        self.edtSerial.setObjectName(_fromUtf8("edtSerial"))
        self.gridLayout.addWidget(self.edtSerial, 0, 1, 1, 2)
        self.lblNumber = QtGui.QLabel(TempInvalidDuplicateEditDialog)
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.gridLayout.addWidget(self.lblNumber, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 11, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(TempInvalidDuplicateEditDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 12, 0, 1, 3)
        self.lblDate = QtGui.QLabel(TempInvalidDuplicateEditDialog)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 2, 0, 1, 1)
        self.lblPerson = QtGui.QLabel(TempInvalidDuplicateEditDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 3, 0, 1, 1)
        self.lblDestination = QtGui.QLabel(TempInvalidDuplicateEditDialog)
        self.lblDestination.setObjectName(_fromUtf8("lblDestination"))
        self.gridLayout.addWidget(self.lblDestination, 5, 0, 1, 1)
        self.edtDestination = QtGui.QLineEdit(TempInvalidDuplicateEditDialog)
        self.edtDestination.setObjectName(_fromUtf8("edtDestination"))
        self.gridLayout.addWidget(self.edtDestination, 5, 1, 1, 2)
        self.cmbReason = CRBComboBox(TempInvalidDuplicateEditDialog)
        self.cmbReason.setObjectName(_fromUtf8("cmbReason"))
        self.gridLayout.addWidget(self.cmbReason, 6, 1, 1, 2)
        self.lblReason = QtGui.QLabel(TempInvalidDuplicateEditDialog)
        self.lblReason.setObjectName(_fromUtf8("lblReason"))
        self.gridLayout.addWidget(self.lblReason, 6, 0, 1, 1)
        self.chkInsuranceOfficeMark = QtGui.QCheckBox(TempInvalidDuplicateEditDialog)
        self.chkInsuranceOfficeMark.setObjectName(_fromUtf8("chkInsuranceOfficeMark"))
        self.gridLayout.addWidget(self.chkInsuranceOfficeMark, 10, 1, 1, 2)
        self.edtPlaceWork = QtGui.QLineEdit(TempInvalidDuplicateEditDialog)
        self.edtPlaceWork.setEnabled(False)
        self.edtPlaceWork.setObjectName(_fromUtf8("edtPlaceWork"))
        self.gridLayout.addWidget(self.edtPlaceWork, 7, 1, 1, 2)
        self.lblPlaceWork = QtGui.QLabel(TempInvalidDuplicateEditDialog)
        self.lblPlaceWork.setObjectName(_fromUtf8("lblPlaceWork"))
        self.gridLayout.addWidget(self.lblPlaceWork, 7, 0, 1, 1)
        self.edtDate = CDateEdit(TempInvalidDuplicateEditDialog)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 2, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(71, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 2, 2, 1, 1)
        self.label = QtGui.QLabel(TempInvalidDuplicateEditDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        self.cmbExpert = CPersonComboBoxEx(TempInvalidDuplicateEditDialog)
        self.cmbExpert.setObjectName(_fromUtf8("cmbExpert"))
        self.gridLayout.addWidget(self.cmbExpert, 4, 1, 1, 2)
        self.lblNote.setBuddy(self.cmbPerson)
        self.lblNumber.setBuddy(self.edtNumber)
        self.lblDate.setBuddy(self.edtDate)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblDestination.setBuddy(self.cmbPerson)
        self.lblReason.setBuddy(self.cmbPerson)

        self.retranslateUi(TempInvalidDuplicateEditDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TempInvalidDuplicateEditDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TempInvalidDuplicateEditDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TempInvalidDuplicateEditDialog)
        TempInvalidDuplicateEditDialog.setTabOrder(self.edtNumber, self.edtDate)
        TempInvalidDuplicateEditDialog.setTabOrder(self.edtDate, self.cmbPerson)
        TempInvalidDuplicateEditDialog.setTabOrder(self.cmbPerson, self.edtDestination)
        TempInvalidDuplicateEditDialog.setTabOrder(self.edtDestination, self.cmbReason)
        TempInvalidDuplicateEditDialog.setTabOrder(self.cmbReason, self.edtPlaceWork)
        TempInvalidDuplicateEditDialog.setTabOrder(self.edtPlaceWork, self.edtNote)
        TempInvalidDuplicateEditDialog.setTabOrder(self.edtNote, self.chkInsuranceOfficeMark)
        TempInvalidDuplicateEditDialog.setTabOrder(self.chkInsuranceOfficeMark, self.buttonBox)

    def retranslateUi(self, TempInvalidDuplicateEditDialog):
        TempInvalidDuplicateEditDialog.setWindowTitle(_translate("TempInvalidDuplicateEditDialog", "Дубликат документа временной нетрудоспособности", None))
        self.lblNote.setText(_translate("TempInvalidDuplicateEditDialog", "П&римечание", None))
        self.lblSerial.setText(_translate("TempInvalidDuplicateEditDialog", "Серия", None))
        self.lblNumber.setText(_translate("TempInvalidDuplicateEditDialog", "&Номер", None))
        self.lblDate.setText(_translate("TempInvalidDuplicateEditDialog", "&Дата", None))
        self.lblPerson.setText(_translate("TempInvalidDuplicateEditDialog", "&Выдал", None))
        self.lblDestination.setText(_translate("TempInvalidDuplicateEditDialog", "&Для представления в", None))
        self.lblReason.setText(_translate("TempInvalidDuplicateEditDialog", "&Причина выдачи", None))
        self.chkInsuranceOfficeMark.setText(_translate("TempInvalidDuplicateEditDialog", "Отметка страхового стола", None))
        self.lblPlaceWork.setText(_translate("TempInvalidDuplicateEditDialog", "Место работы", None))
        self.label.setText(_translate("TempInvalidDuplicateEditDialog", "Председатель КЭР", None))

from Blank.BlankComboBox import CBlankComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
