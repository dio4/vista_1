# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportAccountService.ui'
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

class Ui_ReportAccount(object):
    def setupUi(self, ReportAccount):
        ReportAccount.setObjectName(_fromUtf8("ReportAccount"))
        ReportAccount.resize(557, 457)
        self.gridLayout = QtGui.QGridLayout(ReportAccount)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(ReportAccount)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.edtBegDate = CDateEdit(self.groupBox)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout_2.addWidget(self.edtBegDate, 1, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 2, 0, 1, 1)
        self.edtEndDate = CDateEdit(self.groupBox)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout_2.addWidget(self.edtEndDate, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
        self.rbtnAccountDate = QtGui.QRadioButton(self.groupBox)
        self.rbtnAccountDate.setChecked(True)
        self.rbtnAccountDate.setObjectName(_fromUtf8("rbtnAccountDate"))
        self.gridLayout_2.addWidget(self.rbtnAccountDate, 0, 0, 1, 1)
        self.rbtnServiceDate = QtGui.QRadioButton(self.groupBox)
        self.rbtnServiceDate.setObjectName(_fromUtf8("rbtnServiceDate"))
        self.gridLayout_2.addWidget(self.rbtnServiceDate, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)
        self.groupBox_2 = QtGui.QGroupBox(ReportAccount)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.rbtnSMO = QtGui.QRadioButton(self.groupBox_2)
        self.rbtnSMO.setObjectName(_fromUtf8("rbtnSMO"))
        self.gridLayout_3.addWidget(self.rbtnSMO, 0, 1, 1, 1)
        self.rbtnClient = QtGui.QRadioButton(self.groupBox_2)
        self.rbtnClient.setChecked(True)
        self.rbtnClient.setObjectName(_fromUtf8("rbtnClient"))
        self.gridLayout_3.addWidget(self.rbtnClient, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 2)
        self.lblInsurer = QtGui.QLabel(ReportAccount)
        self.lblInsurer.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblInsurer.setObjectName(_fromUtf8("lblInsurer"))
        self.gridLayout.addWidget(self.lblInsurer, 2, 0, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout.addLayout(self.verticalLayout, 2, 1, 1, 1)
        self.label = QtGui.QLabel(ReportAccount)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 2)
        self.lstItems = CRBListBox(ReportAccount)
        self.lstItems.setObjectName(_fromUtf8("lstItems"))
        self.gridLayout.addWidget(self.lstItems, 4, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportAccount)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)

        self.retranslateUi(ReportAccount)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportAccount.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportAccount.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportAccount)

    def retranslateUi(self, ReportAccount):
        ReportAccount.setWindowTitle(_translate("ReportAccount", "Dialog", None))
        self.groupBox.setTitle(_translate("ReportAccount", "Период", None))
        self.label_4.setText(_translate("ReportAccount", "Дата окончания", None))
        self.label_3.setText(_translate("ReportAccount", "Дата начала", None))
        self.rbtnAccountDate.setText(_translate("ReportAccount", "Формирования счёта", None))
        self.rbtnServiceDate.setText(_translate("ReportAccount", "Выполнения услуги", None))
        self.groupBox_2.setTitle(_translate("ReportAccount", "Группировка", None))
        self.rbtnSMO.setText(_translate("ReportAccount", "по компании", None))
        self.rbtnClient.setText(_translate("ReportAccount", "по ФИО", None))
        self.lblInsurer.setText(_translate("ReportAccount", "Плательщик", None))
        self.label.setText(_translate("ReportAccount", "Тип финансирования", None))

from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
