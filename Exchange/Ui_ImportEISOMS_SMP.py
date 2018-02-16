# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ImportEISOMS_SMP.ui'
#
# Created: Mon Oct 26 14:20:30 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_ImportSMP(object):
    def setupUi(self, ImportSMP):
        ImportSMP.setObjectName(_fromUtf8("ImportSMP"))
        ImportSMP.resize(545, 356)
        self.gridLayout = QtGui.QGridLayout(ImportSMP)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btnImport = QtGui.QPushButton(ImportSMP)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.horizontalLayout_2.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ImportSMP)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout_2, 5, 0, 1, 2)
        self.loLoadForm = QtGui.QHBoxLayout()
        self.loLoadForm.setObjectName(_fromUtf8("loLoadForm"))
        self.lblLoadForm = QtGui.QLabel(ImportSMP)
        self.lblLoadForm.setObjectName(_fromUtf8("lblLoadForm"))
        self.loLoadForm.addWidget(self.lblLoadForm)
        self.edtFileName = QtGui.QLineEdit(ImportSMP)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.loLoadForm.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportSMP)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.loLoadForm.addWidget(self.btnSelectFile)
        self.gridLayout.addLayout(self.loLoadForm, 0, 0, 1, 2)
        self.progressBar = CProgressBar(ImportSMP)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 3, 0, 1, 2)
        self.logBrowser = QtGui.QTextBrowser(ImportSMP)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 4, 0, 1, 2)
        self.label = QtGui.QLabel(ImportSMP)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.cmbMod = QtGui.QComboBox(ImportSMP)
        self.cmbMod.setObjectName(_fromUtf8("cmbMod"))
        self.cmbMod.addItem(_fromUtf8(""))
        self.cmbMod.addItem(_fromUtf8(""))
        self.cmbMod.addItem(_fromUtf8(""))
        self.cmbMod.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbMod, 1, 1, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ImportSMP)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 2, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ImportSMP)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.retranslateUi(ImportSMP)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("clicked(QAbstractButton*)")), ImportSMP.close)
        QtCore.QMetaObject.connectSlotsByName(ImportSMP)

    def retranslateUi(self, ImportSMP):
        ImportSMP.setWindowTitle(_translate("ImportSMP", "Dialog", None))
        self.btnImport.setText(_translate("ImportSMP", "Импортировать", None))
        self.lblLoadForm.setText(_translate("ImportSMP", "Загрузить из", None))
        self.btnSelectFile.setText(_translate("ImportSMP", "...", None))
        self.label.setText(_translate("ImportSMP", "Тип поля ID_DOC", None))
        self.cmbMod.setItemText(0, _translate("ImportSMP", "ID врача", None))
        self.cmbMod.setItemText(1, _translate("ImportSMP", "Код врача", None))
        self.cmbMod.setItemText(2, _translate("ImportSMP", "Региональный код врача", None))
        self.cmbMod.setItemText(3, _translate("ImportSMP", "Федеральный код врача", None))
        self.label_2.setText(_translate("ImportSMP", "Врач по умолчанию", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.ProgressBar import CProgressBar
