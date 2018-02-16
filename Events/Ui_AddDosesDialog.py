# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AddDosesDialog.ui'
#
# Created: Tue Nov 18 14:32:42 2014
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

class Ui_AddDosesDialog(object):
    def setupUi(self, AddDosesDialog):
        AddDosesDialog.setObjectName(_fromUtf8("AddDosesDialog"))
        AddDosesDialog.resize(766, 613)
        self.gridLayout = QtGui.QGridLayout(AddDosesDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lblRangeDoses = QtGui.QLabel(AddDosesDialog)
        self.lblRangeDoses.setObjectName(_fromUtf8("lblRangeDoses"))
        self.gridLayout_3.addWidget(self.lblRangeDoses, 0, 0, 1, 2)
        self.btnAddDoseToNextDay = QtGui.QPushButton(AddDosesDialog)
        self.btnAddDoseToNextDay.setObjectName(_fromUtf8("btnAddDoseToNextDay"))
        self.gridLayout_3.addWidget(self.btnAddDoseToNextDay, 4, 0, 1, 2)
        self.tblDoseList = QtGui.QTableView(AddDosesDialog)
        self.tblDoseList.setObjectName(_fromUtf8("tblDoseList"))
        self.gridLayout_3.addWidget(self.tblDoseList, 3, 0, 1, 2)
        self.btnAddDoseToAllDay = QtGui.QPushButton(AddDosesDialog)
        self.btnAddDoseToAllDay.setObjectName(_fromUtf8("btnAddDoseToAllDay"))
        self.gridLayout_3.addWidget(self.btnAddDoseToAllDay, 5, 0, 1, 2)
        self.gridLayout.addLayout(self.gridLayout_3, 3, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(AddDosesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 2, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.lblInjectionPath = QtGui.QLabel(AddDosesDialog)
        self.lblInjectionPath.setObjectName(_fromUtf8("lblInjectionPath"))
        self.verticalLayout_3.addWidget(self.lblInjectionPath)
        self.cmbInjectionPath = CRBComboBox(AddDosesDialog)
        self.cmbInjectionPath.setObjectName(_fromUtf8("cmbInjectionPath"))
        self.verticalLayout_3.addWidget(self.cmbInjectionPath)
        self.lblInterval = QtGui.QLabel(AddDosesDialog)
        self.lblInterval.setObjectName(_fromUtf8("lblInterval"))
        self.verticalLayout_3.addWidget(self.lblInterval)
        self.cmbInterval = QtGui.QComboBox(AddDosesDialog)
        self.cmbInterval.setObjectName(_fromUtf8("cmbInterval"))
        self.cmbInterval.addItem(_fromUtf8(""))
        self.cmbInterval.addItem(_fromUtf8(""))
        self.cmbInterval.addItem(_fromUtf8(""))
        self.verticalLayout_3.addWidget(self.cmbInterval)
        self.lblBegDate = QtGui.QLabel(AddDosesDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.verticalLayout_3.addWidget(self.lblBegDate)
        self.edtBegDate = CDateEdit(AddDosesDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.verticalLayout_3.addWidget(self.edtBegDate)
        self.lblEndDate = QtGui.QLabel(AddDosesDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.verticalLayout_3.addWidget(self.lblEndDate)
        self.edtEndDate = CDateEdit(AddDosesDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.verticalLayout_3.addWidget(self.edtEndDate)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lblWhileTaking = QtGui.QLabel(AddDosesDialog)
        self.lblWhileTaking.setObjectName(_fromUtf8("lblWhileTaking"))
        self.verticalLayout.addWidget(self.lblWhileTaking)
        self.tblTimeList = QtGui.QTableView(AddDosesDialog)
        self.tblTimeList.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        self.tblTimeList.setObjectName(_fromUtf8("tblTimeList"))
        self.verticalLayout.addWidget(self.tblTimeList)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)

        self.retranslateUi(AddDosesDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AddDosesDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AddDosesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddDosesDialog)

    def retranslateUi(self, AddDosesDialog):
        AddDosesDialog.setWindowTitle(_translate("AddDosesDialog", "Выбор доз", None))
        self.lblRangeDoses.setText(_translate("AddDosesDialog", "Выбор доз", None))
        self.btnAddDoseToNextDay.setText(_translate("AddDosesDialog", "Заполнить дозы на следующий день", None))
        self.btnAddDoseToAllDay.setText(_translate("AddDosesDialog", "Заполнить дозы на все дни", None))
        self.lblInjectionPath.setText(_translate("AddDosesDialog", "Путь введения", None))
        self.lblInterval.setText(_translate("AddDosesDialog", "Интервал", None))
        self.cmbInterval.setItemText(0, _translate("AddDosesDialog", "ежедневно", None))
        self.cmbInterval.setItemText(1, _translate("AddDosesDialog", "через день", None))
        self.cmbInterval.setItemText(2, _translate("AddDosesDialog", "раз в два дня", None))
        self.lblBegDate.setText(_translate("AddDosesDialog", "Дата начала приёма", None))
        self.lblEndDate.setText(_translate("AddDosesDialog", "Дата окончания приёма", None))
        self.lblWhileTaking.setText(_translate("AddDosesDialog", "Время приёма", None))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
