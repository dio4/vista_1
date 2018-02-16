# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ActionTemplateFindDialog.ui'
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

class Ui_ActionTemplateFindDialog(object):
    def setupUi(self, ActionTemplateFindDialog):
        ActionTemplateFindDialog.setObjectName(_fromUtf8("ActionTemplateFindDialog"))
        ActionTemplateFindDialog.resize(772, 394)
        ActionTemplateFindDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ActionTemplateFindDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbActionType = CActionTypeComboBox(ActionTemplateFindDialog)
        self.cmbActionType.setObjectName(_fromUtf8("cmbActionType"))
        self.gridLayout.addWidget(self.cmbActionType, 1, 1, 1, 2)
        self.cmbSpeciality = CRBComboBox(ActionTemplateFindDialog)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 3, 1, 1, 2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.cmbSex = QtGui.QComboBox(ActionTemplateFindDialog)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.horizontalLayout_3.addWidget(self.cmbSex)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 1, 1, 2)
        self.cmbPerson = CPersonComboBoxEx(ActionTemplateFindDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 4, 1, 1, 2)
        self.lblSex = QtGui.QLabel(ActionTemplateFindDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout.addWidget(self.lblSex, 2, 0, 1, 1)
        self.label_5 = QtGui.QLabel(ActionTemplateFindDialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.label_4 = QtGui.QLabel(ActionTemplateFindDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ActionTemplateFindDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 0, 1, 1, 2)
        self.tblRecords = CTableView(ActionTemplateFindDialog)
        self.tblRecords.setObjectName(_fromUtf8("tblRecords"))
        self.gridLayout.addWidget(self.tblRecords, 5, 0, 1, 3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(ActionTemplateFindDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 8, 0, 1, 3)
        self.lblRecordsCount = QtGui.QLabel(ActionTemplateFindDialog)
        self.lblRecordsCount.setObjectName(_fromUtf8("lblRecordsCount"))
        self.gridLayout.addWidget(self.lblRecordsCount, 7, 0, 1, 3)
        self.lblName = QtGui.QLabel(ActionTemplateFindDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblName.sizePolicy().hasHeightForWidth())
        self.lblName.setSizePolicy(sizePolicy)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 0, 0, 1, 1)
        self.lblActionType = QtGui.QLabel(ActionTemplateFindDialog)
        self.lblActionType.setObjectName(_fromUtf8("lblActionType"))
        self.gridLayout.addWidget(self.lblActionType, 1, 0, 1, 1)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(ActionTemplateFindDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ActionTemplateFindDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ActionTemplateFindDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ActionTemplateFindDialog)
        ActionTemplateFindDialog.setTabOrder(self.edtName, self.tblRecords)
        ActionTemplateFindDialog.setTabOrder(self.tblRecords, self.buttonBox)

    def retranslateUi(self, ActionTemplateFindDialog):
        ActionTemplateFindDialog.setWindowTitle(_translate("ActionTemplateFindDialog", "Dialog", None))
        self.cmbSex.setItemText(0, _translate("ActionTemplateFindDialog", "Любой", None))
        self.cmbSex.setItemText(1, _translate("ActionTemplateFindDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("ActionTemplateFindDialog", "Ж", None))
        self.lblSex.setText(_translate("ActionTemplateFindDialog", "Пол", None))
        self.label_5.setText(_translate("ActionTemplateFindDialog", "Врач", None))
        self.label_4.setText(_translate("ActionTemplateFindDialog", "Специальность", None))
        self.lblRecordsCount.setText(_translate("ActionTemplateFindDialog", "Список пуст", None))
        self.lblName.setText(_translate("ActionTemplateFindDialog", "&Наименование содержит", None))
        self.lblActionType.setText(_translate("ActionTemplateFindDialog", "Тип действия", None))

from Events.ActionTypeComboBox import CActionTypeComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.TableView import CTableView
from library.crbcombobox import CRBComboBox
