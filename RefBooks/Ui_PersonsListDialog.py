# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PersonsListDialog.ui'
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

class Ui_PersonsListDialog(object):
    def setupUi(self, PersonsListDialog):
        PersonsListDialog.setObjectName(_fromUtf8("PersonsListDialog"))
        PersonsListDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PersonsListDialog.resize(908, 717)
        PersonsListDialog.setSizeGripEnabled(True)
        PersonsListDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(PersonsListDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblItems = CTableView(PersonsListDialog)
        self.tblItems.setTabKeyNavigation(False)
        self.tblItems.setAlternatingRowColors(True)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 30, 0, 1, 1)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(PersonsListDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.chkOnlyOwn = QtGui.QCheckBox(PersonsListDialog)
        self.chkOnlyOwn.setChecked(True)
        self.chkOnlyOwn.setObjectName(_fromUtf8("chkOnlyOwn"))
        self.hboxlayout.addWidget(self.chkOnlyOwn)
        self.chkOnlyWorking = QtGui.QCheckBox(PersonsListDialog)
        self.chkOnlyWorking.setChecked(True)
        self.chkOnlyWorking.setObjectName(_fromUtf8("chkOnlyWorking"))
        self.hboxlayout.addWidget(self.chkOnlyWorking)
        self.chkOnlyResearcher = QtGui.QCheckBox(PersonsListDialog)
        self.chkOnlyResearcher.setObjectName(_fromUtf8("chkOnlyResearcher"))
        self.hboxlayout.addWidget(self.chkOnlyResearcher)
        self.btnSync = QtGui.QPushButton(PersonsListDialog)
        self.btnSync.setObjectName(_fromUtf8("btnSync"))
        self.hboxlayout.addWidget(self.btnSync)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(PersonsListDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.hboxlayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.hboxlayout, 32, 0, 1, 2)
        self.tabWidget = QtGui.QTabWidget(PersonsListDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tabWidget.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.tabWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabCommon = QtGui.QWidget()
        self.tabCommon.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tabCommon.setObjectName(_fromUtf8("tabCommon"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tabCommon)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.chkSpec = QtGui.QCheckBox(self.tabCommon)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkSpec.sizePolicy().hasHeightForWidth())
        self.chkSpec.setSizePolicy(sizePolicy)
        self.chkSpec.setObjectName(_fromUtf8("chkSpec"))
        self.gridLayout_2.addWidget(self.chkSpec, 11, 0, 1, 1)
        self.chkUserRightsProfile = QtGui.QCheckBox(self.tabCommon)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkUserRightsProfile.sizePolicy().hasHeightForWidth())
        self.chkUserRightsProfile.setSizePolicy(sizePolicy)
        self.chkUserRightsProfile.setObjectName(_fromUtf8("chkUserRightsProfile"))
        self.gridLayout_2.addWidget(self.chkUserRightsProfile, 4, 2, 1, 1)
        self.chkLPU = QtGui.QCheckBox(self.tabCommon)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkLPU.sizePolicy().hasHeightForWidth())
        self.chkLPU.setSizePolicy(sizePolicy)
        self.chkLPU.setObjectName(_fromUtf8("chkLPU"))
        self.gridLayout_2.addWidget(self.chkLPU, 5, 2, 1, 1)
        self.chkAcademicDegree = QtGui.QCheckBox(self.tabCommon)
        self.chkAcademicDegree.setObjectName(_fromUtf8("chkAcademicDegree"))
        self.gridLayout_2.addWidget(self.chkAcademicDegree, 11, 2, 1, 1)
        self.edtFirstName = QtGui.QLineEdit(self.tabCommon)
        self.edtFirstName.setEnabled(False)
        self.edtFirstName.setObjectName(_fromUtf8("edtFirstName"))
        self.gridLayout_2.addWidget(self.edtFirstName, 5, 1, 1, 1)
        self.cmbAcademicDegree = CEnumComboBox(self.tabCommon)
        self.cmbAcademicDegree.setEnabled(False)
        self.cmbAcademicDegree.setObjectName(_fromUtf8("cmbAcademicDegree"))
        self.gridLayout_2.addWidget(self.cmbAcademicDegree, 11, 3, 1, 1)
        self.cmbOccupationType = CEnumComboBox(self.tabCommon)
        self.cmbOccupationType.setEnabled(False)
        self.cmbOccupationType.setObjectName(_fromUtf8("cmbOccupationType"))
        self.gridLayout_2.addWidget(self.cmbOccupationType, 1, 3, 1, 1)
        self.chkIsReservist = QtGui.QCheckBox(self.tabCommon)
        self.chkIsReservist.setObjectName(_fromUtf8("chkIsReservist"))
        self.gridLayout_2.addWidget(self.chkIsReservist, 7, 2, 1, 1)
        self.cmbActivity = CRBComboBox(self.tabCommon)
        self.cmbActivity.setEnabled(False)
        self.cmbActivity.setObjectName(_fromUtf8("cmbActivity"))
        self.gridLayout_2.addWidget(self.cmbActivity, 13, 1, 1, 1)
        self.chkFirstName = QtGui.QCheckBox(self.tabCommon)
        self.chkFirstName.setObjectName(_fromUtf8("chkFirstName"))
        self.gridLayout_2.addWidget(self.chkFirstName, 5, 0, 1, 1)
        self.cmbUserRightsProfile = CRBComboBox(self.tabCommon)
        self.cmbUserRightsProfile.setEnabled(False)
        self.cmbUserRightsProfile.setObjectName(_fromUtf8("cmbUserRightsProfile"))
        self.gridLayout_2.addWidget(self.cmbUserRightsProfile, 4, 3, 1, 1)
        self.chkOccupationType = QtGui.QCheckBox(self.tabCommon)
        self.chkOccupationType.setObjectName(_fromUtf8("chkOccupationType"))
        self.gridLayout_2.addWidget(self.chkOccupationType, 1, 2, 1, 1)
        self.chkActivity = QtGui.QCheckBox(self.tabCommon)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkActivity.sizePolicy().hasHeightForWidth())
        self.chkActivity.setSizePolicy(sizePolicy)
        self.chkActivity.setObjectName(_fromUtf8("chkActivity"))
        self.gridLayout_2.addWidget(self.chkActivity, 13, 0, 1, 1)
        self.chkLastName = QtGui.QCheckBox(self.tabCommon)
        self.chkLastName.setObjectName(_fromUtf8("chkLastName"))
        self.gridLayout_2.addWidget(self.chkLastName, 4, 0, 1, 1)
        self.cmbIsReservist = CEnumComboBox(self.tabCommon)
        self.cmbIsReservist.setEnabled(False)
        self.cmbIsReservist.setObjectName(_fromUtf8("cmbIsReservist"))
        self.gridLayout_2.addWidget(self.cmbIsReservist, 7, 3, 1, 1)
        self.edtLastName = QtGui.QLineEdit(self.tabCommon)
        self.edtLastName.setEnabled(False)
        self.edtLastName.setObjectName(_fromUtf8("edtLastName"))
        self.gridLayout_2.addWidget(self.edtLastName, 4, 1, 1, 1)
        self.boxStrPodr = COrgStructureComboBox(self.tabCommon)
        self.boxStrPodr.setEnabled(False)
        self.boxStrPodr.setObjectName(_fromUtf8("boxStrPodr"))
        self.gridLayout_2.addWidget(self.boxStrPodr, 9, 1, 1, 1)
        self.edtPatrName = QtGui.QLineEdit(self.tabCommon)
        self.edtPatrName.setEnabled(False)
        self.edtPatrName.setObjectName(_fromUtf8("edtPatrName"))
        self.gridLayout_2.addWidget(self.edtPatrName, 7, 1, 1, 1)
        self.cmbEmploymentType = CEnumComboBox(self.tabCommon)
        self.cmbEmploymentType.setEnabled(False)
        self.cmbEmploymentType.setObjectName(_fromUtf8("cmbEmploymentType"))
        self.gridLayout_2.addWidget(self.cmbEmploymentType, 9, 3, 1, 1)
        self.chkCode = QtGui.QCheckBox(self.tabCommon)
        self.chkCode.setObjectName(_fromUtf8("chkCode"))
        self.gridLayout_2.addWidget(self.chkCode, 1, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(self.tabCommon)
        self.edtCode.setEnabled(False)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout_2.addWidget(self.edtCode, 1, 1, 1, 1)
        self.edtFedCode = QtGui.QLineEdit(self.tabCommon)
        self.edtFedCode.setEnabled(False)
        self.edtFedCode.setObjectName(_fromUtf8("edtFedCode"))
        self.gridLayout_2.addWidget(self.edtFedCode, 13, 3, 1, 1)
        self.chkStrPodr = QtGui.QCheckBox(self.tabCommon)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkStrPodr.sizePolicy().hasHeightForWidth())
        self.chkStrPodr.setSizePolicy(sizePolicy)
        self.chkStrPodr.setObjectName(_fromUtf8("chkStrPodr"))
        self.gridLayout_2.addWidget(self.chkStrPodr, 9, 0, 1, 1)
        self.chkEmploymentType = QtGui.QCheckBox(self.tabCommon)
        self.chkEmploymentType.setObjectName(_fromUtf8("chkEmploymentType"))
        self.gridLayout_2.addWidget(self.chkEmploymentType, 9, 2, 1, 1)
        self.chkFedCode = QtGui.QCheckBox(self.tabCommon)
        self.chkFedCode.setObjectName(_fromUtf8("chkFedCode"))
        self.gridLayout_2.addWidget(self.chkFedCode, 13, 2, 1, 1)
        self.cmbSpeciality = CRBComboBox(self.tabCommon)
        self.cmbSpeciality.setEnabled(False)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout_2.addWidget(self.cmbSpeciality, 11, 1, 1, 1)
        self.chkPatrName = QtGui.QCheckBox(self.tabCommon)
        self.chkPatrName.setObjectName(_fromUtf8("chkPatrName"))
        self.gridLayout_2.addWidget(self.chkPatrName, 7, 0, 1, 1)
        self.cmbOrg = CPolyclinicExtendedComboBox(self.tabCommon)
        self.cmbOrg.setEnabled(False)
        self.cmbOrg.setObjectName(_fromUtf8("cmbOrg"))
        self.gridLayout_2.addWidget(self.cmbOrg, 5, 3, 1, 1)
        self.tabWidget.addTab(self.tabCommon, _fromUtf8(""))
        self.tabPrivateInform = QtGui.QWidget()
        self.tabPrivateInform.setObjectName(_fromUtf8("tabPrivateInform"))
        self.gridLayout_6 = QtGui.QGridLayout(self.tabPrivateInform)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.chkMaritalStatus = QtGui.QCheckBox(self.tabPrivateInform)
        self.chkMaritalStatus.setObjectName(_fromUtf8("chkMaritalStatus"))
        self.gridLayout_5.addWidget(self.chkMaritalStatus, 1, 0, 1, 1)
        self.chkBirthDate = QtGui.QCheckBox(self.tabPrivateInform)
        self.chkBirthDate.setObjectName(_fromUtf8("chkBirthDate"))
        self.gridLayout_5.addWidget(self.chkBirthDate, 4, 0, 1, 1)
        self.edtBirthDate = CDateEdit(self.tabPrivateInform)
        self.edtBirthDate.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBirthDate.sizePolicy().hasHeightForWidth())
        self.edtBirthDate.setSizePolicy(sizePolicy)
        self.edtBirthDate.setObjectName(_fromUtf8("edtBirthDate"))
        self.gridLayout_5.addWidget(self.edtBirthDate, 4, 1, 1, 1)
        self.cmbSex = QtGui.QComboBox(self.tabPrivateInform)
        self.cmbSex.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSex.sizePolicy().hasHeightForWidth())
        self.cmbSex.setSizePolicy(sizePolicy)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridLayout_5.addWidget(self.cmbSex, 3, 1, 1, 1)
        self.chkCitizenship = QtGui.QCheckBox(self.tabPrivateInform)
        self.chkCitizenship.setObjectName(_fromUtf8("chkCitizenship"))
        self.gridLayout_5.addWidget(self.chkCitizenship, 2, 0, 1, 1)
        self.cmbRegistryType = CEnumComboBox(self.tabPrivateInform)
        self.cmbRegistryType.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbRegistryType.sizePolicy().hasHeightForWidth())
        self.cmbRegistryType.setSizePolicy(sizePolicy)
        self.cmbRegistryType.setObjectName(_fromUtf8("cmbRegistryType"))
        self.gridLayout_5.addWidget(self.cmbRegistryType, 0, 1, 1, 1)
        self.cmbCitizenship = CRBComboBox(self.tabPrivateInform)
        self.cmbCitizenship.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbCitizenship.sizePolicy().hasHeightForWidth())
        self.cmbCitizenship.setSizePolicy(sizePolicy)
        self.cmbCitizenship.setObjectName(_fromUtf8("cmbCitizenship"))
        self.gridLayout_5.addWidget(self.cmbCitizenship, 2, 1, 1, 1)
        self.chkSex = QtGui.QCheckBox(self.tabPrivateInform)
        self.chkSex.setObjectName(_fromUtf8("chkSex"))
        self.gridLayout_5.addWidget(self.chkSex, 3, 0, 1, 1)
        self.chkRegistryType = QtGui.QCheckBox(self.tabPrivateInform)
        self.chkRegistryType.setObjectName(_fromUtf8("chkRegistryType"))
        self.gridLayout_5.addWidget(self.chkRegistryType, 0, 0, 1, 1)
        self.cmbMaritalStatus = CEnumComboBox(self.tabPrivateInform)
        self.cmbMaritalStatus.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbMaritalStatus.sizePolicy().hasHeightForWidth())
        self.cmbMaritalStatus.setSizePolicy(sizePolicy)
        self.cmbMaritalStatus.setObjectName(_fromUtf8("cmbMaritalStatus"))
        self.gridLayout_5.addWidget(self.cmbMaritalStatus, 1, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem2, 0, 2, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_5, 0, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_6.addItem(spacerItem3, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tabPrivateInform, _fromUtf8(""))
        self.tabQualification = QtGui.QWidget()
        self.tabQualification.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tabQualification.setObjectName(_fromUtf8("tabQualification"))
        self.gridLayout_4 = QtGui.QGridLayout(self.tabQualification)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.cmbCategory = CRBComboBox(self.tabQualification)
        self.cmbCategory.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbCategory.sizePolicy().hasHeightForWidth())
        self.cmbCategory.setSizePolicy(sizePolicy)
        self.cmbCategory.setObjectName(_fromUtf8("cmbCategory"))
        self.gridLayout_3.addWidget(self.cmbCategory, 1, 1, 1, 1)
        self.cmbEducationType = CEnumComboBox(self.tabQualification)
        self.cmbEducationType.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbEducationType.sizePolicy().hasHeightForWidth())
        self.cmbEducationType.setSizePolicy(sizePolicy)
        self.cmbEducationType.setObjectName(_fromUtf8("cmbEducationType"))
        self.gridLayout_3.addWidget(self.cmbEducationType, 0, 1, 1, 1)
        self.chkCategory = QtGui.QCheckBox(self.tabQualification)
        self.chkCategory.setObjectName(_fromUtf8("chkCategory"))
        self.gridLayout_3.addWidget(self.chkCategory, 1, 0, 1, 1)
        self.chkEducationType = QtGui.QCheckBox(self.tabQualification)
        self.chkEducationType.setObjectName(_fromUtf8("chkEducationType"))
        self.gridLayout_3.addWidget(self.chkEducationType, 0, 0, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem4, 0, 2, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem5, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tabQualification, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 3, 0, 1, 1)

        self.retranslateUi(PersonsListDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PersonsListDialog.close)
        QtCore.QObject.connect(self.chkFedCode, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtFedCode.setEnabled)
        QtCore.QObject.connect(self.chkFedCode, QtCore.SIGNAL(_fromUtf8("clicked()")), self.edtFedCode.setFocus)
        QtCore.QObject.connect(self.chkStrPodr, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.boxStrPodr.setEnabled)
        QtCore.QObject.connect(self.chkSpec, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbSpeciality.setEnabled)
        QtCore.QObject.connect(self.chkPatrName, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtPatrName.setEnabled)
        QtCore.QObject.connect(self.chkActivity, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbActivity.setEnabled)
        QtCore.QObject.connect(self.chkFirstName, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtFirstName.setEnabled)
        QtCore.QObject.connect(self.chkLastName, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtLastName.setEnabled)
        QtCore.QObject.connect(self.chkCode, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtCode.setEnabled)
        QtCore.QObject.connect(self.chkOccupationType, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbOccupationType.setEnabled)
        QtCore.QObject.connect(self.chkAcademicDegree, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbAcademicDegree.setEnabled)
        QtCore.QObject.connect(self.chkEmploymentType, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbEmploymentType.setEnabled)
        QtCore.QObject.connect(self.chkIsReservist, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbIsReservist.setEnabled)
        QtCore.QObject.connect(self.chkLPU, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbOrg.setEnabled)
        QtCore.QObject.connect(self.chkUserRightsProfile, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbUserRightsProfile.setEnabled)
        QtCore.QObject.connect(self.chkRegistryType, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbRegistryType.setEnabled)
        QtCore.QObject.connect(self.chkMaritalStatus, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbMaritalStatus.setEnabled)
        QtCore.QObject.connect(self.chkCitizenship, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbCitizenship.setEnabled)
        QtCore.QObject.connect(self.chkEducationType, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbEducationType.setEnabled)
        QtCore.QObject.connect(self.chkCategory, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbCategory.setEnabled)
        QtCore.QObject.connect(self.chkSex, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbSex.setEnabled)
        QtCore.QObject.connect(self.chkBirthDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtBirthDate.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(PersonsListDialog)
        PersonsListDialog.setTabOrder(self.chkCode, self.edtCode)
        PersonsListDialog.setTabOrder(self.edtCode, self.chkLastName)
        PersonsListDialog.setTabOrder(self.chkLastName, self.edtLastName)
        PersonsListDialog.setTabOrder(self.edtLastName, self.chkFirstName)
        PersonsListDialog.setTabOrder(self.chkFirstName, self.edtFirstName)
        PersonsListDialog.setTabOrder(self.edtFirstName, self.chkPatrName)
        PersonsListDialog.setTabOrder(self.chkPatrName, self.edtPatrName)
        PersonsListDialog.setTabOrder(self.edtPatrName, self.chkStrPodr)
        PersonsListDialog.setTabOrder(self.chkStrPodr, self.boxStrPodr)
        PersonsListDialog.setTabOrder(self.boxStrPodr, self.chkSpec)
        PersonsListDialog.setTabOrder(self.chkSpec, self.cmbSpeciality)
        PersonsListDialog.setTabOrder(self.cmbSpeciality, self.chkActivity)
        PersonsListDialog.setTabOrder(self.chkActivity, self.cmbActivity)
        PersonsListDialog.setTabOrder(self.cmbActivity, self.chkOccupationType)
        PersonsListDialog.setTabOrder(self.chkOccupationType, self.cmbOccupationType)
        PersonsListDialog.setTabOrder(self.cmbOccupationType, self.chkUserRightsProfile)
        PersonsListDialog.setTabOrder(self.chkUserRightsProfile, self.cmbUserRightsProfile)
        PersonsListDialog.setTabOrder(self.cmbUserRightsProfile, self.chkLPU)
        PersonsListDialog.setTabOrder(self.chkLPU, self.cmbOrg)
        PersonsListDialog.setTabOrder(self.cmbOrg, self.chkIsReservist)
        PersonsListDialog.setTabOrder(self.chkIsReservist, self.cmbIsReservist)
        PersonsListDialog.setTabOrder(self.cmbIsReservist, self.chkEmploymentType)
        PersonsListDialog.setTabOrder(self.chkEmploymentType, self.cmbEmploymentType)
        PersonsListDialog.setTabOrder(self.cmbEmploymentType, self.chkAcademicDegree)
        PersonsListDialog.setTabOrder(self.chkAcademicDegree, self.cmbAcademicDegree)
        PersonsListDialog.setTabOrder(self.cmbAcademicDegree, self.chkFedCode)
        PersonsListDialog.setTabOrder(self.chkFedCode, self.edtFedCode)
        PersonsListDialog.setTabOrder(self.edtFedCode, self.tblItems)
        PersonsListDialog.setTabOrder(self.tblItems, self.chkOnlyOwn)
        PersonsListDialog.setTabOrder(self.chkOnlyOwn, self.chkOnlyWorking)
        PersonsListDialog.setTabOrder(self.chkOnlyWorking, self.chkOnlyResearcher)
        PersonsListDialog.setTabOrder(self.chkOnlyResearcher, self.btnSync)
        PersonsListDialog.setTabOrder(self.btnSync, self.buttonBox)
        PersonsListDialog.setTabOrder(self.buttonBox, self.chkRegistryType)
        PersonsListDialog.setTabOrder(self.chkRegistryType, self.cmbRegistryType)
        PersonsListDialog.setTabOrder(self.cmbRegistryType, self.chkMaritalStatus)
        PersonsListDialog.setTabOrder(self.chkMaritalStatus, self.cmbMaritalStatus)
        PersonsListDialog.setTabOrder(self.cmbMaritalStatus, self.chkCitizenship)
        PersonsListDialog.setTabOrder(self.chkCitizenship, self.cmbCitizenship)
        PersonsListDialog.setTabOrder(self.cmbCitizenship, self.chkSex)
        PersonsListDialog.setTabOrder(self.chkSex, self.cmbSex)
        PersonsListDialog.setTabOrder(self.cmbSex, self.chkBirthDate)
        PersonsListDialog.setTabOrder(self.chkBirthDate, self.edtBirthDate)
        PersonsListDialog.setTabOrder(self.edtBirthDate, self.chkEducationType)
        PersonsListDialog.setTabOrder(self.chkEducationType, self.cmbEducationType)
        PersonsListDialog.setTabOrder(self.cmbEducationType, self.chkCategory)
        PersonsListDialog.setTabOrder(self.chkCategory, self.cmbCategory)

    def retranslateUi(self, PersonsListDialog):
        PersonsListDialog.setWindowTitle(_translate("PersonsListDialog", "Список записей", None))
        self.tblItems.setWhatsThis(_translate("PersonsListDialog", "список записей", "ура!"))
        self.label.setText(_translate("PersonsListDialog", "всего: ", None))
        self.chkOnlyOwn.setText(_translate("PersonsListDialog", "Только свои", None))
        self.chkOnlyWorking.setText(_translate("PersonsListDialog", "Только работающие", None))
        self.chkOnlyResearcher.setText(_translate("PersonsListDialog", "Только главные исследователи", None))
        self.btnSync.setText(_translate("PersonsListDialog", "Синхронизация", None))
        self.chkSpec.setText(_translate("PersonsListDialog", "Специальность", None))
        self.chkUserRightsProfile.setText(_translate("PersonsListDialog", "Профиль прав", None))
        self.chkLPU.setText(_translate("PersonsListDialog", "Внешнее ЛПУ", None))
        self.chkAcademicDegree.setText(_translate("PersonsListDialog", "Учёная степень", None))
        self.chkIsReservist.setText(_translate("PersonsListDialog", "Отношение к военной службе", None))
        self.chkFirstName.setText(_translate("PersonsListDialog", "Имя", None))
        self.chkOccupationType.setText(_translate("PersonsListDialog", "Тип занятия должности", None))
        self.chkActivity.setText(_translate("PersonsListDialog", "Вид деятельности", None))
        self.chkLastName.setText(_translate("PersonsListDialog", "Фамилия", None))
        self.chkCode.setText(_translate("PersonsListDialog", "Код", None))
        self.chkStrPodr.setText(_translate("PersonsListDialog", "Структурное подразделение", None))
        self.chkEmploymentType.setText(_translate("PersonsListDialog", "Режим работы", None))
        self.chkFedCode.setText(_translate("PersonsListDialog", "Федеральный код", None))
        self.chkPatrName.setText(_translate("PersonsListDialog", "Отчество", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCommon), _translate("PersonsListDialog", "Общее", None))
        self.chkMaritalStatus.setText(_translate("PersonsListDialog", "Семейное положение", None))
        self.chkBirthDate.setText(_translate("PersonsListDialog", "Дата рождения", None))
        self.cmbSex.setItemText(1, _translate("PersonsListDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("PersonsListDialog", "Ж", None))
        self.chkCitizenship.setText(_translate("PersonsListDialog", "Гражданство", None))
        self.chkSex.setText(_translate("PersonsListDialog", "Пол", None))
        self.chkRegistryType.setText(_translate("PersonsListDialog", "Тип регистрации", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPrivateInform), _translate("PersonsListDialog", "Личное", None))
        self.chkCategory.setText(_translate("PersonsListDialog", "Категория", None))
        self.chkEducationType.setText(_translate("PersonsListDialog", "Тип образования", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabQualification), _translate("PersonsListDialog", "Квалификация", None))

from Orgs.OrgComboBox import CPolyclinicExtendedComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from library.Enum import CEnumComboBox
from library.TableView import CTableView
from library.crbcombobox import CRBComboBox
