# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/hikarido/Documents/forge/VistaMad/s11/Orgs/OrgEditor.ui'
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

class Ui_OrgEditorDialog(object):
    def setupUi(self, OrgEditorDialog):
        OrgEditorDialog.setObjectName(_fromUtf8("OrgEditorDialog"))
        OrgEditorDialog.resize(717, 902)
        OrgEditorDialog.setSizeGripEnabled(False)
        self.gridlayout = QtGui.QGridLayout(OrgEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblShortName = QtGui.QLabel(OrgEditorDialog)
        self.lblShortName.setObjectName(_fromUtf8("lblShortName"))
        self.gridlayout.addWidget(self.lblShortName, 1, 0, 1, 1)
        self.edtTitle = QtGui.QLineEdit(OrgEditorDialog)
        self.edtTitle.setObjectName(_fromUtf8("edtTitle"))
        self.gridlayout.addWidget(self.edtTitle, 2, 1, 1, 1)
        self.lblTitle = QtGui.QLabel(OrgEditorDialog)
        self.lblTitle.setObjectName(_fromUtf8("lblTitle"))
        self.gridlayout.addWidget(self.lblTitle, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(OrgEditorDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        self.edtShortName = QtGui.QLineEdit(OrgEditorDialog)
        self.edtShortName.setObjectName(_fromUtf8("edtShortName"))
        self.gridlayout.addWidget(self.edtShortName, 1, 1, 1, 1)
        self.lblFullName = QtGui.QLabel(OrgEditorDialog)
        self.lblFullName.setObjectName(_fromUtf8("lblFullName"))
        self.gridlayout.addWidget(self.lblFullName, 0, 0, 1, 1)
        self.edtFullName = QtGui.QLineEdit(OrgEditorDialog)
        self.edtFullName.setObjectName(_fromUtf8("edtFullName"))
        self.gridlayout.addWidget(self.edtFullName, 0, 1, 1, 1)
        self.tabWidget = QtGui.QTabWidget(OrgEditorDialog)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabBaseInfo = QtGui.QWidget()
        self.tabBaseInfo.setObjectName(_fromUtf8("tabBaseInfo"))
        self.gridLayout = QtGui.QGridLayout(self.tabBaseInfo)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblChief = QtGui.QLabel(self.tabBaseInfo)
        self.lblChief.setObjectName(_fromUtf8("lblChief"))
        self.gridLayout.addWidget(self.lblChief, 9, 0, 1, 1)
        self.lblINN = QtGui.QLabel(self.tabBaseInfo)
        self.lblINN.setObjectName(_fromUtf8("lblINN"))
        self.gridLayout.addWidget(self.lblINN, 4, 0, 1, 1)
        self.lblCanOmitPolicyNumber = QtGui.QLabel(self.tabBaseInfo)
        self.lblCanOmitPolicyNumber.setObjectName(_fromUtf8("lblCanOmitPolicyNumber"))
        self.gridLayout.addWidget(self.lblCanOmitPolicyNumber, 16, 7, 1, 1)
        self.lblNotes = QtGui.QLabel(self.tabBaseInfo)
        self.lblNotes.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblNotes.setObjectName(_fromUtf8("lblNotes"))
        self.gridLayout.addWidget(self.lblNotes, 20, 0, 1, 1)
        self.edtOGRN = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtOGRN.setObjectName(_fromUtf8("edtOGRN"))
        self.gridLayout.addWidget(self.edtOGRN, 3, 2, 1, 1)
        self.lblInfisCode = QtGui.QLabel(self.tabBaseInfo)
        self.lblInfisCode.setScaledContents(False)
        self.lblInfisCode.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblInfisCode.setObjectName(_fromUtf8("lblInfisCode"))
        self.gridLayout.addWidget(self.lblInfisCode, 12, 5, 1, 1)
        self.lblOKATO = QtGui.QLabel(self.tabBaseInfo)
        self.lblOKATO.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblOKATO.setObjectName(_fromUtf8("lblOKATO"))
        self.gridLayout.addWidget(self.lblOKATO, 3, 5, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 19, 6, 1, 5)
        self.edtOKATO = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtOKATO.setObjectName(_fromUtf8("edtOKATO"))
        self.gridLayout.addWidget(self.edtOKATO, 3, 6, 1, 3)
        self.lblOKFS = QtGui.QLabel(self.tabBaseInfo)
        self.lblOKFS.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblOKFS.setObjectName(_fromUtf8("lblOKFS"))
        self.gridLayout.addWidget(self.lblOKFS, 5, 5, 1, 1)
        self.label = QtGui.QLabel(self.tabBaseInfo)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 6, 0, 1, 1)
        self.chkIsCompulsoryInsurer = QtGui.QCheckBox(self.tabBaseInfo)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkIsCompulsoryInsurer.sizePolicy().hasHeightForWidth())
        self.chkIsCompulsoryInsurer.setSizePolicy(sizePolicy)
        self.chkIsCompulsoryInsurer.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.chkIsCompulsoryInsurer.setObjectName(_fromUtf8("chkIsCompulsoryInsurer"))
        self.gridLayout.addWidget(self.chkIsCompulsoryInsurer, 16, 2, 1, 1)
        self.chkVoluntaryServiceStop = QtGui.QCheckBox(self.tabBaseInfo)
        self.chkVoluntaryServiceStop.setObjectName(_fromUtf8("chkVoluntaryServiceStop"))
        self.gridLayout.addWidget(self.chkVoluntaryServiceStop, 15, 10, 1, 1)
        self.edtAccountant = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtAccountant.setObjectName(_fromUtf8("edtAccountant"))
        self.gridLayout.addWidget(self.edtAccountant, 10, 2, 1, 9)
        self.lblKPP = QtGui.QLabel(self.tabBaseInfo)
        self.lblKPP.setObjectName(_fromUtf8("lblKPP"))
        self.gridLayout.addWidget(self.lblKPP, 5, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.tabBaseInfo)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 15, 7, 1, 1)
        self.lblAccountant = QtGui.QLabel(self.tabBaseInfo)
        self.lblAccountant.setObjectName(_fromUtf8("lblAccountant"))
        self.gridLayout.addWidget(self.lblAccountant, 10, 0, 1, 1)
        self.edtAddress = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtAddress.setEnabled(True)
        self.edtAddress.setObjectName(_fromUtf8("edtAddress"))
        self.gridLayout.addWidget(self.edtAddress, 0, 2, 1, 9)
        self.chkCanOmitPolicyNumber = QtGui.QCheckBox(self.tabBaseInfo)
        self.chkCanOmitPolicyNumber.setText(_fromUtf8(""))
        self.chkCanOmitPolicyNumber.setObjectName(_fromUtf8("chkCanOmitPolicyNumber"))
        self.gridLayout.addWidget(self.chkCanOmitPolicyNumber, 16, 9, 1, 1)
        self.chkCompulsoryServiceStop = QtGui.QCheckBox(self.tabBaseInfo)
        self.chkCompulsoryServiceStop.setObjectName(_fromUtf8("chkCompulsoryServiceStop"))
        self.gridLayout.addWidget(self.chkCompulsoryServiceStop, 15, 9, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(111, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 12, 9, 1, 2)
        self.lblHead = QtGui.QLabel(self.tabBaseInfo)
        self.lblHead.setObjectName(_fromUtf8("lblHead"))
        self.gridLayout.addWidget(self.lblHead, 2, 0, 1, 1)
        self.edtObsoleteInfisCode = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtObsoleteInfisCode.setObjectName(_fromUtf8("edtObsoleteInfisCode"))
        self.gridLayout.addWidget(self.edtObsoleteInfisCode, 13, 2, 1, 9)
        self.chkIsInsurer = QtGui.QCheckBox(self.tabBaseInfo)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkIsInsurer.sizePolicy().hasHeightForWidth())
        self.chkIsInsurer.setSizePolicy(sizePolicy)
        self.chkIsInsurer.setText(_fromUtf8(""))
        self.chkIsInsurer.setObjectName(_fromUtf8("chkIsInsurer"))
        self.gridLayout.addWidget(self.chkIsInsurer, 15, 2, 1, 1)
        self.edtPhone = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtPhone.setObjectName(_fromUtf8("edtPhone"))
        self.gridLayout.addWidget(self.edtPhone, 11, 2, 1, 9)
        self.cmbIsMedical = QtGui.QComboBox(self.tabBaseInfo)
        self.cmbIsMedical.setObjectName(_fromUtf8("cmbIsMedical"))
        self.cmbIsMedical.addItem(_fromUtf8(""))
        self.cmbIsMedical.addItem(_fromUtf8(""))
        self.cmbIsMedical.addItem(_fromUtf8(""))
        self.cmbIsMedical.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbIsMedical, 19, 2, 1, 4)
        self.edtInfisCode = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtInfisCode.setObjectName(_fromUtf8("edtInfisCode"))
        self.gridLayout.addWidget(self.edtInfisCode, 12, 6, 1, 3)
        self.edtNotes = QtGui.QTextEdit(self.tabBaseInfo)
        self.edtNotes.setObjectName(_fromUtf8("edtNotes"))
        self.gridLayout.addWidget(self.edtNotes, 20, 2, 1, 9)
        self.cmbHead = COrgComboBox(self.tabBaseInfo)
        self.cmbHead.setEnabled(True)
        self.cmbHead.setObjectName(_fromUtf8("cmbHead"))
        self.gridLayout.addWidget(self.cmbHead, 2, 2, 1, 8)
        self.cmbArea = CKLADRComboBox(self.tabBaseInfo)
        self.cmbArea.setEnabled(True)
        self.cmbArea.setObjectName(_fromUtf8("cmbArea"))
        self.gridLayout.addWidget(self.cmbArea, 18, 2, 1, 9)
        self.lblAddress = QtGui.QLabel(self.tabBaseInfo)
        self.lblAddress.setObjectName(_fromUtf8("lblAddress"))
        self.gridLayout.addWidget(self.lblAddress, 0, 0, 1, 1)
        self.cmbOKFS = CRBComboBox(self.tabBaseInfo)
        self.cmbOKFS.setObjectName(_fromUtf8("cmbOKFS"))
        self.gridLayout.addWidget(self.cmbOKFS, 5, 6, 1, 5)
        self.lblNet = QtGui.QLabel(self.tabBaseInfo)
        self.lblNet.setObjectName(_fromUtf8("lblNet"))
        self.gridLayout.addWidget(self.lblNet, 12, 0, 1, 1)
        self.edtMiacCode = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtMiacCode.setObjectName(_fromUtf8("edtMiacCode"))
        self.gridLayout.addWidget(self.edtMiacCode, 14, 2, 1, 4)
        self.lblOGRN = QtGui.QLabel(self.tabBaseInfo)
        self.lblOGRN.setObjectName(_fromUtf8("lblOGRN"))
        self.gridLayout.addWidget(self.lblOGRN, 3, 0, 1, 1)
        self.lblIsHospital = QtGui.QLabel(self.tabBaseInfo)
        self.lblIsHospital.setObjectName(_fromUtf8("lblIsHospital"))
        self.gridLayout.addWidget(self.lblIsHospital, 19, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(111, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 6, 9, 1, 2)
        self.edtOKPO = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtOKPO.setObjectName(_fromUtf8("edtOKPO"))
        self.gridLayout.addWidget(self.edtOKPO, 6, 6, 1, 3)
        self.cmbNet = CRBComboBox(self.tabBaseInfo)
        self.cmbNet.setObjectName(_fromUtf8("cmbNet"))
        self.gridLayout.addWidget(self.cmbNet, 12, 2, 1, 1)
        self.lblOKVED = QtGui.QLabel(self.tabBaseInfo)
        self.lblOKVED.setObjectName(_fromUtf8("lblOKVED"))
        self.gridLayout.addWidget(self.lblOKVED, 7, 0, 1, 1)
        self.lblMiacCode = QtGui.QLabel(self.tabBaseInfo)
        self.lblMiacCode.setObjectName(_fromUtf8("lblMiacCode"))
        self.gridLayout.addWidget(self.lblMiacCode, 14, 0, 1, 1)
        self.edtChief = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtChief.setObjectName(_fromUtf8("edtChief"))
        self.gridLayout.addWidget(self.edtChief, 9, 2, 1, 9)
        self.chkIsVoluntaryInsurer = QtGui.QCheckBox(self.tabBaseInfo)
        self.chkIsVoluntaryInsurer.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.chkIsVoluntaryInsurer.setObjectName(_fromUtf8("chkIsVoluntaryInsurer"))
        self.gridLayout.addWidget(self.chkIsVoluntaryInsurer, 17, 2, 1, 1)
        self.lblPhone = QtGui.QLabel(self.tabBaseInfo)
        self.lblPhone.setObjectName(_fromUtf8("lblPhone"))
        self.gridLayout.addWidget(self.lblPhone, 11, 0, 1, 1)
        self.edtFSS = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtFSS.setObjectName(_fromUtf8("edtFSS"))
        self.gridLayout.addWidget(self.edtFSS, 6, 2, 1, 1)
        self.lblIsInsurer = QtGui.QLabel(self.tabBaseInfo)
        self.lblIsInsurer.setObjectName(_fromUtf8("lblIsInsurer"))
        self.gridLayout.addWidget(self.lblIsInsurer, 15, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.tabBaseInfo)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 18, 0, 1, 1)
        self.edtOKVED = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtOKVED.setObjectName(_fromUtf8("edtOKVED"))
        self.gridLayout.addWidget(self.edtOKVED, 7, 2, 1, 1)
        self.lblOKPO = QtGui.QLabel(self.tabBaseInfo)
        self.lblOKPO.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblOKPO.setObjectName(_fromUtf8("lblOKPO"))
        self.gridLayout.addWidget(self.lblOKPO, 6, 5, 1, 1)
        self.lblOKPF = QtGui.QLabel(self.tabBaseInfo)
        self.lblOKPF.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblOKPF.setObjectName(_fromUtf8("lblOKPF"))
        self.gridLayout.addWidget(self.lblOKPF, 4, 5, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(111, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 3, 9, 1, 2)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 15, 4, 1, 2)
        self.lblObsoleteInfisCode = QtGui.QLabel(self.tabBaseInfo)
        self.lblObsoleteInfisCode.setObjectName(_fromUtf8("lblObsoleteInfisCode"))
        self.gridLayout.addWidget(self.lblObsoleteInfisCode, 13, 0, 1, 1)
        self.edtKPP = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtKPP.setObjectName(_fromUtf8("edtKPP"))
        self.gridLayout.addWidget(self.edtKPP, 5, 2, 1, 1)
        self.btnSelectHeadOrganisation = QtGui.QToolButton(self.tabBaseInfo)
        self.btnSelectHeadOrganisation.setEnabled(True)
        self.btnSelectHeadOrganisation.setObjectName(_fromUtf8("btnSelectHeadOrganisation"))
        self.gridLayout.addWidget(self.btnSelectHeadOrganisation, 2, 10, 1, 1)
        self.cmbOKPF = CRBComboBox(self.tabBaseInfo)
        self.cmbOKPF.setObjectName(_fromUtf8("cmbOKPF"))
        self.gridLayout.addWidget(self.cmbOKPF, 4, 6, 1, 5)
        self.edtINN = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtINN.setObjectName(_fromUtf8("edtINN"))
        self.gridLayout.addWidget(self.edtINN, 4, 2, 1, 1)
        self.lblNetricaCode = QtGui.QLabel(self.tabBaseInfo)
        self.lblNetricaCode.setObjectName(_fromUtf8("lblNetricaCode"))
        self.gridLayout.addWidget(self.lblNetricaCode, 7, 5, 1, 1)
        self.edtNetricaCode = QtGui.QLineEdit(self.tabBaseInfo)
        self.edtNetricaCode.setObjectName(_fromUtf8("edtNetricaCode"))
        self.gridLayout.addWidget(self.edtNetricaCode, 7, 6, 1, 5)
        self.tabWidget.addTab(self.tabBaseInfo, _fromUtf8(""))
        self.tabAccounts = QtGui.QWidget()
        self.tabAccounts.setObjectName(_fromUtf8("tabAccounts"))
        self.gridlayout1 = QtGui.QGridLayout(self.tabAccounts)
        self.gridlayout1.setMargin(4)
        self.gridlayout1.setSpacing(4)
        self.gridlayout1.setObjectName(_fromUtf8("gridlayout1"))
        self.tblOrganisationAccounts = CInDocTableView(self.tabAccounts)
        self.tblOrganisationAccounts.setObjectName(_fromUtf8("tblOrganisationAccounts"))
        self.gridlayout1.addWidget(self.tblOrganisationAccounts, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabAccounts, _fromUtf8(""))
        self.tabPolicySerials = QtGui.QWidget()
        self.tabPolicySerials.setObjectName(_fromUtf8("tabPolicySerials"))
        self.gridlayout2 = QtGui.QGridLayout(self.tabPolicySerials)
        self.gridlayout2.setMargin(4)
        self.gridlayout2.setSpacing(4)
        self.gridlayout2.setObjectName(_fromUtf8("gridlayout2"))
        self.tblOrganisationPolicySerials = CInDocTableView(self.tabPolicySerials)
        self.tblOrganisationPolicySerials.setObjectName(_fromUtf8("tblOrganisationPolicySerials"))
        self.gridlayout2.addWidget(self.tblOrganisationPolicySerials, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabPolicySerials, _fromUtf8(""))
        self.gridlayout.addWidget(self.tabWidget, 3, 0, 1, 2)
        self.lblShortName.setBuddy(self.edtShortName)
        self.lblTitle.setBuddy(self.edtTitle)
        self.lblFullName.setBuddy(self.edtFullName)
        self.lblChief.setBuddy(self.edtChief)
        self.lblINN.setBuddy(self.edtINN)
        self.lblNotes.setBuddy(self.edtNotes)
        self.lblInfisCode.setBuddy(self.edtInfisCode)
        self.lblOKATO.setBuddy(self.edtOKATO)
        self.lblOKFS.setBuddy(self.cmbOKFS)
        self.lblKPP.setBuddy(self.edtKPP)
        self.lblAccountant.setBuddy(self.edtAccountant)
        self.lblHead.setBuddy(self.cmbHead)
        self.lblAddress.setBuddy(self.edtAddress)
        self.lblNet.setBuddy(self.cmbNet)
        self.lblOGRN.setBuddy(self.edtOGRN)
        self.lblOKVED.setBuddy(self.edtOKVED)
        self.lblMiacCode.setBuddy(self.edtMiacCode)
        self.lblPhone.setBuddy(self.edtPhone)
        self.lblIsInsurer.setBuddy(self.chkIsInsurer)
        self.label_2.setBuddy(self.cmbArea)
        self.lblOKPO.setBuddy(self.edtOKPO)
        self.lblOKPF.setBuddy(self.cmbOKPF)
        self.lblObsoleteInfisCode.setBuddy(self.edtObsoleteInfisCode)

        self.retranslateUi(OrgEditorDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.chkIsInsurer, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkCompulsoryServiceStop.setEnabled)
        QtCore.QObject.connect(self.chkIsInsurer, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkVoluntaryServiceStop.setEnabled)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), OrgEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), OrgEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(OrgEditorDialog)
        OrgEditorDialog.setTabOrder(self.edtFullName, self.edtShortName)
        OrgEditorDialog.setTabOrder(self.edtShortName, self.edtTitle)
        OrgEditorDialog.setTabOrder(self.edtTitle, self.tabWidget)
        OrgEditorDialog.setTabOrder(self.tabWidget, self.edtAddress)
        OrgEditorDialog.setTabOrder(self.edtAddress, self.cmbHead)
        OrgEditorDialog.setTabOrder(self.cmbHead, self.btnSelectHeadOrganisation)
        OrgEditorDialog.setTabOrder(self.btnSelectHeadOrganisation, self.edtOGRN)
        OrgEditorDialog.setTabOrder(self.edtOGRN, self.edtINN)
        OrgEditorDialog.setTabOrder(self.edtINN, self.edtKPP)
        OrgEditorDialog.setTabOrder(self.edtKPP, self.edtFSS)
        OrgEditorDialog.setTabOrder(self.edtFSS, self.edtOKVED)
        OrgEditorDialog.setTabOrder(self.edtOKVED, self.edtOKATO)
        OrgEditorDialog.setTabOrder(self.edtOKATO, self.cmbOKFS)
        OrgEditorDialog.setTabOrder(self.cmbOKFS, self.edtOKPO)
        OrgEditorDialog.setTabOrder(self.edtOKPO, self.edtChief)
        OrgEditorDialog.setTabOrder(self.edtChief, self.edtAccountant)
        OrgEditorDialog.setTabOrder(self.edtAccountant, self.edtPhone)
        OrgEditorDialog.setTabOrder(self.edtPhone, self.cmbNet)
        OrgEditorDialog.setTabOrder(self.cmbNet, self.edtInfisCode)
        OrgEditorDialog.setTabOrder(self.edtInfisCode, self.edtObsoleteInfisCode)
        OrgEditorDialog.setTabOrder(self.edtObsoleteInfisCode, self.edtMiacCode)
        OrgEditorDialog.setTabOrder(self.edtMiacCode, self.chkIsInsurer)
        OrgEditorDialog.setTabOrder(self.chkIsInsurer, self.cmbArea)
        OrgEditorDialog.setTabOrder(self.cmbArea, self.cmbIsMedical)
        OrgEditorDialog.setTabOrder(self.cmbIsMedical, self.edtNotes)
        OrgEditorDialog.setTabOrder(self.edtNotes, self.tblOrganisationAccounts)
        OrgEditorDialog.setTabOrder(self.tblOrganisationAccounts, self.tblOrganisationPolicySerials)

    def retranslateUi(self, OrgEditorDialog):
        OrgEditorDialog.setWindowTitle(_translate("OrgEditorDialog", "ChangeMe!", None))
        self.lblShortName.setText(_translate("OrgEditorDialog", "&Наименование", None))
        self.lblTitle.setText(_translate("OrgEditorDialog", "Наименование для печати", None))
        self.lblFullName.setText(_translate("OrgEditorDialog", "&Полное наименование", None))
        self.lblChief.setText(_translate("OrgEditorDialog", "Руководитель", None))
        self.lblINN.setText(_translate("OrgEditorDialog", "ИНН", None))
        self.lblCanOmitPolicyNumber.setText(_translate("OrgEditorDialog", "Не требует ввода данных полиса:", None))
        self.lblNotes.setText(_translate("OrgEditorDialog", "Примечания", None))
        self.edtOGRN.setInputMask(_translate("OrgEditorDialog", "999999999999900; ", None))
        self.lblInfisCode.setToolTip(_translate("OrgEditorDialog", "Код в тер.фонде", None))
        self.lblInfisCode.setText(_translate("OrgEditorDialog", "ИНФИС", None))
        self.lblOKATO.setText(_translate("OrgEditorDialog", "ОКАТО", None))
        self.edtOKATO.setInputMask(_translate("OrgEditorDialog", "99999999999; ", None))
        self.lblOKFS.setText(_translate("OrgEditorDialog", "ОКФС", None))
        self.label.setText(_translate("OrgEditorDialog", "ФСС", None))
        self.chkIsCompulsoryInsurer.setText(_translate("OrgEditorDialog", "ОМС", None))
        self.chkVoluntaryServiceStop.setText(_translate("OrgEditorDialog", "ДМС", None))
        self.lblKPP.setText(_translate("OrgEditorDialog", "КПП", None))
        self.label_3.setText(_translate("OrgEditorDialog", "Приостановить обслуживание: ", None))
        self.lblAccountant.setText(_translate("OrgEditorDialog", "Гл.бухгалтер", None))
        self.chkCompulsoryServiceStop.setText(_translate("OrgEditorDialog", "ОМС", None))
        self.lblHead.setText(_translate("OrgEditorDialog", "&Головная организация", None))
        self.cmbIsMedical.setItemText(0, _translate("OrgEditorDialog", "не определено", None))
        self.cmbIsMedical.setItemText(1, _translate("OrgEditorDialog", "поликлиника", None))
        self.cmbIsMedical.setItemText(2, _translate("OrgEditorDialog", "стационар", None))
        self.cmbIsMedical.setItemText(3, _translate("OrgEditorDialog", "прочая мед.организация", None))
        self.edtInfisCode.setToolTip(_translate("OrgEditorDialog", "Код в тер.фонде", None))
        self.lblAddress.setText(_translate("OrgEditorDialog", "Адрес", None))
        self.lblNet.setText(_translate("OrgEditorDialog", "&Сеть", None))
        self.lblOGRN.setText(_translate("OrgEditorDialog", "ОГРН", None))
        self.lblIsHospital.setText(_translate("OrgEditorDialog", "ЛПУ", None))
        self.edtOKPO.setInputMask(_translate("OrgEditorDialog", "99999999; ", None))
        self.lblOKVED.setText(_translate("OrgEditorDialog", "ОКВЭД", None))
        self.lblMiacCode.setText(_translate("OrgEditorDialog", "Код &МИАЦ", None))
        self.chkIsVoluntaryInsurer.setText(_translate("OrgEditorDialog", "ДМС", None))
        self.lblPhone.setText(_translate("OrgEditorDialog", "Телефон", None))
        self.edtFSS.setInputMask(_translate("OrgEditorDialog", "9999999999; ", None))
        self.lblIsInsurer.setText(_translate("OrgEditorDialog", "Страховая компания", None))
        self.label_2.setText(_translate("OrgEditorDialog", "Регион", None))
        self.lblOKPO.setText(_translate("OrgEditorDialog", "ОКПО", None))
        self.lblOKPF.setText(_translate("OrgEditorDialog", "ОКПФ", None))
        self.lblObsoleteInfisCode.setText(_translate("OrgEditorDialog", "Устаревший ИНФИС", None))
        self.edtKPP.setInputMask(_translate("OrgEditorDialog", "999999999; ", None))
        self.btnSelectHeadOrganisation.setText(_translate("OrgEditorDialog", "...", None))
        self.edtINN.setInputMask(_translate("OrgEditorDialog", "999999999900; ", None))
        self.lblNetricaCode.setText(_translate("OrgEditorDialog", "Код Нетрики", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabBaseInfo), _translate("OrgEditorDialog", "Основная информация", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAccounts), _translate("OrgEditorDialog", "Раcчетные счета", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPolicySerials), _translate("OrgEditorDialog", "Серии полисов", None))

from KLADR.kladrComboxes import CKLADRComboBox
from OrgComboBox import COrgComboBox
from library.InDocTable import CInDocTableView
from library.crbcombobox import CRBComboBox
