# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportAgeClassificationSetup.ui'
#
# Created: Mon Feb 09 20:12:10 2015
#      by: PyQt4 UI code generator 4.11
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

class Ui_ReportAgeClassificationSetupDialog(object):
    def setupUi(self, ReportAgeClassificationSetupDialog):
        ReportAgeClassificationSetupDialog.setObjectName(_fromUtf8("ReportAgeClassificationSetupDialog"))
        ReportAgeClassificationSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportAgeClassificationSetupDialog.resize(352, 217)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportAgeClassificationSetupDialog.sizePolicy().hasHeightForWidth())
        ReportAgeClassificationSetupDialog.setSizePolicy(sizePolicy)
        ReportAgeClassificationSetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportAgeClassificationSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 1, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportAgeClassificationSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 1)
        self.cmbPrimary = QtGui.QComboBox(ReportAgeClassificationSetupDialog)
        self.cmbPrimary.setObjectName(_fromUtf8("cmbPrimary"))
        self.cmbPrimary.addItem(_fromUtf8(""))
        self.cmbPrimary.setItemText(0, _fromUtf8(""))
        self.cmbPrimary.addItem(_fromUtf8(""))
        self.cmbPrimary.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbPrimary, 4, 1, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportAgeClassificationSetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 3, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportAgeClassificationSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 1, 0, 1, 1)
        self.lblPrimary = QtGui.QLabel(ReportAgeClassificationSetupDialog)
        self.lblPrimary.setObjectName(_fromUtf8("lblPrimary"))
        self.gridLayout.addWidget(self.lblPrimary, 4, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportAgeClassificationSetupDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAgeClassificationSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)
        self.edtEndDate = CDateEdit(ReportAgeClassificationSetupDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 1, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportAgeClassificationSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 3, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblMKB = QtGui.QLabel(ReportAgeClassificationSetupDialog)
        self.lblMKB.setObjectName(_fromUtf8("lblMKB"))
        self.horizontalLayout.addWidget(self.lblMKB)
        self.cmbMKBFilter = QtGui.QComboBox(ReportAgeClassificationSetupDialog)
        self.cmbMKBFilter.setObjectName(_fromUtf8("cmbMKBFilter"))
        self.cmbMKBFilter.addItem(_fromUtf8(""))
        self.cmbMKBFilter.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.cmbMKBFilter)
        self.edtMKBFrom = CICDCodeEdit(ReportAgeClassificationSetupDialog)
        self.edtMKBFrom.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMKBFrom.sizePolicy().hasHeightForWidth())
        self.edtMKBFrom.setSizePolicy(sizePolicy)
        self.edtMKBFrom.setMaximumSize(QtCore.QSize(40, 16777215))
        self.edtMKBFrom.setMaxLength(6)
        self.edtMKBFrom.setObjectName(_fromUtf8("edtMKBFrom"))
        self.horizontalLayout.addWidget(self.edtMKBFrom)
        self.edtMKBTo = CICDCodeEdit(ReportAgeClassificationSetupDialog)
        self.edtMKBTo.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMKBTo.sizePolicy().hasHeightForWidth())
        self.edtMKBTo.setSizePolicy(sizePolicy)
        self.edtMKBTo.setMaximumSize(QtCore.QSize(40, 16777215))
        self.edtMKBTo.setMaxLength(6)
        self.edtMKBTo.setObjectName(_fromUtf8("edtMKBTo"))
        self.horizontalLayout.addWidget(self.edtMKBTo)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.lblEventType = QtGui.QLabel(ReportAgeClassificationSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 5, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportAgeClassificationSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 5, 1, 1, 1)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblMKB.setBuddy(self.cmbMKBFilter)
        self.lblEventType.setBuddy(self.cmbEventType)

        self.retranslateUi(ReportAgeClassificationSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAgeClassificationSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAgeClassificationSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAgeClassificationSetupDialog)

    def retranslateUi(self, ReportAgeClassificationSetupDialog):
        ReportAgeClassificationSetupDialog.setWindowTitle(_translate("ReportAgeClassificationSetupDialog", "параметры отчёта", None))
        self.lblEndDate.setText(_translate("ReportAgeClassificationSetupDialog", "Дата окончания периода", None))
        self.cmbPrimary.setItemText(1, _translate("ReportAgeClassificationSetupDialog", "Первичный", None))
        self.cmbPrimary.setItemText(2, _translate("ReportAgeClassificationSetupDialog", "Вторичный", None))
        self.lblBegDate.setText(_translate("ReportAgeClassificationSetupDialog", "Дата начала периода", None))
        self.lblPrimary.setText(_translate("ReportAgeClassificationSetupDialog", "Первичность", None))
        self.lblPerson.setText(_translate("ReportAgeClassificationSetupDialog", "&Врач", None))
        self.lblMKB.setText(_translate("ReportAgeClassificationSetupDialog", "Коды диагнозов по &МКБ", None))
        self.cmbMKBFilter.setItemText(0, _translate("ReportAgeClassificationSetupDialog", "Игнор.", None))
        self.cmbMKBFilter.setItemText(1, _translate("ReportAgeClassificationSetupDialog", "Интервал", None))
        self.edtMKBFrom.setInputMask(_translate("ReportAgeClassificationSetupDialog", "a00.00; ", None))
        self.edtMKBFrom.setText(_translate("ReportAgeClassificationSetupDialog", "A.", None))
        self.edtMKBTo.setInputMask(_translate("ReportAgeClassificationSetupDialog", "a00.00; ", None))
        self.edtMKBTo.setText(_translate("ReportAgeClassificationSetupDialog", "Z99.9", None))
        self.lblEventType.setText(_translate("ReportAgeClassificationSetupDialog", "&Тип обращения", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.ICDCodeEdit import CICDCodeEdit
from library.DateEdit import CDateEdit
