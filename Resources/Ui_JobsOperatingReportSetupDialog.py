# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'JobsOperatingReportSetupDialog.ui'
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

class Ui_JobsOperatingReportSetupDialog(object):
    def setupUi(self, JobsOperatingReportSetupDialog):
        JobsOperatingReportSetupDialog.setObjectName(_fromUtf8("JobsOperatingReportSetupDialog"))
        JobsOperatingReportSetupDialog.resize(292, 226)
        self.gridLayout = QtGui.QGridLayout(JobsOperatingReportSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblColumsList = QtGui.QLabel(JobsOperatingReportSetupDialog)
        self.lblColumsList.setObjectName(_fromUtf8("lblColumsList"))
        self.gridLayout.addWidget(self.lblColumsList, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(JobsOperatingReportSetupDialog)
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.chkRowNumber = QtGui.QCheckBox(self.groupBox)
        self.chkRowNumber.setChecked(True)
        self.chkRowNumber.setObjectName(_fromUtf8("chkRowNumber"))
        self.gridLayout_2.addWidget(self.chkRowNumber, 0, 0, 1, 1)
        self.chkDatetime = QtGui.QCheckBox(self.groupBox)
        self.chkDatetime.setChecked(True)
        self.chkDatetime.setObjectName(_fromUtf8("chkDatetime"))
        self.gridLayout_2.addWidget(self.chkDatetime, 1, 0, 1, 1)
        self.chkClientName = QtGui.QCheckBox(self.groupBox)
        self.chkClientName.setChecked(True)
        self.chkClientName.setObjectName(_fromUtf8("chkClientName"))
        self.gridLayout_2.addWidget(self.chkClientName, 2, 0, 1, 1)
        self.chkClientSex = QtGui.QCheckBox(self.groupBox)
        self.chkClientSex.setChecked(True)
        self.chkClientSex.setObjectName(_fromUtf8("chkClientSex"))
        self.gridLayout_2.addWidget(self.chkClientSex, 3, 0, 1, 1)
        self.chkClientBirthday = QtGui.QCheckBox(self.groupBox)
        self.chkClientBirthday.setChecked(True)
        self.chkClientBirthday.setObjectName(_fromUtf8("chkClientBirthday"))
        self.gridLayout_2.addWidget(self.chkClientBirthday, 4, 0, 1, 1)
        self.chkActionType = QtGui.QCheckBox(self.groupBox)
        self.chkActionType.setChecked(True)
        self.chkActionType.setObjectName(_fromUtf8("chkActionType"))
        self.gridLayout_2.addWidget(self.chkActionType, 0, 1, 1, 1)
        self.chkSetPerson = QtGui.QCheckBox(self.groupBox)
        self.chkSetPerson.setChecked(True)
        self.chkSetPerson.setObjectName(_fromUtf8("chkSetPerson"))
        self.gridLayout_2.addWidget(self.chkSetPerson, 1, 1, 1, 1)
        self.chkLabel = QtGui.QCheckBox(self.groupBox)
        self.chkLabel.setChecked(True)
        self.chkLabel.setObjectName(_fromUtf8("chkLabel"))
        self.gridLayout_2.addWidget(self.chkLabel, 2, 1, 1, 1)
        self.chkNotes = QtGui.QCheckBox(self.groupBox)
        self.chkNotes.setChecked(True)
        self.chkNotes.setObjectName(_fromUtf8("chkNotes"))
        self.gridLayout_2.addWidget(self.chkNotes, 3, 1, 1, 1)
        self.chkBarCode = QtGui.QCheckBox(self.groupBox)
        self.chkBarCode.setChecked(True)
        self.chkBarCode.setObjectName(_fromUtf8("chkBarCode"))
        self.gridLayout_2.addWidget(self.chkBarCode, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(0, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(JobsOperatingReportSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(JobsOperatingReportSetupDialog)
        QtCore.QMetaObject.connectSlotsByName(JobsOperatingReportSetupDialog)
        JobsOperatingReportSetupDialog.setTabOrder(self.chkRowNumber, self.chkDatetime)
        JobsOperatingReportSetupDialog.setTabOrder(self.chkDatetime, self.chkClientName)
        JobsOperatingReportSetupDialog.setTabOrder(self.chkClientName, self.chkClientSex)
        JobsOperatingReportSetupDialog.setTabOrder(self.chkClientSex, self.chkClientBirthday)
        JobsOperatingReportSetupDialog.setTabOrder(self.chkClientBirthday, self.chkActionType)
        JobsOperatingReportSetupDialog.setTabOrder(self.chkActionType, self.chkSetPerson)
        JobsOperatingReportSetupDialog.setTabOrder(self.chkSetPerson, self.chkLabel)
        JobsOperatingReportSetupDialog.setTabOrder(self.chkLabel, self.chkNotes)
        JobsOperatingReportSetupDialog.setTabOrder(self.chkNotes, self.chkBarCode)
        JobsOperatingReportSetupDialog.setTabOrder(self.chkBarCode, self.buttonBox)

    def retranslateUi(self, JobsOperatingReportSetupDialog):
        JobsOperatingReportSetupDialog.setWindowTitle(_translate("JobsOperatingReportSetupDialog", "Dialog", None))
        self.lblColumsList.setText(_translate("JobsOperatingReportSetupDialog", "Выберите столбцы:", None))
        self.chkRowNumber.setText(_translate("JobsOperatingReportSetupDialog", "Номер строки", None))
        self.chkDatetime.setText(_translate("JobsOperatingReportSetupDialog", "Дата и время", None))
        self.chkClientName.setText(_translate("JobsOperatingReportSetupDialog", "Ф.И.О.", None))
        self.chkClientSex.setText(_translate("JobsOperatingReportSetupDialog", "Пол", None))
        self.chkClientBirthday.setText(_translate("JobsOperatingReportSetupDialog", "Дата рождения", None))
        self.chkActionType.setText(_translate("JobsOperatingReportSetupDialog", "Тип действия", None))
        self.chkSetPerson.setText(_translate("JobsOperatingReportSetupDialog", "Назначил, дата", None))
        self.chkLabel.setText(_translate("JobsOperatingReportSetupDialog", "Отметка", None))
        self.chkNotes.setText(_translate("JobsOperatingReportSetupDialog", "Примечание", None))
        self.chkBarCode.setText(_translate("JobsOperatingReportSetupDialog", "Штрих-код", None))

