# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HospitalizationEventDialog.ui'
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

class Ui_HospitalizationEventDialog(object):
    def setupUi(self, HospitalizationEventDialog):
        HospitalizationEventDialog.setObjectName(_fromUtf8("HospitalizationEventDialog"))
        HospitalizationEventDialog.resize(640, 450)
        self.gridLayout_2 = QtGui.QGridLayout(HospitalizationEventDialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.tabWidget = QtGui.QTabWidget(HospitalizationEventDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabHospitalizationEvent = QtGui.QWidget()
        self.tabHospitalizationEvent.setObjectName(_fromUtf8("tabHospitalizationEvent"))
        self.vboxlayout = QtGui.QVBoxLayout(self.tabHospitalizationEvent)
        self.vboxlayout.setMargin(4)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.tblHospitalizationEvent = CClientsTableView(self.tabHospitalizationEvent)
        self.tblHospitalizationEvent.setObjectName(_fromUtf8("tblHospitalizationEvent"))
        self.vboxlayout.addWidget(self.tblHospitalizationEvent)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.btnCommit = QtGui.QPushButton(self.tabHospitalizationEvent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnCommit.sizePolicy().hasHeightForWidth())
        self.btnCommit.setSizePolicy(sizePolicy)
        self.btnCommit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.btnCommit.setObjectName(_fromUtf8("btnCommit"))
        self.horizontalLayout_3.addWidget(self.btnCommit)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.btnRegistry = QtGui.QPushButton(self.tabHospitalizationEvent)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRegistry.sizePolicy().hasHeightForWidth())
        self.btnRegistry.setSizePolicy(sizePolicy)
        self.btnRegistry.setMinimumSize(QtCore.QSize(100, 0))
        self.btnRegistry.setObjectName(_fromUtf8("btnRegistry"))
        self.horizontalLayout_3.addWidget(self.btnRegistry)
        self.vboxlayout.addLayout(self.horizontalLayout_3)
        self.tabWidget.addTab(self.tabHospitalizationEvent, _fromUtf8(""))
        self.tabSearch = QtGui.QWidget()
        self.tabSearch.setObjectName(_fromUtf8("tabSearch"))
        self.gridLayout = QtGui.QGridLayout(self.tabSearch)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblPolicy = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPolicy.sizePolicy().hasHeightForWidth())
        self.lblPolicy.setSizePolicy(sizePolicy)
        self.lblPolicy.setObjectName(_fromUtf8("lblPolicy"))
        self.gridLayout.addWidget(self.lblPolicy, 8, 0, 1, 1)
        self.lblClientId = QtGui.QLabel(self.tabSearch)
        self.lblClientId.setObjectName(_fromUtf8("lblClientId"))
        self.gridLayout.addWidget(self.lblClientId, 5, 0, 1, 1)
        self.cmbPolicyInsurer = CInsurerComboBox(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbPolicyInsurer.sizePolicy().hasHeightForWidth())
        self.cmbPolicyInsurer.setSizePolicy(sizePolicy)
        self.cmbPolicyInsurer.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.cmbPolicyInsurer.setObjectName(_fromUtf8("cmbPolicyInsurer"))
        self.gridLayout.addWidget(self.cmbPolicyInsurer, 9, 7, 1, 5)
        spacerItem1 = QtGui.QSpacerItem(57, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 9, 12, 1, 1)
        self.lblContact = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblContact.sizePolicy().hasHeightForWidth())
        self.lblContact.setSizePolicy(sizePolicy)
        self.lblContact.setObjectName(_fromUtf8("lblContact"))
        self.gridLayout.addWidget(self.lblContact, 15, 0, 1, 2)
        self.lblNumber = QtGui.QLabel(self.tabSearch)
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.gridLayout.addWidget(self.lblNumber, 7, 10, 1, 1)
        self.edtNumber = QtGui.QLineEdit(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtNumber.sizePolicy().hasHeightForWidth())
        self.edtNumber.setSizePolicy(sizePolicy)
        self.edtNumber.setObjectName(_fromUtf8("edtNumber"))
        self.gridLayout.addWidget(self.edtNumber, 7, 11, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(74, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 7, 12, 1, 1)
        self.edtRightSerial = QtGui.QLineEdit(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtRightSerial.sizePolicy().hasHeightForWidth())
        self.edtRightSerial.setSizePolicy(sizePolicy)
        self.edtRightSerial.setObjectName(_fromUtf8("edtRightSerial"))
        self.gridLayout.addWidget(self.edtRightSerial, 7, 9, 1, 1)
        self.lblSerial = QtGui.QLabel(self.tabSearch)
        self.lblSerial.setObjectName(_fromUtf8("lblSerial"))
        self.gridLayout.addWidget(self.lblSerial, 7, 5, 1, 1)
        self.lblPatrName = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPatrName.sizePolicy().hasHeightForWidth())
        self.lblPatrName.setSizePolicy(sizePolicy)
        self.lblPatrName.setObjectName(_fromUtf8("lblPatrName"))
        self.gridLayout.addWidget(self.lblPatrName, 3, 0, 1, 2)
        self.edtPatrName = QtGui.QLineEdit(self.tabSearch)
        self.edtPatrName.setObjectName(_fromUtf8("edtPatrName"))
        self.gridLayout.addWidget(self.edtPatrName, 3, 2, 1, 11)
        self.lblFirstName = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFirstName.sizePolicy().hasHeightForWidth())
        self.lblFirstName.setSizePolicy(sizePolicy)
        self.lblFirstName.setObjectName(_fromUtf8("lblFirstName"))
        self.gridLayout.addWidget(self.lblFirstName, 2, 0, 1, 2)
        self.edtContact = QtGui.QLineEdit(self.tabSearch)
        self.edtContact.setObjectName(_fromUtf8("edtContact"))
        self.gridLayout.addWidget(self.edtContact, 15, 2, 1, 11)
        self.edtLastName = QtGui.QLineEdit(self.tabSearch)
        self.edtLastName.setObjectName(_fromUtf8("edtLastName"))
        self.gridLayout.addWidget(self.edtLastName, 1, 2, 1, 11)
        self.edtFirstName = QtGui.QLineEdit(self.tabSearch)
        self.edtFirstName.setObjectName(_fromUtf8("edtFirstName"))
        self.gridLayout.addWidget(self.edtFirstName, 2, 2, 1, 11)
        self.edtPolicySerial = CPolicySerialEdit(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtPolicySerial.sizePolicy().hasHeightForWidth())
        self.edtPolicySerial.setSizePolicy(sizePolicy)
        self.edtPolicySerial.setObjectName(_fromUtf8("edtPolicySerial"))
        self.gridLayout.addWidget(self.edtPolicySerial, 8, 7, 1, 3)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 8, 12, 1, 1)
        self.lblCompulsoryPolisNumber = QtGui.QLabel(self.tabSearch)
        self.lblCompulsoryPolisNumber.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblCompulsoryPolisNumber.setObjectName(_fromUtf8("lblCompulsoryPolisNumber"))
        self.gridLayout.addWidget(self.lblCompulsoryPolisNumber, 8, 10, 1, 1)
        self.edtPolicyNumber = QtGui.QLineEdit(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtPolicyNumber.sizePolicy().hasHeightForWidth())
        self.edtPolicyNumber.setSizePolicy(sizePolicy)
        self.edtPolicyNumber.setObjectName(_fromUtf8("edtPolicyNumber"))
        self.gridLayout.addWidget(self.edtPolicyNumber, 8, 11, 1, 1)
        self.lblPolicyInsurer = QtGui.QLabel(self.tabSearch)
        self.lblPolicyInsurer.setObjectName(_fromUtf8("lblPolicyInsurer"))
        self.gridLayout.addWidget(self.lblPolicyInsurer, 9, 5, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(20, 141, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem4, 16, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem5 = QtGui.QSpacerItem(231, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.readEpoms = QtGui.QPushButton(self.tabSearch)
        self.readEpoms.setObjectName(_fromUtf8("readEpoms"))
        self.horizontalLayout.addWidget(self.readEpoms)
        self.btnReadOMSBarcode = QtGui.QPushButton(self.tabSearch)
        self.btnReadOMSBarcode.setObjectName(_fromUtf8("btnReadOMSBarcode"))
        self.horizontalLayout.addWidget(self.btnReadOMSBarcode)
        self.btnApply = QtGui.QPushButton(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnApply.sizePolicy().hasHeightForWidth())
        self.btnApply.setSizePolicy(sizePolicy)
        self.btnApply.setMinimumSize(QtCore.QSize(100, 0))
        self.btnApply.setObjectName(_fromUtf8("btnApply"))
        self.horizontalLayout.addWidget(self.btnApply)
        self.btnReset = QtGui.QPushButton(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnReset.sizePolicy().hasHeightForWidth())
        self.btnReset.setSizePolicy(sizePolicy)
        self.btnReset.setMinimumSize(QtCore.QSize(100, 0))
        self.btnReset.setObjectName(_fromUtf8("btnReset"))
        self.horizontalLayout.addWidget(self.btnReset)
        self.gridLayout.addLayout(self.horizontalLayout, 17, 0, 1, 13)
        self.lblPolicySerial = QtGui.QLabel(self.tabSearch)
        self.lblPolicySerial.setObjectName(_fromUtf8("lblPolicySerial"))
        self.gridLayout.addWidget(self.lblPolicySerial, 8, 5, 1, 1)
        self.edtLeftSerial = QtGui.QLineEdit(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtLeftSerial.sizePolicy().hasHeightForWidth())
        self.edtLeftSerial.setSizePolicy(sizePolicy)
        self.edtLeftSerial.setObjectName(_fromUtf8("edtLeftSerial"))
        self.gridLayout.addWidget(self.edtLeftSerial, 7, 7, 1, 1)
        self.lblLastName = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblLastName.sizePolicy().hasHeightForWidth())
        self.lblLastName.setSizePolicy(sizePolicy)
        self.lblLastName.setObjectName(_fromUtf8("lblLastName"))
        self.gridLayout.addWidget(self.lblLastName, 1, 0, 1, 2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lblPolicyBegDate = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPolicyBegDate.sizePolicy().hasHeightForWidth())
        self.lblPolicyBegDate.setSizePolicy(sizePolicy)
        self.lblPolicyBegDate.setObjectName(_fromUtf8("lblPolicyBegDate"))
        self.horizontalLayout_2.addWidget(self.lblPolicyBegDate)
        self.edtPolicyBegDate = CDateEdit(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtPolicyBegDate.sizePolicy().hasHeightForWidth())
        self.edtPolicyBegDate.setSizePolicy(sizePolicy)
        self.edtPolicyBegDate.setCalendarPopup(True)
        self.edtPolicyBegDate.setObjectName(_fromUtf8("edtPolicyBegDate"))
        self.horizontalLayout_2.addWidget(self.edtPolicyBegDate)
        self.lblPolicyEndDate = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPolicyEndDate.sizePolicy().hasHeightForWidth())
        self.lblPolicyEndDate.setSizePolicy(sizePolicy)
        self.lblPolicyEndDate.setObjectName(_fromUtf8("lblPolicyEndDate"))
        self.horizontalLayout_2.addWidget(self.lblPolicyEndDate)
        self.edtPolicyEndDate = CDateEdit(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtPolicyEndDate.sizePolicy().hasHeightForWidth())
        self.edtPolicyEndDate.setSizePolicy(sizePolicy)
        self.edtPolicyEndDate.setCalendarPopup(True)
        self.edtPolicyEndDate.setObjectName(_fromUtf8("edtPolicyEndDate"))
        self.horizontalLayout_2.addWidget(self.edtPolicyEndDate)
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem6)
        self.gridLayout.addLayout(self.horizontalLayout_2, 10, 5, 1, 8)
        self.cmbPolicyType = CRBComboBox(self.tabSearch)
        self.cmbPolicyType.setObjectName(_fromUtf8("cmbPolicyType"))
        self.gridLayout.addWidget(self.cmbPolicyType, 8, 2, 1, 1)
        self.lblDocument = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblDocument.sizePolicy().hasHeightForWidth())
        self.lblDocument.setSizePolicy(sizePolicy)
        self.lblDocument.setObjectName(_fromUtf8("lblDocument"))
        self.gridLayout.addWidget(self.lblDocument, 7, 0, 1, 1)
        self.edtClientId = CLineEdit(self.tabSearch)
        self.edtClientId.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtClientId.sizePolicy().hasHeightForWidth())
        self.edtClientId.setSizePolicy(sizePolicy)
        self.edtClientId.setMaxLength(16)
        self.edtClientId.setPlaceholderText(_fromUtf8(""))
        self.edtClientId.setObjectName(_fromUtf8("edtClientId"))
        self.gridLayout.addWidget(self.edtClientId, 5, 2, 1, 1)
        self.cmbDocType = CRBComboBox(self.tabSearch)
        self.cmbDocType.setObjectName(_fromUtf8("cmbDocType"))
        self.gridLayout.addWidget(self.cmbDocType, 7, 2, 1, 1)
        self.lblBirthDate = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblBirthDate.sizePolicy().hasHeightForWidth())
        self.lblBirthDate.setSizePolicy(sizePolicy)
        self.lblBirthDate.setObjectName(_fromUtf8("lblBirthDate"))
        self.gridLayout.addWidget(self.lblBirthDate, 6, 0, 1, 1)
        self.edtBirthDate = CDateEdit(self.tabSearch)
        self.edtBirthDate.setCalendarPopup(True)
        self.edtBirthDate.setObjectName(_fromUtf8("edtBirthDate"))
        self.gridLayout.addWidget(self.edtBirthDate, 6, 2, 1, 1)
        self.lblSex = QtGui.QLabel(self.tabSearch)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout.addWidget(self.lblSex, 6, 10, 1, 1)
        self.cmbSex = QtGui.QComboBox(self.tabSearch)
        self.cmbSex.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSex.sizePolicy().hasHeightForWidth())
        self.cmbSex.setSizePolicy(sizePolicy)
        self.cmbSex.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbSex, 6, 11, 1, 1)
        self.tabWidget.addTab(self.tabSearch, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.lblPolicy.setBuddy(self.edtPolicySerial)
        self.lblFirstName.setBuddy(self.edtFirstName)
        self.lblCompulsoryPolisNumber.setBuddy(self.edtPolicyNumber)
        self.lblPolicyInsurer.setBuddy(self.cmbPolicyInsurer)
        self.lblPolicySerial.setBuddy(self.edtPolicySerial)
        self.lblLastName.setBuddy(self.edtLastName)
        self.lblPolicyBegDate.setBuddy(self.edtPolicyBegDate)

        self.retranslateUi(HospitalizationEventDialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(HospitalizationEventDialog)
        HospitalizationEventDialog.setTabOrder(self.edtLastName, self.edtFirstName)
        HospitalizationEventDialog.setTabOrder(self.edtFirstName, self.edtPatrName)
        HospitalizationEventDialog.setTabOrder(self.edtPatrName, self.edtClientId)
        HospitalizationEventDialog.setTabOrder(self.edtClientId, self.edtBirthDate)
        HospitalizationEventDialog.setTabOrder(self.edtBirthDate, self.cmbSex)
        HospitalizationEventDialog.setTabOrder(self.cmbSex, self.cmbDocType)
        HospitalizationEventDialog.setTabOrder(self.cmbDocType, self.edtLeftSerial)
        HospitalizationEventDialog.setTabOrder(self.edtLeftSerial, self.edtRightSerial)
        HospitalizationEventDialog.setTabOrder(self.edtRightSerial, self.edtNumber)
        HospitalizationEventDialog.setTabOrder(self.edtNumber, self.cmbPolicyType)
        HospitalizationEventDialog.setTabOrder(self.cmbPolicyType, self.edtPolicySerial)
        HospitalizationEventDialog.setTabOrder(self.edtPolicySerial, self.edtPolicyNumber)
        HospitalizationEventDialog.setTabOrder(self.edtPolicyNumber, self.cmbPolicyInsurer)
        HospitalizationEventDialog.setTabOrder(self.cmbPolicyInsurer, self.edtPolicyBegDate)
        HospitalizationEventDialog.setTabOrder(self.edtPolicyBegDate, self.edtPolicyEndDate)
        HospitalizationEventDialog.setTabOrder(self.edtPolicyEndDate, self.edtContact)
        HospitalizationEventDialog.setTabOrder(self.edtContact, self.btnApply)
        HospitalizationEventDialog.setTabOrder(self.btnApply, self.btnReset)
        HospitalizationEventDialog.setTabOrder(self.btnReset, self.readEpoms)
        HospitalizationEventDialog.setTabOrder(self.readEpoms, self.btnReadOMSBarcode)
        HospitalizationEventDialog.setTabOrder(self.btnReadOMSBarcode, self.btnRegistry)
        HospitalizationEventDialog.setTabOrder(self.btnRegistry, self.btnCommit)
        HospitalizationEventDialog.setTabOrder(self.btnCommit, self.tabWidget)
        HospitalizationEventDialog.setTabOrder(self.tabWidget, self.tblHospitalizationEvent)

    def retranslateUi(self, HospitalizationEventDialog):
        HospitalizationEventDialog.setWindowTitle(_translate("HospitalizationEventDialog", "Госпитализация", None))
        self.btnCommit.setText(_translate("HospitalizationEventDialog", "Госпитализировать (Пробел)", None))
        self.btnRegistry.setText(_translate("HospitalizationEventDialog", "Регистрация (F9)", None))
        self.btnRegistry.setShortcut(_translate("HospitalizationEventDialog", "F9", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabHospitalizationEvent), _translate("HospitalizationEventDialog", "Результат поиска", None))
        self.lblPolicy.setText(_translate("HospitalizationEventDialog", "Полис", None))
        self.lblClientId.setText(_translate("HospitalizationEventDialog", "Код пациента", None))
        self.lblContact.setText(_translate("HospitalizationEventDialog", "Контакт", None))
        self.lblNumber.setText(_translate("HospitalizationEventDialog", "Номер", None))
        self.lblSerial.setText(_translate("HospitalizationEventDialog", "Серия", None))
        self.lblPatrName.setText(_translate("HospitalizationEventDialog", "Отчество", None))
        self.lblFirstName.setText(_translate("HospitalizationEventDialog", "Имя", None))
        self.lblCompulsoryPolisNumber.setText(_translate("HospitalizationEventDialog", "Номер", None))
        self.lblPolicyInsurer.setText(_translate("HospitalizationEventDialog", "СМО", None))
        self.readEpoms.setText(_translate("HospitalizationEventDialog", "Считать данные с ЭПОМС", None))
        self.btnReadOMSBarcode.setText(_translate("HospitalizationEventDialog", "Считать данные полиса", None))
        self.btnApply.setText(_translate("HospitalizationEventDialog", "Искать", None))
        self.btnReset.setText(_translate("HospitalizationEventDialog", "Сбросить", None))
        self.lblPolicySerial.setText(_translate("HospitalizationEventDialog", "Серия", None))
        self.lblLastName.setText(_translate("HospitalizationEventDialog", "Фамилия", None))
        self.lblPolicyBegDate.setText(_translate("HospitalizationEventDialog", "Действителен с", None))
        self.lblPolicyEndDate.setText(_translate("HospitalizationEventDialog", "по", None))
        self.lblDocument.setText(_translate("HospitalizationEventDialog", "Документ", None))
        self.edtClientId.setToolTip(_translate("HospitalizationEventDialog", "Код пациента в выбранной учетной системе", None))
        self.lblBirthDate.setText(_translate("HospitalizationEventDialog", "Дата рождения", None))
        self.edtBirthDate.setDisplayFormat(_translate("HospitalizationEventDialog", "dd.MM.yyyy", None))
        self.lblSex.setText(_translate("HospitalizationEventDialog", "Пол", None))
        self.cmbSex.setItemText(1, _translate("HospitalizationEventDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("HospitalizationEventDialog", "Ж", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSearch), _translate("HospitalizationEventDialog", "&Поиск", None))

from Orgs.OrgComboBox import CInsurerComboBox
from Registry.PolicySerialEdit import CPolicySerialEdit
from Registry.RegistryTable import CClientsTableView
from library.DateEdit import CDateEdit
from library.LineEdit import CLineEdit
from library.crbcombobox import CRBComboBox
