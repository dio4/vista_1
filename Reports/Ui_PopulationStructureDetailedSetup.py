# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PopulationStructureDetailedSetup.ui'
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

class Ui_PopulationStructureDetailedSetup(object):
    def setupUi(self, PopulationStructureDetailedSetup):
        PopulationStructureDetailedSetup.setObjectName(_fromUtf8("PopulationStructureDetailedSetup"))
        PopulationStructureDetailedSetup.resize(624, 468)
        self.gridLayout = QtGui.QGridLayout(PopulationStructureDetailedSetup)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblDate = QtGui.QLabel(PopulationStructureDetailedSetup)
        self.lblDate.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblDate.setObjectName(_fromUtf8("lblDate"))
        self.gridLayout.addWidget(self.lblDate, 0, 0, 1, 1)
        self.edtDate = CDateEdit(PopulationStructureDetailedSetup)
        self.edtDate.setObjectName(_fromUtf8("edtDate"))
        self.gridLayout.addWidget(self.edtDate, 0, 1, 1, 1)
        self.lblAge = QtGui.QLabel(PopulationStructureDetailedSetup)
        self.lblAge.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout.addWidget(self.lblAge, 1, 0, 1, 1)
        self.grpAge = QtGui.QHBoxLayout()
        self.grpAge.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.grpAge.setSpacing(6)
        self.grpAge.setObjectName(_fromUtf8("grpAge"))
        self.edtAgeStart = QtGui.QSpinBox(PopulationStructureDetailedSetup)
        self.edtAgeStart.setObjectName(_fromUtf8("edtAgeStart"))
        self.grpAge.addWidget(self.edtAgeStart)
        self.lblAgeRange = QtGui.QLabel(PopulationStructureDetailedSetup)
        self.lblAgeRange.setObjectName(_fromUtf8("lblAgeRange"))
        self.grpAge.addWidget(self.lblAgeRange)
        self.edtAgeEnd = QtGui.QSpinBox(PopulationStructureDetailedSetup)
        self.edtAgeEnd.setMinimum(0)
        self.edtAgeEnd.setMaximum(200)
        self.edtAgeEnd.setProperty("value", 150)
        self.edtAgeEnd.setObjectName(_fromUtf8("edtAgeEnd"))
        self.grpAge.addWidget(self.edtAgeEnd)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.grpAge.addItem(spacerItem)
        self.gridLayout.addLayout(self.grpAge, 1, 1, 1, 1)
        self.lblSocStatusClass = QtGui.QLabel(PopulationStructureDetailedSetup)
        self.lblSocStatusClass.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblSocStatusClass.setObjectName(_fromUtf8("lblSocStatusClass"))
        self.gridLayout.addWidget(self.lblSocStatusClass, 2, 0, 1, 1)
        self.cmbSocStatusClass = CSocStatusComboBox(PopulationStructureDetailedSetup)
        self.cmbSocStatusClass.setObjectName(_fromUtf8("cmbSocStatusClass"))
        self.gridLayout.addWidget(self.cmbSocStatusClass, 2, 1, 1, 1)
        self.lblSocStatusType = QtGui.QLabel(PopulationStructureDetailedSetup)
        self.lblSocStatusType.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblSocStatusType.setObjectName(_fromUtf8("lblSocStatusType"))
        self.gridLayout.addWidget(self.lblSocStatusType, 3, 0, 1, 1)
        self.cmbSocStatusType = CRBComboBox(PopulationStructureDetailedSetup)
        self.cmbSocStatusType.setObjectName(_fromUtf8("cmbSocStatusType"))
        self.gridLayout.addWidget(self.cmbSocStatusType, 3, 1, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(PopulationStructureDetailedSetup)
        self.lblOrgStructure.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 4, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(PopulationStructureDetailedSetup)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 4, 1, 1, 1)
        self.label = QtGui.QLabel(PopulationStructureDetailedSetup)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 5, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PopulationStructureDetailedSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 2)
        self.splitter = QtGui.QSplitter(PopulationStructureDetailedSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.lstStreet = QtGui.QListView(self.splitter)
        self.lstStreet.setObjectName(_fromUtf8("lstStreet"))
        self.lstHouse = QtGui.QListView(self.splitter)
        self.lstHouse.setObjectName(_fromUtf8("lstHouse"))
        self.gridLayout.addWidget(self.splitter, 5, 1, 1, 1)

        self.retranslateUi(PopulationStructureDetailedSetup)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PopulationStructureDetailedSetup.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PopulationStructureDetailedSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(PopulationStructureDetailedSetup)

    def retranslateUi(self, PopulationStructureDetailedSetup):
        PopulationStructureDetailedSetup.setWindowTitle(_translate("PopulationStructureDetailedSetup", "Состав населения по участкам (детализированный)", None))
        self.lblDate.setText(_translate("PopulationStructureDetailedSetup", "Дата", None))
        self.lblAge.setText(_translate("PopulationStructureDetailedSetup", "Возраст с", None))
        self.edtAgeStart.setSuffix(_translate("PopulationStructureDetailedSetup", " лет", None))
        self.lblAgeRange.setText(_translate("PopulationStructureDetailedSetup", "по", None))
        self.edtAgeEnd.setSuffix(_translate("PopulationStructureDetailedSetup", " лет", None))
        self.lblSocStatusClass.setText(_translate("PopulationStructureDetailedSetup", "Класс соц. статуса", None))
        self.lblSocStatusType.setText(_translate("PopulationStructureDetailedSetup", "Тип соц. статуса", None))
        self.lblOrgStructure.setText(_translate("PopulationStructureDetailedSetup", "Подразделение", None))
        self.label.setText(_translate("PopulationStructureDetailedSetup", "Адрес", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Registry.SocStatusComboBox import CSocStatusComboBox
from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
