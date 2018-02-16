# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportCheckJury.ui'
#
# Created: Fri Jul 04 17:28:58 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_ReportCheckJury(object):
    def setupUi(self, ReportCheckJury):
        ReportCheckJury.setObjectName(_fromUtf8("ReportCheckJury"))
        ReportCheckJury.resize(400, 294)
        self.buttonBox = QtGui.QDialogButtonBox(ReportCheckJury)
        self.buttonBox.setGeometry(QtCore.QRect(50, 260, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(ReportCheckJury)
        self.label.setGeometry(QtCore.QRect(10, 10, 141, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.edtFilePath = QtGui.QLineEdit(ReportCheckJury)
        self.edtFilePath.setGeometry(QtCore.QRect(10, 30, 341, 27))
        self.edtFilePath.setObjectName(_fromUtf8("edtFilePath"))
        self.btnOpenFile = QtGui.QToolButton(ReportCheckJury)
        self.btnOpenFile.setGeometry(QtCore.QRect(360, 30, 31, 25))
        self.btnOpenFile.setObjectName(_fromUtf8("btnOpenFile"))
        self.groupBox = QtGui.QGroupBox(ReportCheckJury)
        self.groupBox.setGeometry(QtCore.QRect(20, 60, 371, 161))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkFirstName = QtGui.QCheckBox(self.groupBox)
        self.chkFirstName.setChecked(True)
        self.chkFirstName.setObjectName(_fromUtf8("chkFirstName"))
        self.gridLayout.addWidget(self.chkFirstName, 1, 0, 1, 1)
        self.chkPartName = QtGui.QCheckBox(self.groupBox)
        self.chkPartName.setChecked(True)
        self.chkPartName.setObjectName(_fromUtf8("chkPartName"))
        self.gridLayout.addWidget(self.chkPartName, 2, 0, 1, 1)
        self.chkSex = QtGui.QCheckBox(self.groupBox)
        self.chkSex.setChecked(True)
        self.chkSex.setObjectName(_fromUtf8("chkSex"))
        self.gridLayout.addWidget(self.chkSex, 3, 0, 1, 1)
        self.chkLastName = QtGui.QCheckBox(self.groupBox)
        self.chkLastName.setChecked(True)
        self.chkLastName.setObjectName(_fromUtf8("chkLastName"))
        self.gridLayout.addWidget(self.chkLastName, 0, 0, 1, 1)
        self.chkBirthDate = QtGui.QCheckBox(self.groupBox)
        self.chkBirthDate.setChecked(True)
        self.chkBirthDate.setObjectName(_fromUtf8("chkBirthDate"))
        self.gridLayout.addWidget(self.chkBirthDate, 4, 0, 1, 1)
        self.chkClientId = QtGui.QCheckBox(ReportCheckJury)
        self.chkClientId.setGeometry(QtCore.QRect(20, 230, 161, 17))
        self.chkClientId.setObjectName(_fromUtf8("chkClientId"))
        self.chkClientIdentification = QtGui.QCheckBox(ReportCheckJury)
        self.chkClientIdentification.setGeometry(QtCore.QRect(20, 250, 201, 17))
        self.chkClientIdentification.setObjectName(_fromUtf8("chkClientIdentification"))

        self.retranslateUi(ReportCheckJury)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportCheckJury.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportCheckJury.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportCheckJury)

    def retranslateUi(self, ReportCheckJury):
        ReportCheckJury.setWindowTitle(_translate("ReportCheckJury", "Dialog", None))
        self.label.setText(_translate("ReportCheckJury", "Путь к файлу:", None))
        self.btnOpenFile.setText(_translate("ReportCheckJury", "...", None))
        self.groupBox.setTitle(_translate("ReportCheckJury", "Сверяемые поля", None))
        self.chkFirstName.setText(_translate("ReportCheckJury", "Имя", None))
        self.chkPartName.setText(_translate("ReportCheckJury", "Отчество", None))
        self.chkSex.setText(_translate("ReportCheckJury", "Пол", None))
        self.chkLastName.setText(_translate("ReportCheckJury", "Фамилия", None))
        self.chkBirthDate.setText(_translate("ReportCheckJury", "Дата рождения", None))
        self.chkClientId.setText(_translate("ReportCheckJury", "Выводить код пациента", None))
        self.chkClientIdentification.setText(_translate("ReportCheckJury", "Выводить № истории болезни", None))

