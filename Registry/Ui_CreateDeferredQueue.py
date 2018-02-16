# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CreateDeferredQueue.ui'
#
# Created: Tue Nov 17 16:26:00 2015
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

class Ui_CreateDeferredQueueDialog(object):
    def setupUi(self, CreateDeferredQueueDialog):
        CreateDeferredQueueDialog.setObjectName(_fromUtf8("CreateDeferredQueueDialog"))
        CreateDeferredQueueDialog.resize(579, 340)
        self.gridLayout = QtGui.QGridLayout(CreateDeferredQueueDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gbAfterAddingBehaviour = QtGui.QGroupBox(CreateDeferredQueueDialog)
        self.gbAfterAddingBehaviour.setObjectName(_fromUtf8("gbAfterAddingBehaviour"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.gbAfterAddingBehaviour)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.rbReturnToDeferredQueue = QtGui.QRadioButton(self.gbAfterAddingBehaviour)
        self.rbReturnToDeferredQueue.setObjectName(_fromUtf8("rbReturnToDeferredQueue"))
        self.horizontalLayout.addWidget(self.rbReturnToDeferredQueue)
        self.rbReturnToRegistry = QtGui.QRadioButton(self.gbAfterAddingBehaviour)
        self.rbReturnToRegistry.setObjectName(_fromUtf8("rbReturnToRegistry"))
        self.horizontalLayout.addWidget(self.rbReturnToRegistry)
        self.gridLayout.addWidget(self.gbAfterAddingBehaviour, 6, 1, 1, 1)
        self.label_12 = QtGui.QLabel(CreateDeferredQueueDialog)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout.addWidget(self.label_12, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.edtClient = QtGui.QLineEdit(CreateDeferredQueueDialog)
        self.edtClient.setEnabled(True)
        self.edtClient.setObjectName(_fromUtf8("edtClient"))
        self.horizontalLayout_3.addWidget(self.edtClient)
        self.btnClient = QtGui.QToolButton(CreateDeferredQueueDialog)
        self.btnClient.setEnabled(True)
        self.btnClient.setObjectName(_fromUtf8("btnClient"))
        self.horizontalLayout_3.addWidget(self.btnClient)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)
        self.label_17 = QtGui.QLabel(CreateDeferredQueueDialog)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.gridLayout.addWidget(self.label_17, 1, 0, 1, 1)
        self.edtMaxDate = CDateEdit(CreateDeferredQueueDialog)
        self.edtMaxDate.setObjectName(_fromUtf8("edtMaxDate"))
        self.gridLayout.addWidget(self.edtMaxDate, 1, 1, 1, 1)
        self.label_13 = QtGui.QLabel(CreateDeferredQueueDialog)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout.addWidget(self.label_13, 3, 0, 1, 1)
        self.cmbSpeciality = CRBComboBox(CreateDeferredQueueDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSpeciality.sizePolicy().hasHeightForWidth())
        self.cmbSpeciality.setSizePolicy(sizePolicy)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 3, 1, 1, 1)
        self.label_14 = QtGui.QLabel(CreateDeferredQueueDialog)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout.addWidget(self.label_14, 4, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(CreateDeferredQueueDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbPerson.sizePolicy().hasHeightForWidth())
        self.cmbPerson.setSizePolicy(sizePolicy)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 4, 1, 1, 1)
        self.label_16 = QtGui.QLabel(CreateDeferredQueueDialog)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout.addWidget(self.label_16, 5, 0, 1, 1)
        self.edtComments = QtGui.QTextEdit(CreateDeferredQueueDialog)
        self.edtComments.setObjectName(_fromUtf8("edtComments"))
        self.gridLayout.addWidget(self.edtComments, 5, 1, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(CreateDeferredQueueDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout_5.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout_5, 7, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(CreateDeferredQueueDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(CreateDeferredQueueDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 1)
        self.label_12.setBuddy(self.edtClient)
        self.label_17.setBuddy(self.edtMaxDate)
        self.label_13.setBuddy(self.cmbSpeciality)
        self.label_14.setBuddy(self.cmbPerson)
        self.label_16.setBuddy(self.edtComments)

        self.retranslateUi(CreateDeferredQueueDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CreateDeferredQueueDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CreateDeferredQueueDialog)
        CreateDeferredQueueDialog.setTabOrder(self.edtClient, self.btnClient)
        CreateDeferredQueueDialog.setTabOrder(self.btnClient, self.edtMaxDate)
        CreateDeferredQueueDialog.setTabOrder(self.edtMaxDate, self.cmbSpeciality)
        CreateDeferredQueueDialog.setTabOrder(self.cmbSpeciality, self.cmbPerson)
        CreateDeferredQueueDialog.setTabOrder(self.cmbPerson, self.edtComments)

    def retranslateUi(self, CreateDeferredQueueDialog):
        CreateDeferredQueueDialog.setWindowTitle(_translate("CreateDeferredQueueDialog", "Dialog", None))
        self.gbAfterAddingBehaviour.setTitle(_translate("CreateDeferredQueueDialog", "После добавления перейти в окно", None))
        self.rbReturnToDeferredQueue.setText(_translate("CreateDeferredQueueDialog", "Журнала отложенного спроса", None))
        self.rbReturnToRegistry.setText(_translate("CreateDeferredQueueDialog", "Картотеки", None))
        self.label_12.setText(_translate("CreateDeferredQueueDialog", "Пациент", None))
        self.btnClient.setText(_translate("CreateDeferredQueueDialog", "...", None))
        self.label_17.setText(_translate("CreateDeferredQueueDialog", "Крайняя дата", None))
        self.label_13.setText(_translate("CreateDeferredQueueDialog", "Специальность", None))
        self.label_14.setText(_translate("CreateDeferredQueueDialog", "Врач", None))
        self.label_16.setText(_translate("CreateDeferredQueueDialog", "Комментарий", None))
        self.lblOrgStructure.setText(_translate("CreateDeferredQueueDialog", "Подразделение", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
