# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ProbeWorkListPage.ui'
#
# Created: Mon Dec  7 18:54:23 2015
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

class Ui_ProbeWorkListWidget(object):
    def setupUi(self, ProbeWorkListWidget):
        ProbeWorkListWidget.setObjectName(_fromUtf8("ProbeWorkListWidget"))
        ProbeWorkListWidget.resize(857, 887)
        self.gridLayout_4 = QtGui.QGridLayout(ProbeWorkListWidget)
        self.gridLayout_4.setMargin(4)
        self.gridLayout_4.setSpacing(4)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.splitter_2 = QtGui.QSplitter(ProbeWorkListWidget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setChildrenCollapsible(False)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.grpFilter = QtGui.QGroupBox(self.splitter_2)
        self.grpFilter.setObjectName(_fromUtf8("grpFilter"))
        self.gridLayout_2 = QtGui.QGridLayout(self.grpFilter)
        self.gridLayout_2.setMargin(2)
        self.gridLayout_2.setSpacing(2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.cmbPWLEquipment = CRBComboBox(self.grpFilter)
        self.cmbPWLEquipment.setObjectName(_fromUtf8("cmbPWLEquipment"))
        self.gridLayout_2.addWidget(self.cmbPWLEquipment, 6, 0, 1, 2)
        self.lblPWLTestGroup = QtGui.QLabel(self.grpFilter)
        self.lblPWLTestGroup.setObjectName(_fromUtf8("lblPWLTestGroup"))
        self.gridLayout_2.addWidget(self.lblPWLTestGroup, 9, 0, 1, 2)
        self.buttonBoxPWL = CApplyResetDialogButtonBox(self.grpFilter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBoxPWL.sizePolicy().hasHeightForWidth())
        self.buttonBoxPWL.setSizePolicy(sizePolicy)
        self.buttonBoxPWL.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBoxPWL.setObjectName(_fromUtf8("buttonBoxPWL"))
        self.gridLayout_2.addWidget(self.buttonBoxPWL, 30, 1, 1, 1)
        self.cmbPWLTestGroup = CRBComboBox(self.grpFilter)
        self.cmbPWLTestGroup.setObjectName(_fromUtf8("cmbPWLTestGroup"))
        self.gridLayout_2.addWidget(self.cmbPWLTestGroup, 10, 0, 1, 2)
        self.pnlDates = QtGui.QWidget(self.grpFilter)
        self.pnlDates.setObjectName(_fromUtf8("pnlDates"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.pnlDates)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblDateFrom = QtGui.QLabel(self.pnlDates)
        self.lblDateFrom.setObjectName(_fromUtf8("lblDateFrom"))
        self.horizontalLayout.addWidget(self.lblDateFrom)
        self.edtPWLDateFrom = CDateEdit(self.pnlDates)
        self.edtPWLDateFrom.setObjectName(_fromUtf8("edtPWLDateFrom"))
        self.horizontalLayout.addWidget(self.edtPWLDateFrom)
        self.lblDateTo = QtGui.QLabel(self.pnlDates)
        self.lblDateTo.setObjectName(_fromUtf8("lblDateTo"))
        self.horizontalLayout.addWidget(self.lblDateTo)
        self.edtPWLDateTo = CDateEdit(self.pnlDates)
        self.edtPWLDateTo.setObjectName(_fromUtf8("edtPWLDateTo"))
        self.horizontalLayout.addWidget(self.edtPWLDateTo)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout_2.addWidget(self.pnlDates, 27, 0, 1, 2)
        self.cmbPWLStatus = QtGui.QComboBox(self.grpFilter)
        self.cmbPWLStatus.setObjectName(_fromUtf8("cmbPWLStatus"))
        self.cmbPWLStatus.addItem(_fromUtf8(""))
        self.cmbPWLStatus.addItem(_fromUtf8(""))
        self.cmbPWLStatus.addItem(_fromUtf8(""))
        self.cmbPWLStatus.addItem(_fromUtf8(""))
        self.cmbPWLStatus.addItem(_fromUtf8(""))
        self.cmbPWLStatus.addItem(_fromUtf8(""))
        self.cmbPWLStatus.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.cmbPWLStatus, 14, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 29, 0, 1, 2)
        self.grpClient = QtGui.QGroupBox(self.grpFilter)
        self.grpClient.setCheckable(True)
        self.grpClient.setChecked(False)
        self.grpClient.setObjectName(_fromUtf8("grpClient"))
        self.gridLayout_5 = QtGui.QGridLayout(self.grpClient)
        self.gridLayout_5.setMargin(2)
        self.gridLayout_5.setSpacing(2)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.chkPWLId = QtGui.QCheckBox(self.grpClient)
        self.chkPWLId.setObjectName(_fromUtf8("chkPWLId"))
        self.gridLayout_5.addWidget(self.chkPWLId, 0, 0, 1, 1)
        self.cmbPWLAccountingSystem = CRBComboBox(self.grpClient)
        self.cmbPWLAccountingSystem.setEnabled(False)
        self.cmbPWLAccountingSystem.setObjectName(_fromUtf8("cmbPWLAccountingSystem"))
        self.gridLayout_5.addWidget(self.cmbPWLAccountingSystem, 0, 1, 1, 2)
        self.edtPWLId = QtGui.QLineEdit(self.grpClient)
        self.edtPWLId.setEnabled(False)
        self.edtPWLId.setInputMask(_fromUtf8(""))
        self.edtPWLId.setMaxLength(32767)
        self.edtPWLId.setObjectName(_fromUtf8("edtPWLId"))
        self.gridLayout_5.addWidget(self.edtPWLId, 1, 0, 1, 3)
        self.chkPWLLastName = QtGui.QCheckBox(self.grpClient)
        self.chkPWLLastName.setObjectName(_fromUtf8("chkPWLLastName"))
        self.gridLayout_5.addWidget(self.chkPWLLastName, 2, 0, 1, 1)
        self.edtPWLLastName = QtGui.QLineEdit(self.grpClient)
        self.edtPWLLastName.setEnabled(False)
        self.edtPWLLastName.setObjectName(_fromUtf8("edtPWLLastName"))
        self.gridLayout_5.addWidget(self.edtPWLLastName, 2, 1, 1, 2)
        self.chkPWLFirstName = QtGui.QCheckBox(self.grpClient)
        self.chkPWLFirstName.setObjectName(_fromUtf8("chkPWLFirstName"))
        self.gridLayout_5.addWidget(self.chkPWLFirstName, 3, 0, 1, 1)
        self.edtPWLFirstName = QtGui.QLineEdit(self.grpClient)
        self.edtPWLFirstName.setEnabled(False)
        self.edtPWLFirstName.setObjectName(_fromUtf8("edtPWLFirstName"))
        self.gridLayout_5.addWidget(self.edtPWLFirstName, 3, 1, 1, 2)
        self.chkPWLPatrName = QtGui.QCheckBox(self.grpClient)
        self.chkPWLPatrName.setObjectName(_fromUtf8("chkPWLPatrName"))
        self.gridLayout_5.addWidget(self.chkPWLPatrName, 4, 0, 1, 1)
        self.edtPWLPatrName = QtGui.QLineEdit(self.grpClient)
        self.edtPWLPatrName.setEnabled(False)
        self.edtPWLPatrName.setObjectName(_fromUtf8("edtPWLPatrName"))
        self.gridLayout_5.addWidget(self.edtPWLPatrName, 4, 1, 1, 2)
        self.chkPWLBirthDay = QtGui.QCheckBox(self.grpClient)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkPWLBirthDay.sizePolicy().hasHeightForWidth())
        self.chkPWLBirthDay.setSizePolicy(sizePolicy)
        self.chkPWLBirthDay.setObjectName(_fromUtf8("chkPWLBirthDay"))
        self.gridLayout_5.addWidget(self.chkPWLBirthDay, 5, 0, 1, 1)
        self.edtPWLBirthDay = CDateEdit(self.grpClient)
        self.edtPWLBirthDay.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtPWLBirthDay.sizePolicy().hasHeightForWidth())
        self.edtPWLBirthDay.setSizePolicy(sizePolicy)
        self.edtPWLBirthDay.setCalendarPopup(True)
        self.edtPWLBirthDay.setObjectName(_fromUtf8("edtPWLBirthDay"))
        self.gridLayout_5.addWidget(self.edtPWLBirthDay, 5, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(86, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem2, 5, 2, 1, 1)
        self.gridLayout_2.addWidget(self.grpClient, 28, 0, 1, 2)
        self.lblPWLContainerType = QtGui.QLabel(self.grpFilter)
        self.lblPWLContainerType.setObjectName(_fromUtf8("lblPWLContainerType"))
        self.gridLayout_2.addWidget(self.lblPWLContainerType, 17, 0, 1, 2)
        self.cmbPWLContainerType = CRBComboBox(self.grpFilter)
        self.cmbPWLContainerType.setObjectName(_fromUtf8("cmbPWLContainerType"))
        self.gridLayout_2.addWidget(self.cmbPWLContainerType, 18, 0, 1, 2)
        self.cmbPWLPerson = CPersonComboBoxEx(self.grpFilter)
        self.cmbPWLPerson.setObjectName(_fromUtf8("cmbPWLPerson"))
        self.gridLayout_2.addWidget(self.cmbPWLPerson, 20, 0, 1, 2)
        self.cmbPWLTest = CRBComboBox(self.grpFilter)
        self.cmbPWLTest.setObjectName(_fromUtf8("cmbPWLTest"))
        self.gridLayout_2.addWidget(self.cmbPWLTest, 12, 0, 1, 2)
        self.lblPWLTissueType = QtGui.QLabel(self.grpFilter)
        self.lblPWLTissueType.setObjectName(_fromUtf8("lblPWLTissueType"))
        self.gridLayout_2.addWidget(self.lblPWLTissueType, 15, 0, 1, 2)
        self.cmbPWLTissueType = CRBComboBox(self.grpFilter)
        self.cmbPWLTissueType.setObjectName(_fromUtf8("cmbPWLTissueType"))
        self.gridLayout_2.addWidget(self.cmbPWLTissueType, 16, 0, 1, 2)
        self.cmbPWLRelegateOrg = COrgComboBox(self.grpFilter)
        self.cmbPWLRelegateOrg.setEnabled(False)
        self.cmbPWLRelegateOrg.setObjectName(_fromUtf8("cmbPWLRelegateOrg"))
        self.gridLayout_2.addWidget(self.cmbPWLRelegateOrg, 4, 0, 1, 2)
        self.chkPWLRelegateOrg = QtGui.QCheckBox(self.grpFilter)
        self.chkPWLRelegateOrg.setObjectName(_fromUtf8("chkPWLRelegateOrg"))
        self.gridLayout_2.addWidget(self.chkPWLRelegateOrg, 2, 0, 1, 2)
        self.lblPWLProbeIdentifier = QtGui.QLabel(self.grpFilter)
        self.lblPWLProbeIdentifier.setObjectName(_fromUtf8("lblPWLProbeIdentifier"))
        self.gridLayout_2.addWidget(self.lblPWLProbeIdentifier, 23, 0, 1, 2)
        self.edtPWLProbeIdentifier = QtGui.QLineEdit(self.grpFilter)
        self.edtPWLProbeIdentifier.setObjectName(_fromUtf8("edtPWLProbeIdentifier"))
        self.gridLayout_2.addWidget(self.edtPWLProbeIdentifier, 24, 0, 1, 2)
        self.lblPWLIbm = QtGui.QLabel(self.grpFilter)
        self.lblPWLIbm.setObjectName(_fromUtf8("lblPWLIbm"))
        self.gridLayout_2.addWidget(self.lblPWLIbm, 21, 0, 1, 2)
        self.lblPWLPerson = QtGui.QLabel(self.grpFilter)
        self.lblPWLPerson.setObjectName(_fromUtf8("lblPWLPerson"))
        self.gridLayout_2.addWidget(self.lblPWLPerson, 19, 0, 1, 2)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 30, 0, 1, 1)
        self.lblPWLTripod = QtGui.QLabel(self.grpFilter)
        self.lblPWLTripod.setObjectName(_fromUtf8("lblPWLTripod"))
        self.gridLayout_2.addWidget(self.lblPWLTripod, 7, 0, 1, 2)
        self.edtPWLTripodNumber = QtGui.QLineEdit(self.grpFilter)
        self.edtPWLTripodNumber.setObjectName(_fromUtf8("edtPWLTripodNumber"))
        self.gridLayout_2.addWidget(self.edtPWLTripodNumber, 8, 0, 1, 2)
        self.lblPWLOrganisation = QtGui.QLabel(self.grpFilter)
        self.lblPWLOrganisation.setObjectName(_fromUtf8("lblPWLOrganisation"))
        self.gridLayout_2.addWidget(self.lblPWLOrganisation, 0, 0, 1, 2)
        self.lblPWLEquipment = QtGui.QLabel(self.grpFilter)
        self.lblPWLEquipment.setObjectName(_fromUtf8("lblPWLEquipment"))
        self.gridLayout_2.addWidget(self.lblPWLEquipment, 5, 0, 1, 2)
        self.lblPWLStatus = QtGui.QLabel(self.grpFilter)
        self.lblPWLStatus.setObjectName(_fromUtf8("lblPWLStatus"))
        self.gridLayout_2.addWidget(self.lblPWLStatus, 13, 0, 1, 2)
        self.lblPWLTest = QtGui.QLabel(self.grpFilter)
        self.lblPWLTest.setObjectName(_fromUtf8("lblPWLTest"))
        self.gridLayout_2.addWidget(self.lblPWLTest, 11, 0, 1, 2)
        self.edtPWLIbm = QtGui.QLineEdit(self.grpFilter)
        self.edtPWLIbm.setObjectName(_fromUtf8("edtPWLIbm"))
        self.gridLayout_2.addWidget(self.edtPWLIbm, 22, 0, 1, 2)
        self.chkPWLIsUrgent = QtGui.QCheckBox(self.grpFilter)
        self.chkPWLIsUrgent.setObjectName(_fromUtf8("chkPWLIsUrgent"))
        self.gridLayout_2.addWidget(self.chkPWLIsUrgent, 25, 0, 1, 2)
        self.cmbPWLOrgStructure = COrgStructureComboBox(self.grpFilter)
        self.cmbPWLOrgStructure.setObjectName(_fromUtf8("cmbPWLOrgStructure"))
        self.gridLayout_2.addWidget(self.cmbPWLOrgStructure, 1, 0, 1, 2)
        self.pnlPWLProbes = QtGui.QWidget(self.splitter_2)
        self.pnlPWLProbes.setObjectName(_fromUtf8("pnlPWLProbes"))
        self.gridLayout_3 = QtGui.QGridLayout(self.pnlPWLProbes)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setSpacing(4)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tabWidgetPWL = QtGui.QTabWidget(self.pnlPWLProbes)
        self.tabWidgetPWL.setObjectName(_fromUtf8("tabWidgetPWL"))
        self.tabPWLProbes = QtGui.QWidget()
        self.tabPWLProbes.setObjectName(_fromUtf8("tabPWLProbes"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tabPWLProbes)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setMargin(4)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.splitter = QtGui.QSplitter(self.tabPWLProbes)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.pnlPWLOnlyProbes = QtGui.QWidget(self.splitter)
        self.pnlPWLOnlyProbes.setObjectName(_fromUtf8("pnlPWLOnlyProbes"))
        self.verticalLayout = QtGui.QVBoxLayout(self.pnlPWLOnlyProbes)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tblPWLOnlyProbes = CTableView(self.pnlPWLOnlyProbes)
        self.tblPWLOnlyProbes.setObjectName(_fromUtf8("tblPWLOnlyProbes"))
        self.verticalLayout.addWidget(self.tblPWLOnlyProbes)
        self.lblOnlyProbesCount = QtGui.QLabel(self.pnlPWLOnlyProbes)
        self.lblOnlyProbesCount.setObjectName(_fromUtf8("lblOnlyProbesCount"))
        self.verticalLayout.addWidget(self.lblOnlyProbesCount)
        self.pnlPWLOnlyTests = QtGui.QWidget(self.splitter)
        self.pnlPWLOnlyTests.setObjectName(_fromUtf8("pnlPWLOnlyTests"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.pnlPWLOnlyTests)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tblPWLOnlyTests = CSamplePreparationView(self.pnlPWLOnlyTests)
        self.tblPWLOnlyTests.setObjectName(_fromUtf8("tblPWLOnlyTests"))
        self.verticalLayout_2.addWidget(self.tblPWLOnlyTests)
        self.lblOnlyTestsCount = QtGui.QLabel(self.pnlPWLOnlyTests)
        self.lblOnlyTestsCount.setObjectName(_fromUtf8("lblOnlyTestsCount"))
        self.verticalLayout_2.addWidget(self.lblOnlyTestsCount)
        self.verticalLayout_3.addWidget(self.splitter)
        self.tabWidgetPWL.addTab(self.tabPWLProbes, _fromUtf8(""))
        self.tabPWLTests = QtGui.QWidget()
        self.tabPWLTests.setObjectName(_fromUtf8("tabPWLTests"))
        self.gridLayout = QtGui.QGridLayout(self.tabPWLTests)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblPWLProbe = CSamplePreparationView(self.tabPWLTests)
        self.tblPWLProbe.setObjectName(_fromUtf8("tblPWLProbe"))
        self.gridLayout.addWidget(self.tblPWLProbe, 0, 0, 1, 1)
        self.lblProbeCount = QtGui.QLabel(self.tabPWLTests)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblProbeCount.sizePolicy().hasHeightForWidth())
        self.lblProbeCount.setSizePolicy(sizePolicy)
        self.lblProbeCount.setObjectName(_fromUtf8("lblProbeCount"))
        self.gridLayout.addWidget(self.lblProbeCount, 1, 0, 1, 1)
        self.tabWidgetPWL.addTab(self.tabPWLTests, _fromUtf8(""))
        self.gridLayout_3.addWidget(self.tabWidgetPWL, 0, 0, 1, 6)
        self.btnPWLExport = QtGui.QPushButton(self.pnlPWLProbes)
        self.btnPWLExport.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnPWLExport.sizePolicy().hasHeightForWidth())
        self.btnPWLExport.setSizePolicy(sizePolicy)
        self.btnPWLExport.setObjectName(_fromUtf8("btnPWLExport"))
        self.gridLayout_3.addWidget(self.btnPWLExport, 2, 2, 1, 1)
        self.btnPWLImport = QtGui.QPushButton(self.pnlPWLProbes)
        self.btnPWLImport.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnPWLImport.sizePolicy().hasHeightForWidth())
        self.btnPWLImport.setSizePolicy(sizePolicy)
        self.btnPWLImport.setObjectName(_fromUtf8("btnPWLImport"))
        self.gridLayout_3.addWidget(self.btnPWLImport, 2, 3, 1, 1)
        self.btnPWLPrint = QtGui.QPushButton(self.pnlPWLProbes)
        self.btnPWLPrint.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnPWLPrint.sizePolicy().hasHeightForWidth())
        self.btnPWLPrint.setSizePolicy(sizePolicy)
        self.btnPWLPrint.setObjectName(_fromUtf8("btnPWLPrint"))
        self.gridLayout_3.addWidget(self.btnPWLPrint, 2, 4, 1, 1)
        self.btnRegistration = QtGui.QPushButton(self.pnlPWLProbes)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRegistration.sizePolicy().hasHeightForWidth())
        self.btnRegistration.setSizePolicy(sizePolicy)
        self.btnRegistration.setObjectName(_fromUtf8("btnRegistration"))
        self.gridLayout_3.addWidget(self.btnRegistration, 2, 5, 1, 1)
        self.btnPWLTripod = QtGui.QPushButton(self.pnlPWLProbes)
        self.btnPWLTripod.setObjectName(_fromUtf8("btnPWLTripod"))
        self.gridLayout_3.addWidget(self.btnPWLTripod, 2, 1, 1, 1)
        self.gridLayout_4.addWidget(self.splitter_2, 0, 0, 1, 1)

        self.retranslateUi(ProbeWorkListWidget)
        self.tabWidgetPWL.setCurrentIndex(0)
        QtCore.QObject.connect(self.chkPWLRelegateOrg, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbPWLRelegateOrg.setEnabled)
        QtCore.QObject.connect(self.chkPWLId, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbPWLAccountingSystem.setEnabled)
        QtCore.QObject.connect(self.chkPWLId, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtPWLId.setEnabled)
        QtCore.QObject.connect(self.chkPWLLastName, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtPWLLastName.setEnabled)
        QtCore.QObject.connect(self.chkPWLFirstName, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtPWLFirstName.setEnabled)
        QtCore.QObject.connect(self.chkPWLPatrName, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtPWLPatrName.setEnabled)
        QtCore.QObject.connect(self.chkPWLBirthDay, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtPWLBirthDay.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ProbeWorkListWidget)
        ProbeWorkListWidget.setTabOrder(self.chkPWLRelegateOrg, self.cmbPWLRelegateOrg)
        ProbeWorkListWidget.setTabOrder(self.cmbPWLRelegateOrg, self.cmbPWLEquipment)
        ProbeWorkListWidget.setTabOrder(self.cmbPWLEquipment, self.edtPWLTripodNumber)
        ProbeWorkListWidget.setTabOrder(self.edtPWLTripodNumber, self.cmbPWLTestGroup)
        ProbeWorkListWidget.setTabOrder(self.cmbPWLTestGroup, self.cmbPWLTest)
        ProbeWorkListWidget.setTabOrder(self.cmbPWLTest, self.cmbPWLStatus)
        ProbeWorkListWidget.setTabOrder(self.cmbPWLStatus, self.cmbPWLTissueType)
        ProbeWorkListWidget.setTabOrder(self.cmbPWLTissueType, self.cmbPWLContainerType)
        ProbeWorkListWidget.setTabOrder(self.cmbPWLContainerType, self.cmbPWLPerson)
        ProbeWorkListWidget.setTabOrder(self.cmbPWLPerson, self.edtPWLIbm)
        ProbeWorkListWidget.setTabOrder(self.edtPWLIbm, self.edtPWLProbeIdentifier)
        ProbeWorkListWidget.setTabOrder(self.edtPWLProbeIdentifier, self.chkPWLIsUrgent)
        ProbeWorkListWidget.setTabOrder(self.chkPWLIsUrgent, self.edtPWLDateFrom)
        ProbeWorkListWidget.setTabOrder(self.edtPWLDateFrom, self.edtPWLDateTo)
        ProbeWorkListWidget.setTabOrder(self.edtPWLDateTo, self.grpClient)
        ProbeWorkListWidget.setTabOrder(self.grpClient, self.chkPWLId)
        ProbeWorkListWidget.setTabOrder(self.chkPWLId, self.cmbPWLAccountingSystem)
        ProbeWorkListWidget.setTabOrder(self.cmbPWLAccountingSystem, self.edtPWLId)
        ProbeWorkListWidget.setTabOrder(self.edtPWLId, self.chkPWLLastName)
        ProbeWorkListWidget.setTabOrder(self.chkPWLLastName, self.edtPWLLastName)
        ProbeWorkListWidget.setTabOrder(self.edtPWLLastName, self.chkPWLFirstName)
        ProbeWorkListWidget.setTabOrder(self.chkPWLFirstName, self.edtPWLFirstName)
        ProbeWorkListWidget.setTabOrder(self.edtPWLFirstName, self.chkPWLPatrName)
        ProbeWorkListWidget.setTabOrder(self.chkPWLPatrName, self.edtPWLPatrName)
        ProbeWorkListWidget.setTabOrder(self.edtPWLPatrName, self.chkPWLBirthDay)
        ProbeWorkListWidget.setTabOrder(self.chkPWLBirthDay, self.edtPWLBirthDay)
        ProbeWorkListWidget.setTabOrder(self.edtPWLBirthDay, self.buttonBoxPWL)
        ProbeWorkListWidget.setTabOrder(self.buttonBoxPWL, self.tabWidgetPWL)
        ProbeWorkListWidget.setTabOrder(self.tabWidgetPWL, self.tblPWLOnlyProbes)
        ProbeWorkListWidget.setTabOrder(self.tblPWLOnlyProbes, self.tblPWLOnlyTests)
        ProbeWorkListWidget.setTabOrder(self.tblPWLOnlyTests, self.tblPWLProbe)
        ProbeWorkListWidget.setTabOrder(self.tblPWLProbe, self.btnPWLTripod)
        ProbeWorkListWidget.setTabOrder(self.btnPWLTripod, self.btnPWLExport)
        ProbeWorkListWidget.setTabOrder(self.btnPWLExport, self.btnPWLImport)
        ProbeWorkListWidget.setTabOrder(self.btnPWLImport, self.btnPWLPrint)
        ProbeWorkListWidget.setTabOrder(self.btnPWLPrint, self.btnRegistration)

    def retranslateUi(self, ProbeWorkListWidget):
        ProbeWorkListWidget.setWindowTitle(_translate("ProbeWorkListWidget", "Form", None))
        self.grpFilter.setTitle(_translate("ProbeWorkListWidget", "Фильтр", None))
        self.lblPWLTestGroup.setText(_translate("ProbeWorkListWidget", "Группа", None))
        self.lblDateFrom.setText(_translate("ProbeWorkListWidget", "C", None))
        self.lblDateTo.setText(_translate("ProbeWorkListWidget", "по", None))
        self.cmbPWLStatus.setItemText(0, _translate("ProbeWorkListWidget", "-", None))
        self.cmbPWLStatus.setItemText(1, _translate("ProbeWorkListWidget", "Без пробы", None))
        self.cmbPWLStatus.setItemText(2, _translate("ProbeWorkListWidget", "Ожидание", None))
        self.cmbPWLStatus.setItemText(3, _translate("ProbeWorkListWidget", "В работе", None))
        self.cmbPWLStatus.setItemText(4, _translate("ProbeWorkListWidget", "Закончено", None))
        self.cmbPWLStatus.setItemText(5, _translate("ProbeWorkListWidget", "Без результата", None))
        self.cmbPWLStatus.setItemText(6, _translate("ProbeWorkListWidget", "Назначено", None))
        self.grpClient.setTitle(_translate("ProbeWorkListWidget", "Пациент", None))
        self.chkPWLId.setText(_translate("ProbeWorkListWidget", "Код", None))
        self.chkPWLLastName.setText(_translate("ProbeWorkListWidget", "Фамилия", None))
        self.chkPWLFirstName.setText(_translate("ProbeWorkListWidget", "Имя", None))
        self.chkPWLPatrName.setText(_translate("ProbeWorkListWidget", "Отчество", None))
        self.chkPWLBirthDay.setText(_translate("ProbeWorkListWidget", "Дата рождения", None))
        self.lblPWLContainerType.setText(_translate("ProbeWorkListWidget", "Тип контейнера", None))
        self.lblPWLTissueType.setText(_translate("ProbeWorkListWidget", "Биоматериал", None))
        self.chkPWLRelegateOrg.setText(_translate("ProbeWorkListWidget", "Направитель", None))
        self.lblPWLProbeIdentifier.setText(_translate("ProbeWorkListWidget", "Идентификатор пробы", None))
        self.lblPWLIbm.setText(_translate("ProbeWorkListWidget", "ИБМ", None))
        self.lblPWLPerson.setText(_translate("ProbeWorkListWidget", "Исполнитель", None))
        self.lblPWLTripod.setText(_translate("ProbeWorkListWidget", "Штатив", None))
        self.lblPWLOrganisation.setText(_translate("ProbeWorkListWidget", "ЛПУ", None))
        self.lblPWLEquipment.setText(_translate("ProbeWorkListWidget", "Оборудование", None))
        self.lblPWLStatus.setText(_translate("ProbeWorkListWidget", "Статус", None))
        self.lblPWLTest.setText(_translate("ProbeWorkListWidget", "Тест", None))
        self.chkPWLIsUrgent.setText(_translate("ProbeWorkListWidget", "Срочный", None))
        self.lblOnlyProbesCount.setText(_translate("ProbeWorkListWidget", "Количество: 0", None))
        self.lblOnlyTestsCount.setText(_translate("ProbeWorkListWidget", "Количество: 0", None))
        self.tabWidgetPWL.setTabText(self.tabWidgetPWL.indexOf(self.tabPWLProbes), _translate("ProbeWorkListWidget", "&Пробы", None))
        self.lblProbeCount.setText(_translate("ProbeWorkListWidget", "Количество проб", None))
        self.tabWidgetPWL.setTabText(self.tabWidgetPWL.indexOf(self.tabPWLTests), _translate("ProbeWorkListWidget", "&Тесты", None))
        self.btnPWLExport.setText(_translate("ProbeWorkListWidget", "Экспорт", None))
        self.btnPWLImport.setText(_translate("ProbeWorkListWidget", "Импорт", None))
        self.btnPWLPrint.setText(_translate("ProbeWorkListWidget", "Печать", None))
        self.btnRegistration.setText(_translate("ProbeWorkListWidget", "Регистрация", None))
        self.btnPWLTripod.setText(_translate("ProbeWorkListWidget", "Штатив", None))

from Orgs.OrgComboBox import COrgComboBox
from library.crbcombobox import CRBComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DialogButtonBox import CApplyResetDialogButtonBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.TableView import CTableView
from TissueJournal.TissueJournalModels import CSamplePreparationView
from library.DateEdit import CDateEdit
