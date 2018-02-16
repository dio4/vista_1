# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ActionPropertyCopyDialog.ui'
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

class Ui_ActionPropertyCopyDialog(object):
    def setupUi(self, ActionPropertyCopyDialog):
        ActionPropertyCopyDialog.setObjectName(_fromUtf8("ActionPropertyCopyDialog"))
        ActionPropertyCopyDialog.resize(845, 710)
        self.gridLayout = QtGui.QGridLayout(ActionPropertyCopyDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.edtDateFrom = CDateEdit(ActionPropertyCopyDialog)
        self.edtDateFrom.setObjectName(_fromUtf8("edtDateFrom"))
        self.gridLayout_2.addWidget(self.edtDateFrom, 2, 2, 1, 1)
        self.lblDateFrom = QtGui.QLabel(ActionPropertyCopyDialog)
        self.lblDateFrom.setObjectName(_fromUtf8("lblDateFrom"))
        self.gridLayout_2.addWidget(self.lblDateFrom, 2, 1, 1, 1)
        self.lblDateTo = QtGui.QLabel(ActionPropertyCopyDialog)
        self.lblDateTo.setObjectName(_fromUtf8("lblDateTo"))
        self.gridLayout_2.addWidget(self.lblDateTo, 2, 3, 1, 1)
        self.lblPerson = QtGui.QLabel(ActionPropertyCopyDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout_2.addWidget(self.lblPerson, 0, 0, 1, 1)
        self.lblSpeciality = QtGui.QLabel(ActionPropertyCopyDialog)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout_2.addWidget(self.lblSpeciality, 1, 0, 1, 1)
        self.edtDateTo = CDateEdit(ActionPropertyCopyDialog)
        self.edtDateTo.setObjectName(_fromUtf8("edtDateTo"))
        self.gridLayout_2.addWidget(self.edtDateTo, 2, 4, 1, 1)
        self.lblDate = QtGui.QLabel(ActionPropertyCopyDialog)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout_2.addWidget(self.lblDate, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 2, 5, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ActionPropertyCopyDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbPerson.sizePolicy().hasHeightForWidth())
        self.cmbPerson.setSizePolicy(sizePolicy)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout_2.addWidget(self.cmbPerson, 0, 1, 1, 4)
        self.cmbSpeciality = CRBComboBox(ActionPropertyCopyDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSpeciality.sizePolicy().hasHeightForWidth())
        self.cmbSpeciality.setSizePolicy(sizePolicy)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout_2.addWidget(self.cmbSpeciality, 1, 1, 1, 4)
        self.horizontalLayout.addLayout(self.gridLayout_2)
        self.buttonBox = QtGui.QDialogButtonBox(ActionPropertyCopyDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.splitter = QtGui.QSplitter(ActionPropertyCopyDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tblActions = CTableView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(60)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblActions.sizePolicy().hasHeightForWidth())
        self.tblActions.setSizePolicy(sizePolicy)
        self.tblActions.setObjectName(_fromUtf8("tblActions"))
        self.tblProperties = CTableView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(40)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblProperties.sizePolicy().hasHeightForWidth())
        self.tblProperties.setSizePolicy(sizePolicy)
        self.tblProperties.setObjectName(_fromUtf8("tblProperties"))
        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 1)

        self.retranslateUi(ActionPropertyCopyDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ActionPropertyCopyDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ActionPropertyCopyDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ActionPropertyCopyDialog)
        ActionPropertyCopyDialog.setTabOrder(self.cmbPerson, self.cmbSpeciality)
        ActionPropertyCopyDialog.setTabOrder(self.cmbSpeciality, self.edtDateFrom)
        ActionPropertyCopyDialog.setTabOrder(self.edtDateFrom, self.edtDateTo)
        ActionPropertyCopyDialog.setTabOrder(self.edtDateTo, self.tblActions)
        ActionPropertyCopyDialog.setTabOrder(self.tblActions, self.tblProperties)
        ActionPropertyCopyDialog.setTabOrder(self.tblProperties, self.buttonBox)

    def retranslateUi(self, ActionPropertyCopyDialog):
        ActionPropertyCopyDialog.setWindowTitle(_translate("ActionPropertyCopyDialog", "Dialog", None))
        self.lblDateFrom.setText(_translate("ActionPropertyCopyDialog", "от", None))
        self.lblDateTo.setText(_translate("ActionPropertyCopyDialog", "до", None))
        self.lblPerson.setText(_translate("ActionPropertyCopyDialog", "Исполнитель", None))
        self.lblSpeciality.setText(_translate("ActionPropertyCopyDialog", "Специальность", None))
        self.lblDate.setText(_translate("ActionPropertyCopyDialog", "Дата выполнения", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from library.TableView import CTableView
from library.crbcombobox import CRBComboBox
