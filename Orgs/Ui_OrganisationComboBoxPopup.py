# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Orgs/OrganisationComboBoxPopup.ui'
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

class Ui_OrganisationComboBoxPopup(object):
    def setupUi(self, OrganisationComboBoxPopup):
        OrganisationComboBoxPopup.setObjectName(_fromUtf8("OrganisationComboBoxPopup"))
        OrganisationComboBoxPopup.resize(387, 306)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(OrganisationComboBoxPopup)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.tabWidget = QtGui.QTabWidget(OrganisationComboBoxPopup)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tblOrganisation = COrganisationComboBoxListView(self.tab)
        self.tblOrganisation.setObjectName(_fromUtf8("tblOrganisation"))
        self.verticalLayout.addWidget(self.tblOrganisation)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.gridLayout = QtGui.QGridLayout(self.tab_2)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkArea = QtGui.QCheckBox(self.tab_2)
        self.chkArea.setEnabled(True)
        self.chkArea.setChecked(False)
        self.chkArea.setObjectName(_fromUtf8("chkArea"))
        self.gridLayout.addWidget(self.chkArea, 0, 0, 1, 1)
        self.cmbArea = CKLADRComboBox(self.tab_2)
        self.cmbArea.setEnabled(False)
        self.cmbArea.setObjectName(_fromUtf8("cmbArea"))
        self.gridLayout.addWidget(self.cmbArea, 0, 2, 1, 1)
        self.lblInfis = QtGui.QLabel(self.tab_2)
        self.lblInfis.setObjectName(_fromUtf8("lblInfis"))
        self.gridLayout.addWidget(self.lblInfis, 1, 0, 1, 1)
        self.edtInfis = QtGui.QLineEdit(self.tab_2)
        self.edtInfis.setObjectName(_fromUtf8("edtInfis"))
        self.gridLayout.addWidget(self.edtInfis, 1, 2, 1, 1)
        self.lblName = QtGui.QLabel(self.tab_2)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 2, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 10, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(self.tab_2)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 2, 2, 1, 1)
        self.lblPolisSerial = QtGui.QLabel(self.tab_2)
        self.lblPolisSerial.setObjectName(_fromUtf8("lblPolisSerial"))
        self.gridLayout.addWidget(self.lblPolisSerial, 5, 0, 2, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(self.tab_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 11, 0, 1, 3)
        self.edtINN = QtGui.QLineEdit(self.tab_2)
        self.edtINN.setObjectName(_fromUtf8("edtINN"))
        self.gridLayout.addWidget(self.edtINN, 3, 2, 1, 1)
        self.lblINN = QtGui.QLabel(self.tab_2)
        self.lblINN.setObjectName(_fromUtf8("lblINN"))
        self.gridLayout.addWidget(self.lblINN, 3, 0, 1, 1)
        self.edtPolisSerial = COrganisationComboBoxPopupPolicySerialEdit(self.tab_2)
        self.edtPolisSerial.setObjectName(_fromUtf8("edtPolisSerial"))
        self.gridLayout.addWidget(self.edtPolisSerial, 6, 2, 1, 1)
        self.lblOGRN = QtGui.QLabel(self.tab_2)
        self.lblOGRN.setObjectName(_fromUtf8("lblOGRN"))
        self.gridLayout.addWidget(self.lblOGRN, 7, 0, 1, 1)
        self.lblOKATO = QtGui.QLabel(self.tab_2)
        self.lblOKATO.setObjectName(_fromUtf8("lblOKATO"))
        self.gridLayout.addWidget(self.lblOKATO, 9, 0, 1, 1)
        self.edtOGRN = QtGui.QLineEdit(self.tab_2)
        self.edtOGRN.setObjectName(_fromUtf8("edtOGRN"))
        self.gridLayout.addWidget(self.edtOGRN, 7, 2, 1, 1)
        self.edtOKATO = QtGui.QLineEdit(self.tab_2)
        self.edtOKATO.setObjectName(_fromUtf8("edtOKATO"))
        self.gridLayout.addWidget(self.edtOKATO, 9, 2, 1, 1)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.horizontalLayout_2.addWidget(self.tabWidget)
        self.lblInfis.setBuddy(self.edtInfis)
        self.lblName.setBuddy(self.edtName)
        self.lblPolisSerial.setBuddy(self.edtPolisSerial)
        self.lblINN.setBuddy(self.edtINN)
        self.lblOGRN.setBuddy(self.edtOGRN)
        self.lblOKATO.setBuddy(self.edtOKATO)

        self.retranslateUi(OrganisationComboBoxPopup)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.chkArea, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cmbArea.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(OrganisationComboBoxPopup)
        OrganisationComboBoxPopup.setTabOrder(self.tabWidget, self.tblOrganisation)
        OrganisationComboBoxPopup.setTabOrder(self.tblOrganisation, self.chkArea)
        OrganisationComboBoxPopup.setTabOrder(self.chkArea, self.cmbArea)
        OrganisationComboBoxPopup.setTabOrder(self.cmbArea, self.edtInfis)
        OrganisationComboBoxPopup.setTabOrder(self.edtInfis, self.edtName)
        OrganisationComboBoxPopup.setTabOrder(self.edtName, self.edtINN)
        OrganisationComboBoxPopup.setTabOrder(self.edtINN, self.edtPolisSerial)
        OrganisationComboBoxPopup.setTabOrder(self.edtPolisSerial, self.buttonBox)

    def retranslateUi(self, OrganisationComboBoxPopup):
        OrganisationComboBoxPopup.setWindowTitle(_translate("OrganisationComboBoxPopup", "Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("OrganisationComboBoxPopup", "&МО", None))
        self.chkArea.setText(_translate("OrganisationComboBoxPopup", "&Регион", None))
        self.lblInfis.setText(_translate("OrganisationComboBoxPopup", "Код ИН&ФИС", None))
        self.lblName.setText(_translate("OrganisationComboBoxPopup", "&Название содержит", None))
        self.lblPolisSerial.setText(_translate("OrganisationComboBoxPopup", "Серия", None))
        self.lblINN.setText(_translate("OrganisationComboBoxPopup", "&ИНН", None))
        self.lblOGRN.setText(_translate("OrganisationComboBoxPopup", "ОГРН", None))
        self.lblOKATO.setText(_translate("OrganisationComboBoxPopup", "ОКАТО", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("OrganisationComboBoxPopup", "&Поиск", None))

from KLADR.kladrComboxes import CKLADRComboBox
from OrganisationComboBoxPopup import COrganisationComboBoxListView, COrganisationComboBoxPopupPolicySerialEdit
