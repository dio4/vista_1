# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F027.ui'
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(872, 708)
        Dialog.setSizeGripEnabled(True)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.sptTopLevel = QtGui.QSplitter(Dialog)
        self.sptTopLevel.setOrientation(QtCore.Qt.Vertical)
        self.sptTopLevel.setObjectName(_fromUtf8("sptTopLevel"))
        self.txtClientInfoBrowser = CTextBrowser(self.sptTopLevel)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtClientInfoBrowser.sizePolicy().hasHeightForWidth())
        self.txtClientInfoBrowser.setSizePolicy(sizePolicy)
        self.txtClientInfoBrowser.setMinimumSize(QtCore.QSize(0, 100))
        self.txtClientInfoBrowser.setMaximumSize(QtCore.QSize(16777215, 130))
        self.txtClientInfoBrowser.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.txtClientInfoBrowser.setObjectName(_fromUtf8("txtClientInfoBrowser"))
        self.tabWidget = QtGui.QTabWidget(self.sptTopLevel)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabToken = QtGui.QWidget()
        self.tabToken.setObjectName(_fromUtf8("tabToken"))
        self.gridLayout_9 = QtGui.QGridLayout(self.tabToken)
        self.gridLayout_9.setMargin(4)
        self.gridLayout_9.setSpacing(4)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.scrollArea = QtGui.QScrollArea(self.tabToken)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 824, 1161))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter_3 = QtGui.QSplitter(self.scrollAreaWidgetContents)
        self.splitter_3.setOrientation(QtCore.Qt.Vertical)
        self.splitter_3.setObjectName(_fromUtf8("splitter_3"))
        self.frameBaseAndDiagnosises = QtGui.QFrame(self.splitter_3)
        self.frameBaseAndDiagnosises.setFrameShape(QtGui.QFrame.NoFrame)
        self.frameBaseAndDiagnosises.setFrameShadow(QtGui.QFrame.Raised)
        self.frameBaseAndDiagnosises.setObjectName(_fromUtf8("frameBaseAndDiagnosises"))
        self.gridLayout_10 = QtGui.QGridLayout(self.frameBaseAndDiagnosises)
        self.gridLayout_10.setMargin(4)
        self.gridLayout_10.setSpacing(4)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.grpBase = QtGui.QGroupBox(self.frameBaseAndDiagnosises)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpBase.sizePolicy().hasHeightForWidth())
        self.grpBase.setSizePolicy(sizePolicy)
        self.grpBase.setObjectName(_fromUtf8("grpBase"))
        self.gridLayout_4 = QtGui.QGridLayout(self.grpBase)
        self.gridLayout_4.setMargin(2)
        self.gridLayout_4.setSpacing(2)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.cmbCureMethod = CRBComboBox(self.grpBase)
        self.cmbCureMethod.setObjectName(_fromUtf8("cmbCureMethod"))
        self.gridLayout_4.addWidget(self.cmbCureMethod, 13, 2, 1, 4)
        self.cmbEventCurator = CPersonComboBoxEx(self.grpBase)
        self.cmbEventCurator.setObjectName(_fromUtf8("cmbEventCurator"))
        self.gridLayout_4.addWidget(self.cmbEventCurator, 15, 2, 1, 4)
        self.cmbPatientModel = CModelPatientComboBoxF027(self.grpBase)
        self.cmbPatientModel.setObjectName(_fromUtf8("cmbPatientModel"))
        self.gridLayout_4.addWidget(self.cmbPatientModel, 11, 2, 1, 4)
        self.cmbEventAssistant = CPersonComboBoxEx(self.grpBase)
        self.cmbEventAssistant.setObjectName(_fromUtf8("cmbEventAssistant"))
        self.gridLayout_4.addWidget(self.cmbEventAssistant, 19, 2, 1, 4)
        self.lblPersonManager = QtGui.QLabel(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPersonManager.sizePolicy().hasHeightForWidth())
        self.lblPersonManager.setSizePolicy(sizePolicy)
        self.lblPersonManager.setObjectName(_fromUtf8("lblPersonManager"))
        self.gridLayout_4.addWidget(self.lblPersonManager, 17, 0, 1, 2)
        self.chkPrimary = QtGui.QCheckBox(self.grpBase)
        self.chkPrimary.setObjectName(_fromUtf8("chkPrimary"))
        self.gridLayout_4.addWidget(self.chkPrimary, 8, 0, 1, 2)
        self.cmbPersonManager = CPersonComboBoxEx(self.grpBase)
        self.cmbPersonManager.setObjectName(_fromUtf8("cmbPersonManager"))
        self.cmbPersonManager.addItem(_fromUtf8(""))
        self.gridLayout_4.addWidget(self.cmbPersonManager, 17, 2, 1, 4)
        spacerItem = QtGui.QSpacerItem(20, 31, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem, 24, 1, 1, 3)
        self.lblPerson = QtGui.QLabel(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPerson.sizePolicy().hasHeightForWidth())
        self.lblPerson.setSizePolicy(sizePolicy)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout_4.addWidget(self.lblPerson, 15, 0, 1, 2)
        self.lblResult = QtGui.QLabel(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblResult.sizePolicy().hasHeightForWidth())
        self.lblResult.setSizePolicy(sizePolicy)
        self.lblResult.setObjectName(_fromUtf8("lblResult"))
        self.gridLayout_4.addWidget(self.lblResult, 20, 0, 1, 2)
        self.lblPatientModel = QtGui.QLabel(self.grpBase)
        self.lblPatientModel.setObjectName(_fromUtf8("lblPatientModel"))
        self.gridLayout_4.addWidget(self.lblPatientModel, 11, 0, 1, 2)
        self.btnSelectRelegateOrg = QtGui.QToolButton(self.grpBase)
        self.btnSelectRelegateOrg.setObjectName(_fromUtf8("btnSelectRelegateOrg"))
        self.gridLayout_4.addWidget(self.btnSelectRelegateOrg, 2, 5, 1, 1)
        self.chkZNOFirst = QtGui.QCheckBox(self.grpBase)
        self.chkZNOFirst.setObjectName(_fromUtf8("chkZNOFirst"))
        self.gridLayout_4.addWidget(self.chkZNOFirst, 22, 0, 1, 4)
        self.lblEndDate = QtGui.QLabel(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEndDate.sizePolicy().hasHeightForWidth())
        self.lblEndDate.setSizePolicy(sizePolicy)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout_4.addWidget(self.lblEndDate, 5, 0, 1, 1)
        self.lblEventId = QtGui.QLabel(self.grpBase)
        self.lblEventId.setObjectName(_fromUtf8("lblEventId"))
        self.gridLayout_4.addWidget(self.lblEventId, 6, 0, 1, 1)
        self.cmbQuota = CQuotaTypeComboBox(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbQuota.sizePolicy().hasHeightForWidth())
        self.cmbQuota.setSizePolicy(sizePolicy)
        self.cmbQuota.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.cmbQuota.setObjectName(_fromUtf8("cmbQuota"))
        self.gridLayout_4.addWidget(self.cmbQuota, 10, 2, 1, 4)
        self.cmbEventExternalIdValue = QtGui.QComboBox(self.grpBase)
        self.cmbEventExternalIdValue.setObjectName(_fromUtf8("cmbEventExternalIdValue"))
        self.cmbEventExternalIdValue.addItem(_fromUtf8(""))
        self.cmbEventExternalIdValue.addItem(_fromUtf8(""))
        self.gridLayout_4.addWidget(self.cmbEventExternalIdValue, 6, 1, 1, 5)
        self.frame_5 = QtGui.QFrame(self.grpBase)
        self.frame_5.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_5.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_5.setLineWidth(0)
        self.frame_5.setObjectName(_fromUtf8("frame_5"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.frame_5)
        self.horizontalLayout_5.setMargin(0)
        self.horizontalLayout_5.setSpacing(4)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.edtBegDate = CDateEdit(self.frame_5)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.horizontalLayout_5.addWidget(self.edtBegDate)
        self.edtBegTime = QtGui.QTimeEdit(self.frame_5)
        self.edtBegTime.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.edtBegTime.setCalendarPopup(False)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.horizontalLayout_5.addWidget(self.edtBegTime)
        self.gridLayout_4.addWidget(self.frame_5, 4, 1, 1, 4)
        self.frame_4 = QtGui.QFrame(self.grpBase)
        self.frame_4.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_4.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_4.setLineWidth(0)
        self.frame_4.setObjectName(_fromUtf8("frame_4"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.frame_4)
        self.horizontalLayout_4.setMargin(0)
        self.horizontalLayout_4.setSpacing(4)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.edtEndDate = CDateEdit(self.frame_4)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.horizontalLayout_4.addWidget(self.edtEndDate)
        self.edtEndTime = QtGui.QTimeEdit(self.frame_4)
        self.edtEndTime.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.edtEndTime.setCalendarPopup(False)
        self.edtEndTime.setObjectName(_fromUtf8("edtEndTime"))
        self.horizontalLayout_4.addWidget(self.edtEndTime)
        self.gridLayout_4.addWidget(self.frame_4, 5, 1, 1, 4)
        spacerItem1 = QtGui.QSpacerItem(21, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 4, 5, 1, 1)
        self.cmbCureType = CRBComboBox(self.grpBase)
        self.cmbCureType.setObjectName(_fromUtf8("cmbCureType"))
        self.gridLayout_4.addWidget(self.cmbCureType, 12, 2, 1, 4)
        self.lblPersonCurator = QtGui.QLabel(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPersonCurator.sizePolicy().hasHeightForWidth())
        self.lblPersonCurator.setSizePolicy(sizePolicy)
        self.lblPersonCurator.setObjectName(_fromUtf8("lblPersonCurator"))
        self.gridLayout_4.addWidget(self.lblPersonCurator, 18, 0, 1, 1)
        self.cmbOrder = CRBComboBox(self.grpBase)
        self.cmbOrder.setObjectName(_fromUtf8("cmbOrder"))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.setItemText(0, _fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.cmbOrder.addItem(_fromUtf8(""))
        self.gridLayout_4.addWidget(self.cmbOrder, 9, 0, 1, 6)
        self.lblOrder = QtGui.QLabel(self.grpBase)
        self.lblOrder.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblOrder.setObjectName(_fromUtf8("lblOrder"))
        self.gridLayout_4.addWidget(self.lblOrder, 8, 3, 1, 3)
        self.chkZNOMorph = QtGui.QCheckBox(self.grpBase)
        self.chkZNOMorph.setObjectName(_fromUtf8("chkZNOMorph"))
        self.gridLayout_4.addWidget(self.chkZNOMorph, 23, 0, 1, 4)
        self.cmbPerson = CPersonComboBoxEx(self.grpBase)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridLayout_4.addWidget(self.cmbPerson, 18, 2, 1, 4)
        self.cmbResult = CRBComboBox(self.grpBase)
        self.cmbResult.setObjectName(_fromUtf8("cmbResult"))
        self.cmbResult.addItem(_fromUtf8(""))
        self.gridLayout_4.addWidget(self.cmbResult, 20, 2, 1, 4)
        self.cmbRelegateOrg = CPolyclinicComboBox(self.grpBase)
        self.cmbRelegateOrg.setEnabled(True)
        self.cmbRelegateOrg.setObjectName(_fromUtf8("cmbRelegateOrg"))
        self.gridLayout_4.addWidget(self.cmbRelegateOrg, 2, 1, 1, 4)
        self.chkExposeConfirmed = QtGui.QCheckBox(self.grpBase)
        self.chkExposeConfirmed.setObjectName(_fromUtf8("chkExposeConfirmed"))
        self.gridLayout_4.addWidget(self.chkExposeConfirmed, 1, 0, 1, 6)
        self.lblBegDate = QtGui.QLabel(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblBegDate.sizePolicy().hasHeightForWidth())
        self.lblBegDate.setSizePolicy(sizePolicy)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout_4.addWidget(self.lblBegDate, 4, 0, 1, 1)
        self.lblCureType = QtGui.QLabel(self.grpBase)
        self.lblCureType.setObjectName(_fromUtf8("lblCureType"))
        self.gridLayout_4.addWidget(self.lblCureType, 12, 0, 1, 2)
        self.label_2 = QtGui.QLabel(self.grpBase)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_4.addWidget(self.label_2, 10, 0, 1, 2)
        self.cmbPersonMedicineHead = CPersonComboBoxEx(self.grpBase)
        self.cmbPersonMedicineHead.setObjectName(_fromUtf8("cmbPersonMedicineHead"))
        self.cmbPersonMedicineHead.addItem(_fromUtf8(""))
        self.gridLayout_4.addWidget(self.cmbPersonMedicineHead, 16, 2, 1, 4)
        self.lblPersonMedicineHead = QtGui.QLabel(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPersonMedicineHead.sizePolicy().hasHeightForWidth())
        self.lblPersonMedicineHead.setSizePolicy(sizePolicy)
        self.lblPersonMedicineHead.setObjectName(_fromUtf8("lblPersonMedicineHead"))
        self.gridLayout_4.addWidget(self.lblPersonMedicineHead, 16, 0, 1, 2)
        self.label = QtGui.QLabel(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_4.addWidget(self.label, 21, 0, 1, 2)
        self.lblEventAssistantIdValue = QtGui.QLabel(self.grpBase)
        self.lblEventAssistantIdValue.setObjectName(_fromUtf8("lblEventAssistantIdValue"))
        self.gridLayout_4.addWidget(self.lblEventAssistantIdValue, 19, 0, 1, 2)
        self.lblCureMethod = QtGui.QLabel(self.grpBase)
        self.lblCureMethod.setObjectName(_fromUtf8("lblCureMethod"))
        self.gridLayout_4.addWidget(self.lblCureMethod, 13, 0, 1, 2)
        self.edtPlanningDate = CDateEdit(self.grpBase)
        self.edtPlanningDate.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtPlanningDate.sizePolicy().hasHeightForWidth())
        self.edtPlanningDate.setSizePolicy(sizePolicy)
        self.edtPlanningDate.setObjectName(_fromUtf8("edtPlanningDate"))
        self.gridLayout_4.addWidget(self.edtPlanningDate, 21, 2, 1, 4)
        self.lblRelegateOrg = QtGui.QLabel(self.grpBase)
        self.lblRelegateOrg.setObjectName(_fromUtf8("lblRelegateOrg"))
        self.gridLayout_4.addWidget(self.lblRelegateOrg, 2, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(21, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem2, 5, 5, 1, 1)
        self.chkIsClosed = QtGui.QCheckBox(self.grpBase)
        self.chkIsClosed.setObjectName(_fromUtf8("chkIsClosed"))
        self.gridLayout_4.addWidget(self.chkIsClosed, 0, 0, 1, 6)
        self.gridLayout_10.addWidget(self.grpBase, 0, 0, 1, 1)
        self.frame_6 = QtGui.QFrame(self.frameBaseAndDiagnosises)
        self.frame_6.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_6.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_6.setObjectName(_fromUtf8("frame_6"))
        self.gridLayout_11 = QtGui.QGridLayout(self.frame_6)
        self.gridLayout_11.setMargin(4)
        self.gridLayout_11.setSpacing(4)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.grpActions = QtGui.QGroupBox(self.frame_6)
        self.grpActions.setObjectName(_fromUtf8("grpActions"))
        self.gridLayout_12 = QtGui.QGridLayout(self.grpActions)
        self.gridLayout_12.setMargin(4)
        self.gridLayout_12.setSpacing(4)
        self.gridLayout_12.setObjectName(_fromUtf8("gridLayout_12"))
        self.tblActionProperties = CActionPropertiesTableView(self.grpActions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.tblActionProperties.sizePolicy().hasHeightForWidth())
        self.tblActionProperties.setSizePolicy(sizePolicy)
        self.tblActionProperties.setObjectName(_fromUtf8("tblActionProperties"))
        self.gridLayout_12.addWidget(self.tblActionProperties, 0, 0, 1, 1)
        self.gridLayout_11.addWidget(self.grpActions, 0, 0, 1, 1)
        self.gridLayout_10.addWidget(self.frame_6, 0, 1, 1, 1)
        self.splitter_4 = QtGui.QSplitter(self.splitter_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_4.sizePolicy().hasHeightForWidth())
        self.splitter_4.setSizePolicy(sizePolicy)
        self.splitter_4.setFrameShape(QtGui.QFrame.NoFrame)
        self.splitter_4.setFrameShadow(QtGui.QFrame.Plain)
        self.splitter_4.setLineWidth(0)
        self.splitter_4.setOrientation(QtCore.Qt.Vertical)
        self.splitter_4.setChildrenCollapsible(False)
        self.splitter_4.setObjectName(_fromUtf8("splitter_4"))
        self.grpInspections_2 = QtGui.QGroupBox(self.splitter_4)
        self.grpInspections_2.setObjectName(_fromUtf8("grpInspections_2"))
        self.gridLayout_13 = QtGui.QGridLayout(self.grpInspections_2)
        self.gridLayout_13.setMargin(2)
        self.gridLayout_13.setSpacing(2)
        self.gridLayout_13.setObjectName(_fromUtf8("gridLayout_13"))
        self.tblPreliminaryDiagnostics = CDiagnosticsInDocTableView(self.grpInspections_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblPreliminaryDiagnostics.sizePolicy().hasHeightForWidth())
        self.tblPreliminaryDiagnostics.setSizePolicy(sizePolicy)
        self.tblPreliminaryDiagnostics.setMinimumSize(QtCore.QSize(0, 100))
        self.tblPreliminaryDiagnostics.setObjectName(_fromUtf8("tblPreliminaryDiagnostics"))
        self.gridLayout_13.addWidget(self.tblPreliminaryDiagnostics, 0, 0, 1, 1)
        self.grpInspections = QtGui.QGroupBox(self.splitter_4)
        self.grpInspections.setObjectName(_fromUtf8("grpInspections"))
        self.gridLayout_14 = QtGui.QGridLayout(self.grpInspections)
        self.gridLayout_14.setMargin(2)
        self.gridLayout_14.setSpacing(2)
        self.gridLayout_14.setObjectName(_fromUtf8("gridLayout_14"))
        self.tblFinalDiagnostics = CDiagnosticsInDocTableView(self.grpInspections)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblFinalDiagnostics.sizePolicy().hasHeightForWidth())
        self.tblFinalDiagnostics.setSizePolicy(sizePolicy)
        self.tblFinalDiagnostics.setMinimumSize(QtCore.QSize(0, 100))
        self.tblFinalDiagnostics.setObjectName(_fromUtf8("tblFinalDiagnostics"))
        self.gridLayout_14.addWidget(self.tblFinalDiagnostics, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.splitter_3)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_9.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabToken, _fromUtf8(""))
        self.tabAmbCard = CAmbCardPage()
        self.tabAmbCard.setObjectName(_fromUtf8("tabAmbCard"))
        self.tabWidget.addTab(self.tabAmbCard, _fromUtf8(""))
        self.tabNotes = CEventNotesPageProtocol()
        self.tabNotes.setMaximumSize(QtCore.QSize(838, 16777215))
        self.tabNotes.setObjectName(_fromUtf8("tabNotes"))
        self.tabWidget.addTab(self.tabNotes, _fromUtf8(""))
        self.verticalLayout_2.addWidget(self.sptTopLevel)
        self.widget = QtGui.QWidget(Dialog)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblProlongateEvent = QtGui.QLabel(self.widget)
        self.lblProlongateEvent.setText(_fromUtf8(""))
        self.lblProlongateEvent.setObjectName(_fromUtf8("lblProlongateEvent"))
        self.horizontalLayout.addWidget(self.lblProlongateEvent)
        self.lblValueExternalId = QtGui.QLabel(self.widget)
        self.lblValueExternalId.setText(_fromUtf8(""))
        self.lblValueExternalId.setObjectName(_fromUtf8("lblValueExternalId"))
        self.horizontalLayout.addWidget(self.lblValueExternalId)
        self.buttonBox = QtGui.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addWidget(self.widget)
        self.statusBar = QtGui.QStatusBar(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusBar.sizePolicy().hasHeightForWidth())
        self.statusBar.setSizePolicy(sizePolicy)
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        self.verticalLayout_2.addWidget(self.statusBar)
        self.lblPersonManager.setBuddy(self.cmbPersonManager)
        self.lblPerson.setBuddy(self.cmbEventCurator)
        self.lblResult.setBuddy(self.cmbResult)
        self.lblPatientModel.setBuddy(self.cmbPatientModel)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblPersonCurator.setBuddy(self.cmbPerson)
        self.lblOrder.setBuddy(self.cmbOrder)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblCureType.setBuddy(self.cmbCureType)
        self.lblPersonMedicineHead.setBuddy(self.cmbPersonMedicineHead)
        self.lblEventAssistantIdValue.setBuddy(self.cmbEventAssistant)
        self.lblCureMethod.setBuddy(self.cmbCureMethod)
        self.lblRelegateOrg.setBuddy(self.cmbRelegateOrg)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.tabWidget, self.scrollArea)
        Dialog.setTabOrder(self.scrollArea, self.chkIsClosed)
        Dialog.setTabOrder(self.chkIsClosed, self.chkExposeConfirmed)
        Dialog.setTabOrder(self.chkExposeConfirmed, self.cmbRelegateOrg)
        Dialog.setTabOrder(self.cmbRelegateOrg, self.btnSelectRelegateOrg)
        Dialog.setTabOrder(self.btnSelectRelegateOrg, self.edtBegDate)
        Dialog.setTabOrder(self.edtBegDate, self.edtBegTime)
        Dialog.setTabOrder(self.edtBegTime, self.edtEndDate)
        Dialog.setTabOrder(self.edtEndDate, self.edtEndTime)
        Dialog.setTabOrder(self.edtEndTime, self.cmbEventExternalIdValue)
        Dialog.setTabOrder(self.cmbEventExternalIdValue, self.chkPrimary)
        Dialog.setTabOrder(self.chkPrimary, self.cmbOrder)
        Dialog.setTabOrder(self.cmbOrder, self.cmbQuota)
        Dialog.setTabOrder(self.cmbQuota, self.cmbPatientModel)
        Dialog.setTabOrder(self.cmbPatientModel, self.cmbCureType)
        Dialog.setTabOrder(self.cmbCureType, self.cmbCureMethod)
        Dialog.setTabOrder(self.cmbCureMethod, self.cmbEventCurator)
        Dialog.setTabOrder(self.cmbEventCurator, self.cmbPersonMedicineHead)
        Dialog.setTabOrder(self.cmbPersonMedicineHead, self.cmbPersonManager)
        Dialog.setTabOrder(self.cmbPersonManager, self.cmbPerson)
        Dialog.setTabOrder(self.cmbPerson, self.cmbEventAssistant)
        Dialog.setTabOrder(self.cmbEventAssistant, self.cmbResult)
        Dialog.setTabOrder(self.cmbResult, self.edtPlanningDate)
        Dialog.setTabOrder(self.edtPlanningDate, self.chkZNOFirst)
        Dialog.setTabOrder(self.chkZNOFirst, self.chkZNOMorph)
        Dialog.setTabOrder(self.chkZNOMorph, self.tblActionProperties)
        Dialog.setTabOrder(self.tblActionProperties, self.tblPreliminaryDiagnostics)
        Dialog.setTabOrder(self.tblPreliminaryDiagnostics, self.tblFinalDiagnostics)
        Dialog.setTabOrder(self.tblFinalDiagnostics, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.txtClientInfoBrowser.setWhatsThis(_translate("Dialog", "Описание пациента", None))
        self.txtClientInfoBrowser.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p></body></html>", None))
        self.grpBase.setTitle(_translate("Dialog", "Протокол по ВМП/ВМП из ОМС", None))
        self.cmbEventAssistant.setWhatsThis(_translate("Dialog", "ассистент События", None))
        self.lblPersonManager.setText(_translate("Dialog", "Зав.отд.", None))
        self.chkPrimary.setText(_translate("Dialog", "Пе&рвичный", None))
        self.cmbPersonManager.setWhatsThis(_translate("Dialog", "ответственный за Действие \"протокол\"", None))
        self.cmbPersonManager.setItemText(0, _translate("Dialog", "Врач", None))
        self.lblPerson.setText(_translate("Dialog", "Председатель", None))
        self.lblResult.setText(_translate("Dialog", "Результат", None))
        self.lblPatientModel.setText(_translate("Dialog", "Модель пациента", None))
        self.btnSelectRelegateOrg.setText(_translate("Dialog", "...", None))
        self.chkZNOFirst.setToolTip(_translate("Dialog", "ЗНО установлен впервые", None))
        self.chkZNOFirst.setText(_translate("Dialog", "ЗНО уст. впервые", None))
        self.lblEndDate.setText(_translate("Dialog", "Закрыт", None))
        self.lblEventId.setText(_translate("Dialog", "Тип", None))
        self.cmbEventExternalIdValue.setItemText(0, _translate("Dialog", "КС", None))
        self.cmbEventExternalIdValue.setItemText(1, _translate("Dialog", "ДС", None))
        self.edtBegDate.setWhatsThis(_translate("Dialog", "дата начала осмотра", None))
        self.edtBegTime.setDisplayFormat(_translate("Dialog", "HH:mm", None))
        self.edtEndDate.setWhatsThis(_translate("Dialog", "дата окончания осмотра", None))
        self.edtEndTime.setDisplayFormat(_translate("Dialog", "HH:mm", None))
        self.lblPersonCurator.setText(_translate("Dialog", "Лечащий врач", None))
        self.cmbOrder.setItemText(1, _translate("Dialog", "Плановый", None))
        self.cmbOrder.setItemText(2, _translate("Dialog", "Экстренный", None))
        self.cmbOrder.setItemText(3, _translate("Dialog", "Самообращение", None))
        self.cmbOrder.setItemText(4, _translate("Dialog", "Принудительный", None))
        self.cmbOrder.setItemText(5, _translate("Dialog", "Неотложный", None))
        self.lblOrder.setText(_translate("Dialog", "П&орядок", None))
        self.chkZNOMorph.setToolTip(_translate("Dialog", "ЗНО потдверждён морфологически", None))
        self.chkZNOMorph.setText(_translate("Dialog", "ЗНО подтв. морф-ки", None))
        self.cmbPerson.setWhatsThis(_translate("Dialog", "врач отвечающий за осмотр (терапевт)", None))
        self.cmbPerson.setItemText(0, _translate("Dialog", "Врач", None))
        self.cmbResult.setWhatsThis(_translate("Dialog", "результат осмотра", None))
        self.cmbResult.setItemText(0, _translate("Dialog", "Результат", None))
        self.chkExposeConfirmed.setText(_translate("Dialog", "Добавить к выставлению", None))
        self.lblBegDate.setText(_translate("Dialog", "Открыт", None))
        self.lblCureType.setText(_translate("Dialog", "Вид лечения", None))
        self.label_2.setText(_translate("Dialog", "Квота", None))
        self.cmbPersonMedicineHead.setWhatsThis(_translate("Dialog", "назначивший действие \"протокол\"", None))
        self.cmbPersonMedicineHead.setItemText(0, _translate("Dialog", "Врач", None))
        self.lblPersonMedicineHead.setText(_translate("Dialog", "Зам.гл.вр. по мед части", None))
        self.label.setText(_translate("Dialog", "Дата госпитализации", None))
        self.lblEventAssistantIdValue.setText(_translate("Dialog", "Зам.гл.врача по КЭР", None))
        self.lblCureMethod.setText(_translate("Dialog", "Метод лечения", None))
        self.lblRelegateOrg.setText(_translate("Dialog", "Направитель", None))
        self.chkIsClosed.setText(_translate("Dialog", "Карта заполнена", None))
        self.grpActions.setTitle(_translate("Dialog", "Протокол", None))
        self.grpInspections_2.setTitle(_translate("Dialog", "&Предварительный диагноз", None))
        self.grpInspections.setTitle(_translate("Dialog", "&Заключительный диагноз", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabToken), _translate("Dialog", "Протокол", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAmbCard), _translate("Dialog", "Мед.&карта", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabNotes), _translate("Dialog", "Приме&чания", None))
        self.statusBar.setToolTip(_translate("Dialog", "A status bar", None))
        self.statusBar.setWhatsThis(_translate("Dialog", "A status bar.", None))

from Events.ActionPropertiesTable import CActionPropertiesTableView
from Events.AmbCardPage import CAmbCardPage
from Events.EventDiagnosticsTable import CDiagnosticsInDocTableView
from Forms.F027.EventNotesPageProtocol import CEventNotesPageProtocol
from Orgs.OrgComboBox import CPolyclinicComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from Quoting.QuotaTypeComboBox import CQuotaTypeComboBox
from library.DateEdit import CDateEdit
from library.ModelPatientComboBox import CModelPatientComboBoxF027
from library.TextBrowser import CTextBrowser
from library.crbcombobox import CRBComboBox
