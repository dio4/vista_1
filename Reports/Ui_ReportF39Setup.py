# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportF39Setup.ui'
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

class Ui_ReportF39SetupDialog(object):
    def setupUi(self, ReportF39SetupDialog):
        ReportF39SetupDialog.setObjectName(_fromUtf8("ReportF39SetupDialog"))
        ReportF39SetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportF39SetupDialog.resize(671, 662)
        ReportF39SetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportF39SetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkVisitDisp = QtGui.QCheckBox(ReportF39SetupDialog)
        self.chkVisitDisp.setObjectName(_fromUtf8("chkVisitDisp"))
        self.gridLayout.addWidget(self.chkVisitDisp, 5, 0, 1, 1)
        self.chkCombine = QtGui.QCheckBox(ReportF39SetupDialog)
        self.chkCombine.setObjectName(_fromUtf8("chkCombine"))
        self.gridLayout.addWidget(self.chkCombine, 15, 1, 1, 1)
        self.lblEventPurpose = QtGui.QLabel(ReportF39SetupDialog)
        self.lblEventPurpose.setEnabled(True)
        self.lblEventPurpose.setObjectName(_fromUtf8("lblEventPurpose"))
        self.gridLayout.addWidget(self.lblEventPurpose, 6, 0, 1, 1)
        self.cmbVisitPayStatus = QtGui.QComboBox(ReportF39SetupDialog)
        self.cmbVisitPayStatus.setObjectName(_fromUtf8("cmbVisitPayStatus"))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbVisitPayStatus, 16, 1, 1, 4)
        self.cmbPerson = CPersonComboBoxEx(ReportF39SetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbPerson, 10, 1, 1, 4)
        self.lblSex = QtGui.QLabel(ReportF39SetupDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout.addWidget(self.lblSex, 11, 0, 1, 1)
        self.chkADN = QtGui.QCheckBox(ReportF39SetupDialog)
        self.chkADN.setEnabled(False)
        self.chkADN.setObjectName(_fromUtf8("chkADN"))
        self.gridLayout.addWidget(self.chkADN, 3, 2, 1, 2)
        self.cmbRowGrouping = QtGui.QComboBox(ReportF39SetupDialog)
        self.cmbRowGrouping.setObjectName(_fromUtf8("cmbRowGrouping"))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbRowGrouping, 13, 1, 1, 4)
        self.edtEndDate = CDateEdit(ReportF39SetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 2)
        self.chkVisitHospital = QtGui.QCheckBox(ReportF39SetupDialog)
        self.chkVisitHospital.setObjectName(_fromUtf8("chkVisitHospital"))
        self.gridLayout.addWidget(self.chkVisitHospital, 4, 0, 1, 1)
        self.chkDetailChildren = QtGui.QCheckBox(ReportF39SetupDialog)
        self.chkDetailChildren.setEnabled(True)
        self.chkDetailChildren.setObjectName(_fromUtf8("chkDetailChildren"))
        self.gridLayout.addWidget(self.chkDetailChildren, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportF39SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 17, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 2)
        self.lblPerson = QtGui.QLabel(ReportF39SetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 10, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportF39SetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 3, 1, 2)
        self.gbEventDatetimeParams = QtGui.QGroupBox(ReportF39SetupDialog)
        self.gbEventDatetimeParams.setMinimumSize(QtCore.QSize(0, 41))
        self.gbEventDatetimeParams.setCheckable(True)
        self.gbEventDatetimeParams.setChecked(False)
        self.gbEventDatetimeParams.setObjectName(_fromUtf8("gbEventDatetimeParams"))
        self.edtEventBegDatetime = QtGui.QDateTimeEdit(self.gbEventDatetimeParams)
        self.edtEventBegDatetime.setGeometry(QtCore.QRect(200, 20, 201, 21))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEventBegDatetime.sizePolicy().hasHeightForWidth())
        self.edtEventBegDatetime.setSizePolicy(sizePolicy)
        self.edtEventBegDatetime.setCalendarPopup(True)
        self.edtEventBegDatetime.setObjectName(_fromUtf8("edtEventBegDatetime"))
        self.edtEventEndDatetime = QtGui.QDateTimeEdit(self.gbEventDatetimeParams)
        self.edtEventEndDatetime.setGeometry(QtCore.QRect(420, 20, 194, 22))
        self.edtEventEndDatetime.setCalendarPopup(True)
        self.edtEventEndDatetime.setObjectName(_fromUtf8("edtEventEndDatetime"))
        self.lblEventDatetime = QtGui.QLabel(self.gbEventDatetimeParams)
        self.lblEventDatetime.setGeometry(QtCore.QRect(10, 20, 181, 21))
        self.lblEventDatetime.setObjectName(_fromUtf8("lblEventDatetime"))
        self.gridLayout.addWidget(self.gbEventDatetimeParams, 2, 0, 1, 5)
        self.cmbEventPurpose = CRBComboBox(ReportF39SetupDialog)
        self.cmbEventPurpose.setEnabled(True)
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.gridLayout.addWidget(self.cmbEventPurpose, 6, 1, 1, 4)
        spacerItem2 = QtGui.QSpacerItem(21, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 12, 2, 1, 1)
        self.frmAge = QtGui.QFrame(ReportF39SetupDialog)
        self.frmAge.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAge.setFrameShadow(QtGui.QFrame.Raised)
        self.frmAge.setObjectName(_fromUtf8("frmAge"))
        self._2 = QtGui.QHBoxLayout(self.frmAge)
        self._2.setMargin(0)
        self._2.setSpacing(4)
        self._2.setObjectName(_fromUtf8("_2"))
        self.lblAgFrom = QtGui.QLabel(self.frmAge)
        self.lblAgFrom.setObjectName(_fromUtf8("lblAgFrom"))
        self._2.addWidget(self.lblAgFrom)
        self.edtAgeFrom = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeFrom.sizePolicy().hasHeightForWidth())
        self.edtAgeFrom.setSizePolicy(sizePolicy)
        self.edtAgeFrom.setMaximum(150)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self._2.addWidget(self.edtAgeFrom)
        self.lblAgeTo = QtGui.QLabel(self.frmAge)
        self.lblAgeTo.setObjectName(_fromUtf8("lblAgeTo"))
        self._2.addWidget(self.lblAgeTo)
        self.edtAgeTo = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeTo.sizePolicy().hasHeightForWidth())
        self.edtAgeTo.setSizePolicy(sizePolicy)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self._2.addWidget(self.edtAgeTo)
        self.lblAgeYears = QtGui.QLabel(self.frmAge)
        self.lblAgeYears.setObjectName(_fromUtf8("lblAgeYears"))
        self._2.addWidget(self.lblAgeYears)
        self.gridLayout.addWidget(self.frmAge, 12, 1, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportF39SetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.lblAge = QtGui.QLabel(ReportF39SetupDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout.addWidget(self.lblAge, 12, 0, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportF39SetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 9, 0, 1, 1)
        self.lblRowGrouping = QtGui.QLabel(ReportF39SetupDialog)
        self.lblRowGrouping.setObjectName(_fromUtf8("lblRowGrouping"))
        self.gridLayout.addWidget(self.lblRowGrouping, 13, 0, 1, 1)
        self.lblVisitPayStatus = QtGui.QLabel(ReportF39SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblVisitPayStatus.sizePolicy().hasHeightForWidth())
        self.lblVisitPayStatus.setSizePolicy(sizePolicy)
        self.lblVisitPayStatus.setObjectName(_fromUtf8("lblVisitPayStatus"))
        self.gridLayout.addWidget(self.lblVisitPayStatus, 16, 0, 1, 1)
        self.chkAmbVisits = QtGui.QCheckBox(ReportF39SetupDialog)
        self.chkAmbVisits.setObjectName(_fromUtf8("chkAmbVisits"))
        self.gridLayout.addWidget(self.chkAmbVisits, 14, 1, 1, 3)
        self.edtBegDate = CDateEdit(ReportF39SetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.chkCountCall = QtGui.QCheckBox(ReportF39SetupDialog)
        self.chkCountCall.setEnabled(False)
        self.chkCountCall.setObjectName(_fromUtf8("chkCountCall"))
        self.gridLayout.addWidget(self.chkCountCall, 3, 1, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportF39SetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 9, 1, 1, 4)
        self.cmbSex = QtGui.QComboBox(ReportF39SetupDialog)
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
        self.gridLayout.addWidget(self.cmbSex, 11, 1, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportF39SetupDialog)
        self.lblEventType.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 7, 0, 1, 1)
        self.lstEventTypes = CRBListBox(ReportF39SetupDialog)
        self.lstEventTypes.setObjectName(_fromUtf8("lstEventTypes"))
        self.gridLayout.addWidget(self.lstEventTypes, 7, 1, 1, 3)
        self.lblEventPurpose.setBuddy(self.cmbEventPurpose)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblAgFrom.setBuddy(self.edtAgeFrom)
        self.lblAgeTo.setBuddy(self.edtAgeTo)
        self.lblAgeYears.setBuddy(self.edtAgeTo)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblAge.setBuddy(self.edtAgeFrom)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblRowGrouping.setBuddy(self.cmbRowGrouping)
        self.lblVisitPayStatus.setBuddy(self.cmbVisitPayStatus)
        self.lblEventType.setBuddy(self.lstEventTypes)

        self.retranslateUi(ReportF39SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF39SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF39SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF39SetupDialog)
        ReportF39SetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportF39SetupDialog.setTabOrder(self.edtEndDate, self.cmbEventPurpose)
        ReportF39SetupDialog.setTabOrder(self.cmbEventPurpose, self.cmbOrgStructure)
        ReportF39SetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbSex)
        ReportF39SetupDialog.setTabOrder(self.cmbSex, self.edtAgeFrom)
        ReportF39SetupDialog.setTabOrder(self.edtAgeFrom, self.edtAgeTo)
        ReportF39SetupDialog.setTabOrder(self.edtAgeTo, self.cmbRowGrouping)
        ReportF39SetupDialog.setTabOrder(self.cmbRowGrouping, self.cmbVisitPayStatus)
        ReportF39SetupDialog.setTabOrder(self.cmbVisitPayStatus, self.buttonBox)

    def retranslateUi(self, ReportF39SetupDialog):
        ReportF39SetupDialog.setWindowTitle(_translate("ReportF39SetupDialog", "параметры отчёта", None))
        self.chkVisitDisp.setText(_translate("ReportF39SetupDialog", "Учитывать посещения ДД", None))
        self.chkCombine.setText(_translate("ReportF39SetupDialog", "Учитывать совмещения", None))
        self.lblEventPurpose.setText(_translate("ReportF39SetupDialog", "&Назначение обращения", None))
        self.cmbVisitPayStatus.setItemText(0, _translate("ReportF39SetupDialog", "не задано", None))
        self.cmbVisitPayStatus.setItemText(1, _translate("ReportF39SetupDialog", "не выставлено", None))
        self.cmbVisitPayStatus.setItemText(2, _translate("ReportF39SetupDialog", "выставлено", None))
        self.cmbVisitPayStatus.setItemText(3, _translate("ReportF39SetupDialog", "отказано", None))
        self.cmbVisitPayStatus.setItemText(4, _translate("ReportF39SetupDialog", "оплачено", None))
        self.cmbPerson.setItemText(0, _translate("ReportF39SetupDialog", "Врач", None))
        self.lblSex.setText(_translate("ReportF39SetupDialog", "По&л", None))
        self.chkADN.setText(_translate("ReportF39SetupDialog", "из нихАДН", None))
        self.cmbRowGrouping.setItemText(0, _translate("ReportF39SetupDialog", "Датам", None))
        self.cmbRowGrouping.setItemText(1, _translate("ReportF39SetupDialog", "Врачам", None))
        self.cmbRowGrouping.setItemText(2, _translate("ReportF39SetupDialog", "Подразделениям", None))
        self.cmbRowGrouping.setItemText(3, _translate("ReportF39SetupDialog", "Специальности", None))
        self.cmbRowGrouping.setItemText(4, _translate("ReportF39SetupDialog", "Должности", None))
        self.chkVisitHospital.setText(_translate("ReportF39SetupDialog", "Учитывать посещения ДС", None))
        self.chkDetailChildren.setText(_translate("ReportF39SetupDialog", "Детализация по подросткам", None))
        self.lblPerson.setText(_translate("ReportF39SetupDialog", "&Врач", None))
        self.lblEndDate.setText(_translate("ReportF39SetupDialog", "Дата &окончания периода", None))
        self.gbEventDatetimeParams.setTitle(_translate("ReportF39SetupDialog", "Дата и время создания обращения", None))
        self.lblEventDatetime.setText(_translate("ReportF39SetupDialog", "Интервал дат и времени (с, по):", None))
        self.lblAgFrom.setText(_translate("ReportF39SetupDialog", "с", None))
        self.lblAgeTo.setText(_translate("ReportF39SetupDialog", "по", None))
        self.lblAgeYears.setText(_translate("ReportF39SetupDialog", "лет", None))
        self.lblBegDate.setText(_translate("ReportF39SetupDialog", "Дата &начала периода", None))
        self.lblAge.setText(_translate("ReportF39SetupDialog", "Во&зраст", None))
        self.lblOrgStructure.setText(_translate("ReportF39SetupDialog", "&Подразделение", None))
        self.lblRowGrouping.setText(_translate("ReportF39SetupDialog", "&Строки по", None))
        self.lblVisitPayStatus.setText(_translate("ReportF39SetupDialog", "Флаг &финансирования", None))
        self.chkAmbVisits.setText(_translate("ReportF39SetupDialog", "учитывать амбулаторные посещения сотрудника того же подразделения", None))
        self.chkCountCall.setText(_translate("ReportF39SetupDialog", "Подсчёт количества вызовов", None))
        self.cmbSex.setItemText(1, _translate("ReportF39SetupDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("ReportF39SetupDialog", "Ж", None))
        self.lblEventType.setText(_translate("ReportF39SetupDialog", "&Тип обращения", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
from library.crbcombobox import CRBComboBox
