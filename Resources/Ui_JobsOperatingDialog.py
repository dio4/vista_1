# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'JobsOperatingDialog.ui'
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

class Ui_JobsOperatingDialog(object):
    def setupUi(self, JobsOperatingDialog):
        JobsOperatingDialog.setObjectName(_fromUtf8("JobsOperatingDialog"))
        JobsOperatingDialog.setWindowModality(QtCore.Qt.NonModal)
        JobsOperatingDialog.resize(1159, 743)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(JobsOperatingDialog.sizePolicy().hasHeightForWidth())
        JobsOperatingDialog.setSizePolicy(sizePolicy)
        JobsOperatingDialog.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout_3 = QtGui.QVBoxLayout(JobsOperatingDialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.splitter_2 = QtGui.QSplitter(JobsOperatingDialog)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.pnlFilter = QtGui.QWidget(self.splitter_2)
        self.pnlFilter.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pnlFilter.sizePolicy().hasHeightForWidth())
        self.pnlFilter.setSizePolicy(sizePolicy)
        self.pnlFilter.setObjectName(_fromUtf8("pnlFilter"))
        self.verticalLayout = QtGui.QVBoxLayout(self.pnlFilter)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.pnlSmartFilter = QtGui.QWidget(self.pnlFilter)
        self.pnlSmartFilter.setObjectName(_fromUtf8("pnlSmartFilter"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.pnlSmartFilter)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setSpacing(4)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.splitter = QtGui.QSplitter(self.pnlSmartFilter)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.treeOrgStructure = QtGui.QTreeView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.treeOrgStructure.sizePolicy().hasHeightForWidth())
        self.treeOrgStructure.setSizePolicy(sizePolicy)
        self.treeOrgStructure.setObjectName(_fromUtf8("treeOrgStructure"))
        self.tabDateClientFilter = QtGui.QTabWidget(self.splitter)
        self.tabDateClientFilter.setObjectName(_fromUtf8("tabDateClientFilter"))
        self.tabDateFilter = QtGui.QWidget()
        self.tabDateFilter.setObjectName(_fromUtf8("tabDateFilter"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tabDateFilter)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.calendar = CCalendarWidget(self.tabDateFilter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calendar.sizePolicy().hasHeightForWidth())
        self.calendar.setSizePolicy(sizePolicy)
        self.calendar.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.calendar.setGridVisible(False)
        self.calendar.setObjectName(_fromUtf8("calendar"))
        self.gridLayout_2.addWidget(self.calendar, 1, 1, 1, 1)
        self.pnlDateRange = QtGui.QWidget(self.tabDateFilter)
        self.pnlDateRange.setEnabled(False)
        self.pnlDateRange.setObjectName(_fromUtf8("pnlDateRange"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.pnlDateRange)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblDateRangeFrom = QtGui.QLabel(self.pnlDateRange)
        self.lblDateRangeFrom.setEnabled(False)
        self.lblDateRangeFrom.setObjectName(_fromUtf8("lblDateRangeFrom"))
        self.horizontalLayout.addWidget(self.lblDateRangeFrom)
        self.edtDateRangeFrom = CDateEdit(self.pnlDateRange)
        self.edtDateRangeFrom.setEnabled(False)
        self.edtDateRangeFrom.setObjectName(_fromUtf8("edtDateRangeFrom"))
        self.horizontalLayout.addWidget(self.edtDateRangeFrom)
        self.lblDateRangeTo = QtGui.QLabel(self.pnlDateRange)
        self.lblDateRangeTo.setEnabled(False)
        self.lblDateRangeTo.setObjectName(_fromUtf8("lblDateRangeTo"))
        self.horizontalLayout.addWidget(self.lblDateRangeTo)
        self.edtDateRangeTo = CDateEdit(self.pnlDateRange)
        self.edtDateRangeTo.setEnabled(False)
        self.edtDateRangeTo.setObjectName(_fromUtf8("edtDateRangeTo"))
        self.horizontalLayout.addWidget(self.edtDateRangeTo)
        self.gridLayout_2.addWidget(self.pnlDateRange, 2, 1, 1, 1)
        self.btnCalendarDate = QtGui.QRadioButton(self.tabDateFilter)
        self.btnCalendarDate.setText(_fromUtf8(""))
        self.btnCalendarDate.setCheckable(True)
        self.btnCalendarDate.setChecked(True)
        self.btnCalendarDate.setObjectName(_fromUtf8("btnCalendarDate"))
        self.gridLayout_2.addWidget(self.btnCalendarDate, 1, 0, 1, 1)
        self.btnDateRange = QtGui.QRadioButton(self.tabDateFilter)
        self.btnDateRange.setText(_fromUtf8(""))
        self.btnDateRange.setObjectName(_fromUtf8("btnDateRange"))
        self.gridLayout_2.addWidget(self.btnDateRange, 2, 0, 1, 1)
        self.tabDateClientFilter.addTab(self.tabDateFilter, _fromUtf8(""))
        self.tblJobTypes = CTableView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.tblJobTypes.sizePolicy().hasHeightForWidth())
        self.tblJobTypes.setSizePolicy(sizePolicy)
        self.tblJobTypes.setObjectName(_fromUtf8("tblJobTypes"))
        self.verticalLayout_4.addWidget(self.splitter)
        self.verticalLayout_2.addWidget(self.pnlSmartFilter)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.pnlJobTickets = QtGui.QWidget(self.splitter_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pnlJobTickets.sizePolicy().hasHeightForWidth())
        self.pnlJobTickets.setSizePolicy(sizePolicy)
        self.pnlJobTickets.setObjectName(_fromUtf8("pnlJobTickets"))
        self.gridLayout_4 = QtGui.QGridLayout(self.pnlJobTickets)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.lblSuperviseInfo = QtGui.QLabel(self.pnlJobTickets)
        self.lblSuperviseInfo.setObjectName(_fromUtf8("lblSuperviseInfo"))
        self.gridLayout_4.addWidget(self.lblSuperviseInfo, 4, 2, 1, 1)
        self.tblJobTickets = CJobTicketsView(self.pnlJobTickets)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblJobTickets.sizePolicy().hasHeightForWidth())
        self.tblJobTickets.setSizePolicy(sizePolicy)
        self.tblJobTickets.setObjectName(_fromUtf8("tblJobTickets"))
        self.gridLayout_4.addWidget(self.tblJobTickets, 0, 1, 1, 2)
        self.lblTicketsCount = QtGui.QLabel(self.pnlJobTickets)
        self.lblTicketsCount.setObjectName(_fromUtf8("lblTicketsCount"))
        self.gridLayout_4.addWidget(self.lblTicketsCount, 4, 1, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setContentsMargins(-1, -1, 0, -1)
        self.gridLayout_3.setHorizontalSpacing(1)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lblCurrentTablePage = QtGui.QLabel(self.pnlJobTickets)
        self.lblCurrentTablePage.setEnabled(False)
        self.lblCurrentTablePage.setMinimumSize(QtCore.QSize(100, 0))
        self.lblCurrentTablePage.setAlignment(QtCore.Qt.AlignCenter)
        self.lblCurrentTablePage.setObjectName(_fromUtf8("lblCurrentTablePage"))
        self.gridLayout_3.addWidget(self.lblCurrentTablePage, 0, 2, 1, 1)
        self.btnNextTablePage = QtGui.QPushButton(self.pnlJobTickets)
        self.btnNextTablePage.setEnabled(False)
        self.btnNextTablePage.setObjectName(_fromUtf8("btnNextTablePage"))
        self.gridLayout_3.addWidget(self.btnNextTablePage, 0, 3, 1, 1)
        self.btnPrevTablePage = QtGui.QPushButton(self.pnlJobTickets)
        self.btnPrevTablePage.setEnabled(False)
        self.btnPrevTablePage.setObjectName(_fromUtf8("btnPrevTablePage"))
        self.gridLayout_3.addWidget(self.btnPrevTablePage, 0, 1, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 3, 2, 1, 1)
        self.lblMaxTablePagesCount = QtGui.QLabel(self.pnlJobTickets)
        self.lblMaxTablePagesCount.setEnabled(False)
        self.lblMaxTablePagesCount.setObjectName(_fromUtf8("lblMaxTablePagesCount"))
        self.gridLayout_4.addWidget(self.lblMaxTablePagesCount, 3, 1, 1, 1)
        self.verticalLayout_3.addWidget(self.splitter_2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btnEnableStaticFilter = QtGui.QToolButton(JobsOperatingDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnEnableStaticFilter.sizePolicy().hasHeightForWidth())
        self.btnEnableStaticFilter.setSizePolicy(sizePolicy)
        self.btnEnableStaticFilter.setCheckable(True)
        self.btnEnableStaticFilter.setChecked(True)
        self.btnEnableStaticFilter.setAutoExclusive(False)
        self.btnEnableStaticFilter.setObjectName(_fromUtf8("btnEnableStaticFilter"))
        self.horizontalLayout_2.addWidget(self.btnEnableStaticFilter)
        self.btnEnableEQueue = QtGui.QToolButton(JobsOperatingDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnEnableEQueue.sizePolicy().hasHeightForWidth())
        self.btnEnableEQueue.setSizePolicy(sizePolicy)
        self.btnEnableEQueue.setCheckable(True)
        self.btnEnableEQueue.setAutoExclusive(False)
        self.btnEnableEQueue.setObjectName(_fromUtf8("btnEnableEQueue"))
        self.horizontalLayout_2.addWidget(self.btnEnableEQueue)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.grpStaticFilter = QtGui.QStackedWidget(JobsOperatingDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpStaticFilter.sizePolicy().hasHeightForWidth())
        self.grpStaticFilter.setSizePolicy(sizePolicy)
        self.grpStaticFilter.setMinimumSize(QtCore.QSize(0, 0))
        self.grpStaticFilter.setObjectName(_fromUtf8("grpStaticFilter"))
        self.grpStaticFilterPage1 = QtGui.QWidget()
        self.grpStaticFilterPage1.setObjectName(_fromUtf8("grpStaticFilterPage1"))
        self.gridLayout = QtGui.QGridLayout(self.grpStaticFilterPage1)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.grpPersonFilter = QtGui.QGroupBox(self.grpStaticFilterPage1)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpPersonFilter.sizePolicy().hasHeightForWidth())
        self.grpPersonFilter.setSizePolicy(sizePolicy)
        self.grpPersonFilter.setObjectName(_fromUtf8("grpPersonFilter"))
        self.gridLayout_8 = QtGui.QGridLayout(self.grpPersonFilter)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.lblOrgStructure = QtGui.QLabel(self.grpPersonFilter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOrgStructure.sizePolicy().hasHeightForWidth())
        self.lblOrgStructure.setSizePolicy(sizePolicy)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout_8.addWidget(self.lblOrgStructure, 0, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(self.grpPersonFilter)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout_8.addWidget(self.cmbOrgStructure, 0, 1, 1, 1)
        self.lblSpeciality = QtGui.QLabel(self.grpPersonFilter)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout_8.addWidget(self.lblSpeciality, 1, 0, 1, 1)
        self.cmbSpeciality = CRBComboBox(self.grpPersonFilter)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout_8.addWidget(self.cmbSpeciality, 1, 1, 1, 1)
        self.lblPerson = QtGui.QLabel(self.grpPersonFilter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPerson.sizePolicy().hasHeightForWidth())
        self.lblPerson.setSizePolicy(sizePolicy)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout_8.addWidget(self.lblPerson, 2, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(self.grpPersonFilter)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridLayout_8.addWidget(self.cmbPerson, 2, 1, 1, 1)
        self.chkFilterListLength = QtGui.QCheckBox(self.grpPersonFilter)
        self.chkFilterListLength.setEnabled(True)
        self.chkFilterListLength.setChecked(True)
        self.chkFilterListLength.setObjectName(_fromUtf8("chkFilterListLength"))
        self.gridLayout_8.addWidget(self.chkFilterListLength, 3, 1, 1, 1)
        self.edtFilterListLength = QtGui.QSpinBox(self.grpPersonFilter)
        self.edtFilterListLength.setMaximum(1000000000)
        self.edtFilterListLength.setProperty("value", 250)
        self.edtFilterListLength.setObjectName(_fromUtf8("edtFilterListLength"))
        self.gridLayout_8.addWidget(self.edtFilterListLength, 4, 1, 1, 1)
        self.buttonBoxFilter = QtGui.QDialogButtonBox(self.grpPersonFilter)
        self.buttonBoxFilter.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBoxFilter.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBoxFilter.setObjectName(_fromUtf8("buttonBoxFilter"))
        self.gridLayout_8.addWidget(self.buttonBoxFilter, 5, 0, 1, 2)
        self.gridLayout.addWidget(self.grpPersonFilter, 10, 2, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.grpStaticFilterPage1)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.chkClientLastName = QtGui.QCheckBox(self.groupBox_2)
        self.chkClientLastName.setObjectName(_fromUtf8("chkClientLastName"))
        self.gridLayout_6.addWidget(self.chkClientLastName, 0, 0, 1, 2)
        self.edtClientLastName = QtGui.QLineEdit(self.groupBox_2)
        self.edtClientLastName.setEnabled(False)
        self.edtClientLastName.setObjectName(_fromUtf8("edtClientLastName"))
        self.gridLayout_6.addWidget(self.edtClientLastName, 0, 2, 1, 4)
        self.chkClientFirstName = QtGui.QCheckBox(self.groupBox_2)
        self.chkClientFirstName.setObjectName(_fromUtf8("chkClientFirstName"))
        self.gridLayout_6.addWidget(self.chkClientFirstName, 1, 0, 1, 2)
        self.edtClientFirstName = QtGui.QLineEdit(self.groupBox_2)
        self.edtClientFirstName.setEnabled(False)
        self.edtClientFirstName.setObjectName(_fromUtf8("edtClientFirstName"))
        self.gridLayout_6.addWidget(self.edtClientFirstName, 1, 2, 1, 4)
        self.chkClientPatrName = QtGui.QCheckBox(self.groupBox_2)
        self.chkClientPatrName.setObjectName(_fromUtf8("chkClientPatrName"))
        self.gridLayout_6.addWidget(self.chkClientPatrName, 2, 0, 1, 2)
        self.edtClientPatrName = QtGui.QLineEdit(self.groupBox_2)
        self.edtClientPatrName.setEnabled(False)
        self.edtClientPatrName.setObjectName(_fromUtf8("edtClientPatrName"))
        self.gridLayout_6.addWidget(self.edtClientPatrName, 2, 2, 1, 4)
        self.lblSex = QtGui.QLabel(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblSex.sizePolicy().hasHeightForWidth())
        self.lblSex.setSizePolicy(sizePolicy)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout_6.addWidget(self.lblSex, 3, 0, 1, 1)
        self.cmbSex = QtGui.QComboBox(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSex.sizePolicy().hasHeightForWidth())
        self.cmbSex.setSizePolicy(sizePolicy)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridLayout_6.addWidget(self.cmbSex, 3, 1, 1, 2)
        self.lblAge = QtGui.QLabel(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblAge.sizePolicy().hasHeightForWidth())
        self.lblAge.setSizePolicy(sizePolicy)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout_6.addWidget(self.lblAge, 4, 0, 1, 1)
        self.edtAgeFrom = QtGui.QSpinBox(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeFrom.sizePolicy().hasHeightForWidth())
        self.edtAgeFrom.setSizePolicy(sizePolicy)
        self.edtAgeFrom.setMaximum(150)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self.gridLayout_6.addWidget(self.edtAgeFrom, 4, 1, 1, 2)
        self.lblAgeTo = QtGui.QLabel(self.groupBox_2)
        self.lblAgeTo.setObjectName(_fromUtf8("lblAgeTo"))
        self.gridLayout_6.addWidget(self.lblAgeTo, 4, 3, 1, 1)
        self.edtAgeTo = QtGui.QSpinBox(self.groupBox_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeTo.sizePolicy().hasHeightForWidth())
        self.edtAgeTo.setSizePolicy(sizePolicy)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self.gridLayout_6.addWidget(self.edtAgeTo, 4, 4, 1, 1)
        self.lblAgeYears = QtGui.QLabel(self.groupBox_2)
        self.lblAgeYears.setObjectName(_fromUtf8("lblAgeYears"))
        self.gridLayout_6.addWidget(self.lblAgeYears, 4, 5, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 10, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(self.grpStaticFilterPage1)
        self.groupBox_3.setTitle(_fromUtf8(""))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.chkClientId = QtGui.QCheckBox(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkClientId.sizePolicy().hasHeightForWidth())
        self.chkClientId.setSizePolicy(sizePolicy)
        self.chkClientId.setObjectName(_fromUtf8("chkClientId"))
        self.gridLayout_7.addWidget(self.chkClientId, 0, 0, 1, 1)
        self.cmbClientAccountingSystem = CRBComboBox(self.groupBox_3)
        self.cmbClientAccountingSystem.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbClientAccountingSystem.sizePolicy().hasHeightForWidth())
        self.cmbClientAccountingSystem.setSizePolicy(sizePolicy)
        self.cmbClientAccountingSystem.setObjectName(_fromUtf8("cmbClientAccountingSystem"))
        self.gridLayout_7.addWidget(self.cmbClientAccountingSystem, 0, 1, 1, 3)
        self.edtClientId = QtGui.QLineEdit(self.groupBox_3)
        self.edtClientId.setEnabled(False)
        self.edtClientId.setInputMask(_fromUtf8(""))
        self.edtClientId.setMaxLength(32767)
        self.edtClientId.setObjectName(_fromUtf8("edtClientId"))
        self.gridLayout_7.addWidget(self.edtClientId, 1, 0, 1, 4)
        self.chkJobTicketId = QtGui.QCheckBox(self.groupBox_3)
        self.chkJobTicketId.setObjectName(_fromUtf8("chkJobTicketId"))
        self.gridLayout_7.addWidget(self.chkJobTicketId, 2, 0, 1, 2)
        self.edtJobTicketId = QtGui.QLineEdit(self.groupBox_3)
        self.edtJobTicketId.setEnabled(False)
        self.edtJobTicketId.setObjectName(_fromUtf8("edtJobTicketId"))
        self.gridLayout_7.addWidget(self.edtJobTicketId, 2, 2, 1, 2)
        self.lblTissueType = QtGui.QLabel(self.groupBox_3)
        self.lblTissueType.setObjectName(_fromUtf8("lblTissueType"))
        self.gridLayout_7.addWidget(self.lblTissueType, 3, 0, 1, 2)
        self.line = QtGui.QFrame(self.groupBox_3)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout_7.addWidget(self.line, 3, 2, 4, 1)
        self.chkAwaiting = QtGui.QCheckBox(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkAwaiting.sizePolicy().hasHeightForWidth())
        self.chkAwaiting.setSizePolicy(sizePolicy)
        self.chkAwaiting.setChecked(True)
        self.chkAwaiting.setObjectName(_fromUtf8("chkAwaiting"))
        self.gridLayout_7.addWidget(self.chkAwaiting, 3, 3, 1, 1)
        self.cmbTissueType = CRBComboBox(self.groupBox_3)
        self.cmbTissueType.setObjectName(_fromUtf8("cmbTissueType"))
        self.gridLayout_7.addWidget(self.cmbTissueType, 4, 0, 1, 2)
        self.chkInProgress = QtGui.QCheckBox(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkInProgress.sizePolicy().hasHeightForWidth())
        self.chkInProgress.setSizePolicy(sizePolicy)
        self.chkInProgress.setAutoFillBackground(False)
        self.chkInProgress.setObjectName(_fromUtf8("chkInProgress"))
        self.gridLayout_7.addWidget(self.chkInProgress, 4, 3, 1, 1)
        self.lblTakenTissueType = QtGui.QLabel(self.groupBox_3)
        self.lblTakenTissueType.setObjectName(_fromUtf8("lblTakenTissueType"))
        self.gridLayout_7.addWidget(self.lblTakenTissueType, 5, 0, 1, 2)
        self.chkDone = QtGui.QCheckBox(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chkDone.sizePolicy().hasHeightForWidth())
        self.chkDone.setSizePolicy(sizePolicy)
        self.chkDone.setObjectName(_fromUtf8("chkDone"))
        self.gridLayout_7.addWidget(self.chkDone, 5, 3, 1, 1)
        self.cmbTakenTissueType = CRBComboBox(self.groupBox_3)
        self.cmbTakenTissueType.setObjectName(_fromUtf8("cmbTakenTissueType"))
        self.gridLayout_7.addWidget(self.cmbTakenTissueType, 6, 0, 1, 2)
        self.chkOnlyUrgent = QtGui.QCheckBox(self.groupBox_3)
        self.chkOnlyUrgent.setObjectName(_fromUtf8("chkOnlyUrgent"))
        self.gridLayout_7.addWidget(self.chkOnlyUrgent, 6, 3, 1, 1)
        self.gridLayout.addWidget(self.groupBox_3, 10, 1, 1, 1)
        self.grpStaticFilter.addWidget(self.grpStaticFilterPage1)
        self.grbEQueueControlWidget = QtGui.QWidget()
        self.grbEQueueControlWidget.setObjectName(_fromUtf8("grbEQueueControlWidget"))
        self.gridLayout_5 = QtGui.QGridLayout(self.grbEQueueControlWidget)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.eqControlWidget = CEQControlWidget(self.grbEQueueControlWidget)
        self.eqControlWidget.setObjectName(_fromUtf8("eqControlWidget"))
        self.gridLayout_5.addWidget(self.eqControlWidget, 0, 0, 1, 1)
        self.grpStaticFilter.addWidget(self.grbEQueueControlWidget)
        self.verticalLayout_3.addWidget(self.grpStaticFilter)
        self.buttonBox = QtGui.QDialogButtonBox(JobsOperatingDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(JobsOperatingDialog)
        self.tabDateClientFilter.setCurrentIndex(0)
        self.grpStaticFilter.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), JobsOperatingDialog.reject)
        QtCore.QObject.connect(self.btnCalendarDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.calendar.setEnabled)
        QtCore.QObject.connect(self.btnCalendarDate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.pnlDateRange.setDisabled)
        QtCore.QObject.connect(self.btnDateRange, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblDateRangeFrom.setEnabled)
        QtCore.QObject.connect(self.btnDateRange, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lblDateRangeTo.setEnabled)
        QtCore.QObject.connect(self.btnDateRange, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtDateRangeFrom.setEnabled)
        QtCore.QObject.connect(self.btnDateRange, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtDateRangeTo.setEnabled)
        QtCore.QObject.connect(self.chkClientFirstName, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtClientFirstName.setEnabled)
        QtCore.QObject.connect(self.chkClientLastName, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtClientLastName.setEnabled)
        QtCore.QObject.connect(self.chkClientPatrName, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtClientPatrName.setEnabled)
        QtCore.QObject.connect(self.chkClientId, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbClientAccountingSystem.setEnabled)
        QtCore.QObject.connect(self.chkClientId, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtClientId.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(JobsOperatingDialog)
        JobsOperatingDialog.setTabOrder(self.btnCalendarDate, self.btnDateRange)
        JobsOperatingDialog.setTabOrder(self.btnDateRange, self.edtDateRangeFrom)
        JobsOperatingDialog.setTabOrder(self.edtDateRangeFrom, self.edtDateRangeTo)
        JobsOperatingDialog.setTabOrder(self.edtDateRangeTo, self.chkClientLastName)
        JobsOperatingDialog.setTabOrder(self.chkClientLastName, self.edtClientLastName)
        JobsOperatingDialog.setTabOrder(self.edtClientLastName, self.chkClientFirstName)
        JobsOperatingDialog.setTabOrder(self.chkClientFirstName, self.edtClientFirstName)
        JobsOperatingDialog.setTabOrder(self.edtClientFirstName, self.chkClientPatrName)
        JobsOperatingDialog.setTabOrder(self.chkClientPatrName, self.edtClientPatrName)
        JobsOperatingDialog.setTabOrder(self.edtClientPatrName, self.cmbSex)
        JobsOperatingDialog.setTabOrder(self.cmbSex, self.edtAgeFrom)
        JobsOperatingDialog.setTabOrder(self.edtAgeFrom, self.edtAgeTo)
        JobsOperatingDialog.setTabOrder(self.edtAgeTo, self.chkClientId)
        JobsOperatingDialog.setTabOrder(self.chkClientId, self.cmbClientAccountingSystem)
        JobsOperatingDialog.setTabOrder(self.cmbClientAccountingSystem, self.edtClientId)
        JobsOperatingDialog.setTabOrder(self.edtClientId, self.chkJobTicketId)
        JobsOperatingDialog.setTabOrder(self.chkJobTicketId, self.edtJobTicketId)
        JobsOperatingDialog.setTabOrder(self.edtJobTicketId, self.cmbTissueType)
        JobsOperatingDialog.setTabOrder(self.cmbTissueType, self.cmbTakenTissueType)
        JobsOperatingDialog.setTabOrder(self.cmbTakenTissueType, self.chkAwaiting)
        JobsOperatingDialog.setTabOrder(self.chkAwaiting, self.chkInProgress)
        JobsOperatingDialog.setTabOrder(self.chkInProgress, self.chkDone)
        JobsOperatingDialog.setTabOrder(self.chkDone, self.chkOnlyUrgent)
        JobsOperatingDialog.setTabOrder(self.chkOnlyUrgent, self.cmbOrgStructure)
        JobsOperatingDialog.setTabOrder(self.cmbOrgStructure, self.cmbSpeciality)
        JobsOperatingDialog.setTabOrder(self.cmbSpeciality, self.cmbPerson)
        JobsOperatingDialog.setTabOrder(self.cmbPerson, self.chkFilterListLength)
        JobsOperatingDialog.setTabOrder(self.chkFilterListLength, self.edtFilterListLength)
        JobsOperatingDialog.setTabOrder(self.edtFilterListLength, self.buttonBoxFilter)
        JobsOperatingDialog.setTabOrder(self.buttonBoxFilter, self.btnEnableEQueue)
        JobsOperatingDialog.setTabOrder(self.btnEnableEQueue, self.buttonBox)
        JobsOperatingDialog.setTabOrder(self.buttonBox, self.treeOrgStructure)
        JobsOperatingDialog.setTabOrder(self.treeOrgStructure, self.calendar)
        JobsOperatingDialog.setTabOrder(self.calendar, self.tblJobTickets)
        JobsOperatingDialog.setTabOrder(self.tblJobTickets, self.tabDateClientFilter)
        JobsOperatingDialog.setTabOrder(self.tabDateClientFilter, self.tblJobTypes)

    def retranslateUi(self, JobsOperatingDialog):
        JobsOperatingDialog.setWindowTitle(_translate("JobsOperatingDialog", "Выполнение работ", None))
        self.lblDateRangeFrom.setText(_translate("JobsOperatingDialog", "С", None))
        self.lblDateRangeTo.setText(_translate("JobsOperatingDialog", "По", None))
        self.tabDateClientFilter.setTabText(self.tabDateClientFilter.indexOf(self.tabDateFilter), _translate("JobsOperatingDialog", "&Дата", None))
        self.lblSuperviseInfo.setText(_translate("JobsOperatingDialog", "Не выбрана работа", None))
        self.lblTicketsCount.setText(_translate("JobsOperatingDialog", "Список пуст", None))
        self.lblCurrentTablePage.setText(_translate("JobsOperatingDialog", "Страница 1", None))
        self.btnNextTablePage.setText(_translate("JobsOperatingDialog", ">", None))
        self.btnPrevTablePage.setText(_translate("JobsOperatingDialog", "<", None))
        self.lblMaxTablePagesCount.setText(_translate("JobsOperatingDialog", "Всего страниц: ", None))
        self.btnEnableStaticFilter.setText(_translate("JobsOperatingDialog", "Фильтр", None))
        self.btnEnableEQueue.setText(_translate("JobsOperatingDialog", "Электронная очередь", None))
        self.grpPersonFilter.setTitle(_translate("JobsOperatingDialog", "Фильтр по назначившему", None))
        self.lblOrgStructure.setText(_translate("JobsOperatingDialog", "Подразделение", None))
        self.lblSpeciality.setText(_translate("JobsOperatingDialog", "Специальность", None))
        self.cmbSpeciality.setWhatsThis(_translate("JobsOperatingDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.lblPerson.setText(_translate("JobsOperatingDialog", "Врач", None))
        self.cmbPerson.setItemText(0, _translate("JobsOperatingDialog", "Врач", None))
        self.chkFilterListLength.setText(_translate("JobsOperatingDialog", "Вывести на экран постранично, количество строк:", None))
        self.chkClientLastName.setText(_translate("JobsOperatingDialog", "Фамилия", None))
        self.chkClientFirstName.setText(_translate("JobsOperatingDialog", "Имя", None))
        self.chkClientPatrName.setText(_translate("JobsOperatingDialog", "Отчество", None))
        self.lblSex.setText(_translate("JobsOperatingDialog", "Пол", None))
        self.cmbSex.setItemText(1, _translate("JobsOperatingDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("JobsOperatingDialog", "Ж", None))
        self.lblAge.setText(_translate("JobsOperatingDialog", "Возраст с", None))
        self.lblAgeTo.setText(_translate("JobsOperatingDialog", "по", None))
        self.lblAgeYears.setText(_translate("JobsOperatingDialog", "лет", None))
        self.chkClientId.setText(_translate("JobsOperatingDialog", "Код", None))
        self.chkJobTicketId.setText(_translate("JobsOperatingDialog", "Идентификатор", None))
        self.lblTissueType.setText(_translate("JobsOperatingDialog", "Биоматериал", None))
        self.chkAwaiting.setText(_translate("JobsOperatingDialog", "&Ожидающие", None))
        self.chkInProgress.setText(_translate("JobsOperatingDialog", "&Выполняемые", None))
        self.lblTakenTissueType.setText(_translate("JobsOperatingDialog", "Забранный биоматериал", None))
        self.chkDone.setText(_translate("JobsOperatingDialog", "&Законченные", None))
        self.chkOnlyUrgent.setText(_translate("JobsOperatingDialog", "Только &срочные", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from Resources.JobTicketsView import CJobTicketsView
from library.DateEdit import CDateEdit
from library.ElectronicQueue.EQControl import CEQControlWidget
from library.TableView import CTableView
from library.calendar import CCalendarWidget
from library.crbcombobox import CRBComboBox
