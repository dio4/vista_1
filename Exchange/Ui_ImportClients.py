# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportClients.ui'
#
# Created: Tue Apr 14 13:54:50 2015
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

class Ui_ImportClients(object):
    def setupUi(self, ImportClients):
        ImportClients.setObjectName(_fromUtf8("ImportClients"))
        ImportClients.resize(400, 188)
        self.gridLayout = QtGui.QGridLayout(ImportClients)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ImportClients)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.edtFilePath = QtGui.QLineEdit(ImportClients)
        self.edtFilePath.setObjectName(_fromUtf8("edtFilePath"))
        self.horizontalLayout.addWidget(self.edtFilePath)
        self.btnOpenFile = QtGui.QToolButton(ImportClients)
        self.btnOpenFile.setObjectName(_fromUtf8("btnOpenFile"))
        self.horizontalLayout.addWidget(self.btnOpenFile)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 3)
        self.label_2 = QtGui.QLabel(ImportClients)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.cmbOrganisation = COrgComboBox(ImportClients)
        self.cmbOrganisation.setObjectName(_fromUtf8("cmbOrganisation"))
        self.horizontalLayout_3.addWidget(self.cmbOrganisation)
        self.btnSelectOrganisation = QtGui.QToolButton(ImportClients)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSelectOrganisation.sizePolicy().hasHeightForWidth())
        self.btnSelectOrganisation.setSizePolicy(sizePolicy)
        self.btnSelectOrganisation.setObjectName(_fromUtf8("btnSelectOrganisation"))
        self.horizontalLayout_3.addWidget(self.btnSelectOrganisation)
        self.gridLayout.addLayout(self.horizontalLayout_3, 3, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ImportClients)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 2, 1, 1)
        self.progressBar = CProgressBar(ImportClients)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 4, 0, 1, 3)
        self.lblProgressBar = QtGui.QLabel(ImportClients)
        self.lblProgressBar.setText(_fromUtf8(""))
        self.lblProgressBar.setObjectName(_fromUtf8("lblProgressBar"))
        self.gridLayout.addWidget(self.lblProgressBar, 5, 0, 1, 3)
        self.label_3 = QtGui.QLabel(ImportClients)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.cmbNameList = QtGui.QComboBox(ImportClients)
        self.cmbNameList.setEnabled(True)
        self.cmbNameList.setEditable(False)
        self.cmbNameList.setFrame(True)
        self.cmbNameList.setObjectName(_fromUtf8("cmbNameList"))
        self.gridLayout.addWidget(self.cmbNameList, 2, 1, 1, 2)

        self.retranslateUi(ImportClients)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ImportClients.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImportClients.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportClients)

    def retranslateUi(self, ImportClients):
        ImportClients.setWindowTitle(_translate("ImportClients", "Dialog", None))
        self.label.setText(_translate("ImportClients", "Путь к файлу:", None))
        self.btnOpenFile.setText(_translate("ImportClients", "...", None))
        self.label_2.setText(_translate("ImportClients", "Организация", None))
        self.btnSelectOrganisation.setText(_translate("ImportClients", "...", None))
        self.label_3.setText(_translate("ImportClients", "Лист", None))

from Orgs.OrgComboBox import COrgComboBox
from library.ProgressBar import CProgressBar
