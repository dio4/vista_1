# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F131.ui'
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
        Dialog.resize(919, 628)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
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
        self.gridLayout = QtGui.QGridLayout(self.tabToken)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.scrollArea = QtGui.QScrollArea(self.tabToken)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 867, 1115))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.splitter_3 = QtGui.QSplitter(self.scrollAreaWidgetContents)
        self.splitter_3.setOrientation(QtCore.Qt.Vertical)
        self.splitter_3.setObjectName(_fromUtf8("splitter_3"))
        self.layoutWidget = QtGui.QWidget(self.splitter_3)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.grpBase = QtGui.QGroupBox(self.layoutWidget)
        self.grpBase.setObjectName(_fromUtf8("grpBase"))
        self.gridLayout_2 = QtGui.QGridLayout(self.grpBase)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblNextDate = QtGui.QLabel(self.grpBase)
        self.lblNextDate.setObjectName(_fromUtf8("lblNextDate"))
        self.gridLayout_2.addWidget(self.lblNextDate, 5, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(self.grpBase)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout_2.addWidget(self.lblEndDate, 4, 0, 1, 1)
        self.cmbContract = CContractComboBox(self.grpBase)
        self.cmbContract.setObjectName(_fromUtf8("cmbContract"))
        self.cmbContract.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.cmbContract, 0, 0, 1, 3)
        self.lblBegDate = QtGui.QLabel(self.grpBase)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout_2.addWidget(self.lblBegDate, 3, 0, 1, 1)
        self.lblResult = QtGui.QLabel(self.grpBase)
        self.lblResult.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblResult.setObjectName(_fromUtf8("lblResult"))
        self.gridLayout_2.addWidget(self.lblResult, 8, 2, 1, 1)
        self.cmbResult = CRBComboBox(self.grpBase)
        self.cmbResult.setObjectName(_fromUtf8("cmbResult"))
        self.cmbResult.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.cmbResult, 9, 0, 1, 3)
        self.cmbPerson = CPersonComboBoxEx(self.grpBase)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.cmbPerson, 7, 0, 1, 3)
        self.chkPrimary = QtGui.QCheckBox(self.grpBase)
        self.chkPrimary.setObjectName(_fromUtf8("chkPrimary"))
        self.gridLayout_2.addWidget(self.chkPrimary, 8, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(16, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 16, 0, 1, 2)
        self.lblPerson = QtGui.QLabel(self.grpBase)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout_2.addWidget(self.lblPerson, 6, 0, 1, 3)
        self.chkZNOMorph = QtGui.QCheckBox(self.grpBase)
        self.chkZNOMorph.setObjectName(_fromUtf8("chkZNOMorph"))
        self.gridLayout_2.addWidget(self.chkZNOMorph, 14, 0, 1, 3)
        self.chkExposeConfirmed = QtGui.QCheckBox(self.grpBase)
        self.chkExposeConfirmed.setObjectName(_fromUtf8("chkExposeConfirmed"))
        self.gridLayout_2.addWidget(self.chkExposeConfirmed, 2, 0, 1, 3)
        self.cmbGoal = CRBComboBox(self.grpBase)
        self.cmbGoal.setObjectName(_fromUtf8("cmbGoal"))
        self.gridLayout_2.addWidget(self.cmbGoal, 10, 1, 1, 2)
        self.lblGoal = QtGui.QLabel(self.grpBase)
        self.lblGoal.setObjectName(_fromUtf8("lblGoal"))
        self.gridLayout_2.addWidget(self.lblGoal, 10, 0, 1, 1)
        self.chkZNOFirst = QtGui.QCheckBox(self.grpBase)
        self.chkZNOFirst.setObjectName(_fromUtf8("chkZNOFirst"))
        self.gridLayout_2.addWidget(self.chkZNOFirst, 15, 0, 1, 3)
        self.chkDispByMobileTeam = QtGui.QCheckBox(self.grpBase)
        self.chkDispByMobileTeam.setToolTip(_fromUtf8(""))
        self.chkDispByMobileTeam.setWhatsThis(_fromUtf8(""))
        self.chkDispByMobileTeam.setObjectName(_fromUtf8("chkDispByMobileTeam"))
        self.gridLayout_2.addWidget(self.chkDispByMobileTeam, 11, 0, 1, 3)
        self.gbLittleStrangerFlag = QtGui.QGroupBox(self.grpBase)
        self.gbLittleStrangerFlag.setCheckable(True)
        self.gbLittleStrangerFlag.setChecked(False)
        self.gbLittleStrangerFlag.setObjectName(_fromUtf8("gbLittleStrangerFlag"))
        self.gridLayout_5 = QtGui.QGridLayout(self.gbLittleStrangerFlag)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.lblChildBirthDate = QtGui.QLabel(self.gbLittleStrangerFlag)
        self.lblChildBirthDate.setObjectName(_fromUtf8("lblChildBirthDate"))
        self.gridLayout_5.addWidget(self.lblChildBirthDate, 1, 0, 1, 1)
        self.lblChildSex = QtGui.QLabel(self.gbLittleStrangerFlag)
        self.lblChildSex.setObjectName(_fromUtf8("lblChildSex"))
        self.gridLayout_5.addWidget(self.lblChildSex, 0, 2, 1, 1)
        self.cmbChildSex = QtGui.QComboBox(self.gbLittleStrangerFlag)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbChildSex.sizePolicy().hasHeightForWidth())
        self.cmbChildSex.setSizePolicy(sizePolicy)
        self.cmbChildSex.setObjectName(_fromUtf8("cmbChildSex"))
        self.cmbChildSex.addItem(_fromUtf8(""))
        self.cmbChildSex.setItemText(0, _fromUtf8(""))
        self.cmbChildSex.addItem(_fromUtf8(""))
        self.cmbChildSex.addItem(_fromUtf8(""))
        self.gridLayout_5.addWidget(self.cmbChildSex, 0, 3, 1, 1)
        self.chkMultipleBirths = QtGui.QCheckBox(self.gbLittleStrangerFlag)
        self.chkMultipleBirths.setObjectName(_fromUtf8("chkMultipleBirths"))
        self.gridLayout_5.addWidget(self.chkMultipleBirths, 4, 0, 1, 2)
        self.edtChildBirthDate = CDateEdit(self.gbLittleStrangerFlag)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtChildBirthDate.sizePolicy().hasHeightForWidth())
        self.edtChildBirthDate.setSizePolicy(sizePolicy)
        self.edtChildBirthDate.setCalendarPopup(True)
        self.edtChildBirthDate.setObjectName(_fromUtf8("edtChildBirthDate"))
        self.gridLayout_5.addWidget(self.edtChildBirthDate, 1, 2, 1, 2)
        self.lblChildNumber = QtGui.QLabel(self.gbLittleStrangerFlag)
        self.lblChildNumber.setObjectName(_fromUtf8("lblChildNumber"))
        self.gridLayout_5.addWidget(self.lblChildNumber, 0, 0, 1, 1)
        self.sbChildNumber = QtGui.QSpinBox(self.gbLittleStrangerFlag)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sbChildNumber.sizePolicy().hasHeightForWidth())
        self.sbChildNumber.setSizePolicy(sizePolicy)
        self.sbChildNumber.setMinimum(1)
        self.sbChildNumber.setObjectName(_fromUtf8("sbChildNumber"))
        self.gridLayout_5.addWidget(self.sbChildNumber, 0, 1, 1, 1)
        self.lblBirthWeight = QtGui.QLabel(self.gbLittleStrangerFlag)
        self.lblBirthWeight.setObjectName(_fromUtf8("lblBirthWeight"))
        self.gridLayout_5.addWidget(self.lblBirthWeight, 2, 0, 1, 2)
        self.sbBirthWeight = QtGui.QDoubleSpinBox(self.gbLittleStrangerFlag)
        self.sbBirthWeight.setMaximum(9999.99)
        self.sbBirthWeight.setObjectName(_fromUtf8("sbBirthWeight"))
        self.gridLayout_5.addWidget(self.sbBirthWeight, 2, 2, 1, 2)
        self.gridLayout_2.addWidget(self.gbLittleStrangerFlag, 12, 0, 1, 3)
        self.frmBegDateTime = QtGui.QFrame(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frmBegDateTime.sizePolicy().hasHeightForWidth())
        self.frmBegDateTime.setSizePolicy(sizePolicy)
        self.frmBegDateTime.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmBegDateTime.setFrameShadow(QtGui.QFrame.Plain)
        self.frmBegDateTime.setLineWidth(0)
        self.frmBegDateTime.setObjectName(_fromUtf8("frmBegDateTime"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.frmBegDateTime)
        self.horizontalLayout_5.setMargin(0)
        self.horizontalLayout_5.setSpacing(4)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.edtBegDate = CDateEdit(self.frmBegDateTime)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.horizontalLayout_5.addWidget(self.edtBegDate)
        self.edtBegTime = QtGui.QTimeEdit(self.frmBegDateTime)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegTime.sizePolicy().hasHeightForWidth())
        self.edtBegTime.setSizePolicy(sizePolicy)
        self.edtBegTime.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.horizontalLayout_5.addWidget(self.edtBegTime)
        self.gridLayout_2.addWidget(self.frmBegDateTime, 3, 1, 1, 2)
        self.frmNextDateTime = QtGui.QFrame(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frmNextDateTime.sizePolicy().hasHeightForWidth())
        self.frmNextDateTime.setSizePolicy(sizePolicy)
        self.frmNextDateTime.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmNextDateTime.setFrameShadow(QtGui.QFrame.Plain)
        self.frmNextDateTime.setLineWidth(0)
        self.frmNextDateTime.setObjectName(_fromUtf8("frmNextDateTime"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.frmNextDateTime)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setSpacing(4)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.edtNextDate = CDateEdit(self.frmNextDateTime)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtNextDate.sizePolicy().hasHeightForWidth())
        self.edtNextDate.setSizePolicy(sizePolicy)
        self.edtNextDate.setCalendarPopup(True)
        self.edtNextDate.setObjectName(_fromUtf8("edtNextDate"))
        self.horizontalLayout_3.addWidget(self.edtNextDate)
        self.gridLayout_2.addWidget(self.frmNextDateTime, 5, 1, 1, 2)
        self.frmEndDateTime = QtGui.QFrame(self.grpBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frmEndDateTime.sizePolicy().hasHeightForWidth())
        self.frmEndDateTime.setSizePolicy(sizePolicy)
        self.frmEndDateTime.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmEndDateTime.setFrameShadow(QtGui.QFrame.Plain)
        self.frmEndDateTime.setLineWidth(0)
        self.frmEndDateTime.setObjectName(_fromUtf8("frmEndDateTime"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.frmEndDateTime)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.edtEndDate = CDateEdit(self.frmEndDateTime)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.horizontalLayout_2.addWidget(self.edtEndDate)
        self.edtEndTime = QtGui.QTimeEdit(self.frmEndDateTime)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndTime.sizePolicy().hasHeightForWidth())
        self.edtEndTime.setSizePolicy(sizePolicy)
        self.edtEndTime.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.edtEndTime.setObjectName(_fromUtf8("edtEndTime"))
        self.horizontalLayout_2.addWidget(self.edtEndTime)
        self.gridLayout_2.addWidget(self.frmEndDateTime, 4, 1, 1, 2)
        self.chkIsClosed = QtGui.QCheckBox(self.grpBase)
        self.chkIsClosed.setObjectName(_fromUtf8("chkIsClosed"))
        self.gridLayout_2.addWidget(self.chkIsClosed, 1, 0, 1, 3)
        self.horizontalLayout_4.addWidget(self.grpBase)
        self.grpWork = QtGui.QGroupBox(self.layoutWidget)
        self.grpWork.setObjectName(_fromUtf8("grpWork"))
        self._2 = QtGui.QGridLayout(self.grpWork)
        self._2.setMargin(4)
        self._2.setSpacing(4)
        self._2.setObjectName(_fromUtf8("_2"))
        self.btnSelectWorkOrganisation = QtGui.QToolButton(self.grpWork)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSelectWorkOrganisation.sizePolicy().hasHeightForWidth())
        self.btnSelectWorkOrganisation.setSizePolicy(sizePolicy)
        self.btnSelectWorkOrganisation.setObjectName(_fromUtf8("btnSelectWorkOrganisation"))
        self._2.addWidget(self.btnSelectWorkOrganisation, 0, 3, 1, 1)
        self.cmbWorkOKVED = COKVEDComboBox(self.grpWork)
        self.cmbWorkOKVED.setObjectName(_fromUtf8("cmbWorkOKVED"))
        self._2.addWidget(self.cmbWorkOKVED, 5, 1, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(111, 21, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self._2.addItem(spacerItem1, 8, 0, 1, 2)
        self.edtPrevDate = CDateEdit(self.grpWork)
        self.edtPrevDate.setCalendarPopup(True)
        self.edtPrevDate.setObjectName(_fromUtf8("edtPrevDate"))
        self._2.addWidget(self.edtPrevDate, 7, 2, 1, 2)
        self.edtWorkStage = QtGui.QSpinBox(self.grpWork)
        self.edtWorkStage.setObjectName(_fromUtf8("edtWorkStage"))
        self._2.addWidget(self.edtWorkStage, 6, 1, 1, 3)
        self.lblWorkPost = QtGui.QLabel(self.grpWork)
        self.lblWorkPost.setObjectName(_fromUtf8("lblWorkPost"))
        self._2.addWidget(self.lblWorkPost, 4, 0, 1, 1)
        self.lblWorkOKVED = QtGui.QLabel(self.grpWork)
        self.lblWorkOKVED.setObjectName(_fromUtf8("lblWorkOKVED"))
        self._2.addWidget(self.lblWorkOKVED, 5, 0, 1, 1)
        self.label_7 = QtGui.QLabel(self.grpWork)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self._2.addWidget(self.label_7, 7, 0, 1, 2)
        self.lblWorkStage = QtGui.QLabel(self.grpWork)
        self.lblWorkStage.setObjectName(_fromUtf8("lblWorkStage"))
        self._2.addWidget(self.lblWorkStage, 6, 0, 1, 1)
        self.lblKPP = QtGui.QLabel(self.grpWork)
        self.lblKPP.setObjectName(_fromUtf8("lblKPP"))
        self._2.addWidget(self.lblKPP, 2, 0, 1, 4)
        self.lblINN = QtGui.QLabel(self.grpWork)
        self.lblINN.setObjectName(_fromUtf8("lblINN"))
        self._2.addWidget(self.lblINN, 1, 0, 1, 4)
        self.edtWorkPost = QtGui.QLineEdit(self.grpWork)
        self.edtWorkPost.setObjectName(_fromUtf8("edtWorkPost"))
        self._2.addWidget(self.edtWorkPost, 4, 1, 1, 3)
        self.cmbWorkOrganisation = COrgComboBox(self.grpWork)
        self.cmbWorkOrganisation.setObjectName(_fromUtf8("cmbWorkOrganisation"))
        self._2.addWidget(self.cmbWorkOrganisation, 0, 0, 1, 3)
        self.lblOGRN = QtGui.QLabel(self.grpWork)
        self.lblOGRN.setObjectName(_fromUtf8("lblOGRN"))
        self._2.addWidget(self.lblOGRN, 3, 0, 1, 4)
        self.horizontalLayout_4.addWidget(self.grpWork)
        self.tblWorkHurt = QtGui.QGroupBox(self.layoutWidget)
        self.tblWorkHurt.setObjectName(_fromUtf8("tblWorkHurt"))
        self._3 = QtGui.QGridLayout(self.tblWorkHurt)
        self._3.setMargin(0)
        self._3.setSpacing(0)
        self._3.setObjectName(_fromUtf8("_3"))
        self.splitter = QtGui.QSplitter(self.tblWorkHurt)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tblWorkHurts = CWorkHurtTableView(self.splitter)
        self.tblWorkHurts.setObjectName(_fromUtf8("tblWorkHurts"))
        self.tblWorkHurtFactors = CInDocTableView(self.splitter)
        self.tblWorkHurtFactors.setObjectName(_fromUtf8("tblWorkHurtFactors"))
        self._3.addWidget(self.splitter, 0, 0, 1, 1)
        self.horizontalLayout_4.addWidget(self.tblWorkHurt)
        self.splitter_2 = QtGui.QSplitter(self.splitter_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_2.sizePolicy().hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.grpInspections = QtGui.QGroupBox(self.splitter_2)
        self.grpInspections.setObjectName(_fromUtf8("grpInspections"))
        self._4 = QtGui.QVBoxLayout(self.grpInspections)
        self._4.setMargin(4)
        self._4.setSpacing(4)
        self._4.setObjectName(_fromUtf8("_4"))
        self.tblFinalDiagnostics = CInDocTableView(self.grpInspections)
        self.tblFinalDiagnostics.setMinimumSize(QtCore.QSize(0, 100))
        self.tblFinalDiagnostics.setObjectName(_fromUtf8("tblFinalDiagnostics"))
        self._4.addWidget(self.tblFinalDiagnostics)
        self.grpActions = QtGui.QGroupBox(self.splitter_2)
        self.grpActions.setObjectName(_fromUtf8("grpActions"))
        self._5 = QtGui.QGridLayout(self.grpActions)
        self._5.setMargin(4)
        self._5.setSpacing(4)
        self._5.setObjectName(_fromUtf8("_5"))
        self.tblActions = CInDocTableView(self.grpActions)
        self.tblActions.setMinimumSize(QtCore.QSize(0, 100))
        self.tblActions.setObjectName(_fromUtf8("tblActions"))
        self._5.addWidget(self.tblActions, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.splitter_3)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabToken, _fromUtf8(""))
        self.tabMes = CFastEventMesPage()
        self.tabMes.setObjectName(_fromUtf8("tabMes"))
        self.tabWidget.addTab(self.tabMes, _fromUtf8(""))
        self.tabStatus = CFastActionsPage()
        self.tabStatus.setObjectName(_fromUtf8("tabStatus"))
        self.tabWidget.addTab(self.tabStatus, _fromUtf8(""))
        self.tabDiagnostic = CFastActionsPage()
        self.tabDiagnostic.setObjectName(_fromUtf8("tabDiagnostic"))
        self.tabWidget.addTab(self.tabDiagnostic, _fromUtf8(""))
        self.tabCure = CFastActionsPage()
        self.tabCure.setObjectName(_fromUtf8("tabCure"))
        self.tabWidget.addTab(self.tabCure, _fromUtf8(""))
        self.tabMisc = CFastActionsPage()
        self.tabMisc.setObjectName(_fromUtf8("tabMisc"))
        self.tabWidget.addTab(self.tabMisc, _fromUtf8(""))
        self.tabCash = CFastEventCashPage()
        self.tabCash.setObjectName(_fromUtf8("tabCash"))
        self.tabWidget.addTab(self.tabCash, _fromUtf8(""))
        self.tabReferral = CReferralPage()
        self.tabReferral.setObjectName(_fromUtf8("tabReferral"))
        self.tabWidget.addTab(self.tabReferral, _fromUtf8(""))
        self.tabNotes = CFastEventNotesPage()
        self.tabNotes.setObjectName(_fromUtf8("tabNotes"))
        self.tabWidget.addTab(self.tabNotes, _fromUtf8(""))
        self.verticalLayout.addWidget(self.sptTopLevel)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblProlongateEvent = QtGui.QLabel(Dialog)
        self.lblProlongateEvent.setText(_fromUtf8(""))
        self.lblProlongateEvent.setObjectName(_fromUtf8("lblProlongateEvent"))
        self.horizontalLayout.addWidget(self.lblProlongateEvent)
        self.lblValueExternalId = QtGui.QLabel(Dialog)
        self.lblValueExternalId.setText(_fromUtf8(""))
        self.lblValueExternalId.setObjectName(_fromUtf8("lblValueExternalId"))
        self.horizontalLayout.addWidget(self.lblValueExternalId)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.statusBar = QtGui.QStatusBar(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusBar.sizePolicy().hasHeightForWidth())
        self.statusBar.setSizePolicy(sizePolicy)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        self.verticalLayout.addWidget(self.statusBar)
        self.lblNextDate.setBuddy(self.edtNextDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblResult.setBuddy(self.cmbResult)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblGoal.setBuddy(self.cmbGoal)
        self.lblChildBirthDate.setBuddy(self.edtChildBirthDate)
        self.lblChildSex.setBuddy(self.cmbChildSex)
        self.lblChildNumber.setBuddy(self.sbChildNumber)
        self.lblBirthWeight.setBuddy(self.sbBirthWeight)
        self.lblWorkPost.setBuddy(self.edtWorkPost)
        self.lblWorkOKVED.setBuddy(self.cmbWorkOKVED)
        self.label_7.setBuddy(self.edtPrevDate)
        self.lblWorkStage.setBuddy(self.edtWorkStage)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.tabWidget, self.scrollArea)
        Dialog.setTabOrder(self.scrollArea, self.cmbContract)
        Dialog.setTabOrder(self.cmbContract, self.chkIsClosed)
        Dialog.setTabOrder(self.chkIsClosed, self.chkExposeConfirmed)
        Dialog.setTabOrder(self.chkExposeConfirmed, self.edtBegDate)
        Dialog.setTabOrder(self.edtBegDate, self.edtBegTime)
        Dialog.setTabOrder(self.edtBegTime, self.edtEndDate)
        Dialog.setTabOrder(self.edtEndDate, self.edtEndTime)
        Dialog.setTabOrder(self.edtEndTime, self.edtNextDate)
        Dialog.setTabOrder(self.edtNextDate, self.cmbPerson)
        Dialog.setTabOrder(self.cmbPerson, self.chkPrimary)
        Dialog.setTabOrder(self.chkPrimary, self.cmbResult)
        Dialog.setTabOrder(self.cmbResult, self.cmbGoal)
        Dialog.setTabOrder(self.cmbGoal, self.chkDispByMobileTeam)
        Dialog.setTabOrder(self.chkDispByMobileTeam, self.gbLittleStrangerFlag)
        Dialog.setTabOrder(self.gbLittleStrangerFlag, self.sbChildNumber)
        Dialog.setTabOrder(self.sbChildNumber, self.cmbChildSex)
        Dialog.setTabOrder(self.cmbChildSex, self.edtChildBirthDate)
        Dialog.setTabOrder(self.edtChildBirthDate, self.sbBirthWeight)
        Dialog.setTabOrder(self.sbBirthWeight, self.chkMultipleBirths)
        Dialog.setTabOrder(self.chkMultipleBirths, self.chkZNOMorph)
        Dialog.setTabOrder(self.chkZNOMorph, self.chkZNOFirst)
        Dialog.setTabOrder(self.chkZNOFirst, self.cmbWorkOrganisation)
        Dialog.setTabOrder(self.cmbWorkOrganisation, self.btnSelectWorkOrganisation)
        Dialog.setTabOrder(self.btnSelectWorkOrganisation, self.edtWorkPost)
        Dialog.setTabOrder(self.edtWorkPost, self.cmbWorkOKVED)
        Dialog.setTabOrder(self.cmbWorkOKVED, self.edtWorkStage)
        Dialog.setTabOrder(self.edtWorkStage, self.edtPrevDate)
        Dialog.setTabOrder(self.edtPrevDate, self.tblWorkHurts)
        Dialog.setTabOrder(self.tblWorkHurts, self.tblWorkHurtFactors)
        Dialog.setTabOrder(self.tblWorkHurtFactors, self.tblFinalDiagnostics)
        Dialog.setTabOrder(self.tblFinalDiagnostics, self.tblActions)
        Dialog.setTabOrder(self.tblActions, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.txtClientInfoBrowser.setWhatsThis(_translate("Dialog", "Описание пациента", None))
        self.txtClientInfoBrowser.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p></body></html>", None))
        self.grpBase.setTitle(_translate("Dialog", "&ф.131", None))
        self.lblNextDate.setText(_translate("Dialog", "След.явка", None))
        self.lblEndDate.setText(_translate("Dialog", "Выполнено", None))
        self.cmbContract.setWhatsThis(_translate("Dialog", "номер, дата и основание договора в рамках которого производится осмотр", None))
        self.cmbContract.setItemText(0, _translate("Dialog", "Договор", None))
        self.lblBegDate.setText(_translate("Dialog", "Назначено", None))
        self.lblResult.setText(_translate("Dialog", "Результа&т", None))
        self.cmbResult.setWhatsThis(_translate("Dialog", "результат осмотра", None))
        self.cmbResult.setItemText(0, _translate("Dialog", "Результат", None))
        self.cmbPerson.setWhatsThis(_translate("Dialog", "врач отвечающий за осмотр (терапевт)", None))
        self.cmbPerson.setItemText(0, _translate("Dialog", "Врач", None))
        self.chkPrimary.setText(_translate("Dialog", "Пе&рвичный", None))
        self.lblPerson.setText(_translate("Dialog", "Ответственный", None))
        self.chkZNOMorph.setToolTip(_translate("Dialog", "ЗНО потдверждён морфологически", None))
        self.chkZNOMorph.setText(_translate("Dialog", "ЗНО подтв. морф-ки", None))
        self.chkExposeConfirmed.setText(_translate("Dialog", "Добавить к выставлению", None))
        self.cmbGoal.setWhatsThis(_translate("Dialog", "результат осмотра", None))
        self.lblGoal.setText(_translate("Dialog", "Цель", None))
        self.chkZNOFirst.setToolTip(_translate("Dialog", "ЗНО установлен впервые", None))
        self.chkZNOFirst.setText(_translate("Dialog", "ЗНО уст. впервые", None))
        self.chkDispByMobileTeam.setText(_translate("Dialog", "Диспансеризация(проф.осмотр) проведена МВБ", None))
        self.gbLittleStrangerFlag.setTitle(_translate("Dialog", "Признак новорожденного", None))
        self.lblChildBirthDate.setText(_translate("Dialog", "Дата рождения", None))
        self.lblChildSex.setText(_translate("Dialog", "Пол", None))
        self.cmbChildSex.setItemText(1, _translate("Dialog", "М", None))
        self.cmbChildSex.setItemText(2, _translate("Dialog", "Ж", None))
        self.chkMultipleBirths.setText(_translate("Dialog", "Многоплодные роды", None))
        self.lblChildNumber.setText(_translate("Dialog", "По счету в семье", None))
        self.lblBirthWeight.setText(_translate("Dialog", "Вес при рождении", None))
        self.edtBegDate.setWhatsThis(_translate("Dialog", "дата начала осмотра", None))
        self.edtBegTime.setDisplayFormat(_translate("Dialog", "HH:mm", None))
        self.edtEndDate.setWhatsThis(_translate("Dialog", "дата окончания осмотра", None))
        self.edtEndTime.setDisplayFormat(_translate("Dialog", "HH:mm", None))
        self.chkIsClosed.setText(_translate("Dialog", "Карта заполнена", None))
        self.grpWork.setTitle(_translate("Dialog", "&Занятость", None))
        self.btnSelectWorkOrganisation.setText(_translate("Dialog", "...", None))
        self.lblWorkPost.setText(_translate("Dialog", "Должность", None))
        self.lblWorkOKVED.setText(_translate("Dialog", "ОКВЭД", None))
        self.label_7.setText(_translate("Dialog", "Дата период.осмотра", None))
        self.lblWorkStage.setText(_translate("Dialog", "стаж", None))
        self.lblKPP.setText(_translate("Dialog", "КПП", None))
        self.lblINN.setText(_translate("Dialog", "ИНН", None))
        self.cmbWorkOrganisation.setWhatsThis(_translate("Dialog", "место работы пациента", None))
        self.lblOGRN.setText(_translate("Dialog", "ОГРН", None))
        self.tblWorkHurt.setTitle(_translate("Dialog", "&Вредность", None))
        self.tblWorkHurtFactors.setWhatsThis(_translate("Dialog", "вредные факторы работы пациента", None))
        self.grpInspections.setTitle(_translate("Dialog", "&Осмотр", None))
        self.grpActions.setTitle(_translate("Dialog", "&Мероприятия", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabToken), _translate("Dialog", "Стат.&учёт", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMes), _translate("Dialog", "Стандарт", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabStatus), _translate("Dialog", "&Статус", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDiagnostic), _translate("Dialog", "&Диагностика", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCure), _translate("Dialog", "&Лечение", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMisc), _translate("Dialog", "&Мероприятия", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCash), _translate("Dialog", "Оплата", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabReferral), _translate("Dialog", "Направления", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabNotes), _translate("Dialog", "Приме&чания", None))
        self.statusBar.setToolTip(_translate("Dialog", "A status bar", None))
        self.statusBar.setWhatsThis(_translate("Dialog", "A status bar.", None))

from Events.ActionsPage import CFastActionsPage
from Events.EventCashPage import CFastEventCashPage
from Events.EventMesPage import CFastEventMesPage
from Events.EventNotesPage import CFastEventNotesPage
from Events.ReferralPage import CReferralPage
from Orgs.OKVEDComboBox import COKVEDComboBox
from Orgs.OrgComboBox import CContractComboBox, COrgComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from Registry.WorkHurtTableView import CWorkHurtTableView
from library.DateEdit import CDateEdit
from library.InDocTable import CInDocTableView
from library.TextBrowser import CTextBrowser
from library.crbcombobox import CRBComboBox