# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'JournalBeforeRecordDialog.ui'
#
# Created: Tue Jul  7 18:07:29 2015
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

class Ui_JournalBeforeRecordDialog(object):
    def setupUi(self, JournalBeforeRecordDialog):
        JournalBeforeRecordDialog.setObjectName(_fromUtf8("JournalBeforeRecordDialog"))
        JournalBeforeRecordDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        JournalBeforeRecordDialog.resize(536, 354)
        JournalBeforeRecordDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(JournalBeforeRecordDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkIgnoreRehabilitation = QtGui.QCheckBox(JournalBeforeRecordDialog)
        self.chkIgnoreRehabilitation.setObjectName(_fromUtf8("chkIgnoreRehabilitation"))
        self.gridLayout.addWidget(self.chkIgnoreRehabilitation, 13, 0, 1, 1)
        self.chkDetailCallCentr = QtGui.QCheckBox(JournalBeforeRecordDialog)
        self.chkDetailCallCentr.setEnabled(True)
        self.chkDetailCallCentr.setObjectName(_fromUtf8("chkDetailCallCentr"))
        self.gridLayout.addWidget(self.chkDetailCallCentr, 10, 0, 1, 8)
        self.chkPeriodRecord = QtGui.QCheckBox(JournalBeforeRecordDialog)
        self.chkPeriodRecord.setChecked(True)
        self.chkPeriodRecord.setObjectName(_fromUtf8("chkPeriodRecord"))
        self.gridLayout.addWidget(self.chkPeriodRecord, 0, 0, 1, 3)
        self.lblUserProfile = QtGui.QLabel(JournalBeforeRecordDialog)
        self.lblUserProfile.setObjectName(_fromUtf8("lblUserProfile"))
        self.gridLayout.addWidget(self.lblUserProfile, 4, 0, 1, 3)
        self.cmbPerson = CPersonComboBoxEx(JournalBeforeRecordDialog)
        self.cmbPerson.setEnabled(False)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 7, 3, 1, 5)
        self.buttonBox = QtGui.QDialogButtonBox(JournalBeforeRecordDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 16, 0, 1, 8)
        self.edtBegDateRecord = CDateEdit(JournalBeforeRecordDialog)
        self.edtBegDateRecord.setEnabled(False)
        self.edtBegDateRecord.setCalendarPopup(True)
        self.edtBegDateRecord.setObjectName(_fromUtf8("edtBegDateRecord"))
        self.gridLayout.addWidget(self.edtBegDateRecord, 1, 3, 1, 1)
        self.edtEndDate = CDateEdit(JournalBeforeRecordDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 0, 5, 1, 1)
        spacerItem = QtGui.QSpacerItem(101, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 7, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(101, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 7, 1, 1)
        self.lblSpeciality = QtGui.QLabel(JournalBeforeRecordDialog)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout.addWidget(self.lblSpeciality, 6, 0, 1, 3)
        self.chkOrgStructure = QtGui.QCheckBox(JournalBeforeRecordDialog)
        self.chkOrgStructure.setObjectName(_fromUtf8("chkOrgStructure"))
        self.gridLayout.addWidget(self.chkOrgStructure, 5, 0, 1, 3)
        self.cmbQueueType = QtGui.QComboBox(JournalBeforeRecordDialog)
        self.cmbQueueType.setObjectName(_fromUtf8("cmbQueueType"))
        self.cmbQueueType.addItem(_fromUtf8(""))
        self.cmbQueueType.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbQueueType, 9, 3, 1, 5)
        self.cmbUserId = CPersonComboBoxEx(JournalBeforeRecordDialog)
        self.cmbUserId.setEnabled(True)
        self.cmbUserId.setObjectName(_fromUtf8("cmbUserId"))
        self.gridLayout.addWidget(self.cmbUserId, 3, 3, 1, 5)
        self.cmbOrgStructure = COrgStructureComboBox(JournalBeforeRecordDialog)
        self.cmbOrgStructure.setEnabled(False)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 5, 3, 1, 5)
        self.lblPerson = QtGui.QLabel(JournalBeforeRecordDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 7, 0, 1, 3)
        self.chkShowWithoutOverTime = QtGui.QCheckBox(JournalBeforeRecordDialog)
        self.chkShowWithoutOverTime.setObjectName(_fromUtf8("chkShowWithoutOverTime"))
        self.gridLayout.addWidget(self.chkShowWithoutOverTime, 12, 0, 1, 3)
        self.lblQueueType = QtGui.QLabel(JournalBeforeRecordDialog)
        self.lblQueueType.setObjectName(_fromUtf8("lblQueueType"))
        self.gridLayout.addWidget(self.lblQueueType, 9, 0, 1, 3)
        self.lblUserId = QtGui.QLabel(JournalBeforeRecordDialog)
        self.lblUserId.setObjectName(_fromUtf8("lblUserId"))
        self.gridLayout.addWidget(self.lblUserId, 3, 0, 1, 3)
        self.chkPeriodBeforeRecord = QtGui.QCheckBox(JournalBeforeRecordDialog)
        self.chkPeriodBeforeRecord.setObjectName(_fromUtf8("chkPeriodBeforeRecord"))
        self.gridLayout.addWidget(self.chkPeriodBeforeRecord, 1, 0, 1, 3)
        self.edtBegDate = CDateEdit(JournalBeforeRecordDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 3, 1, 1)
        self.lblEndDate = QtGui.QLabel(JournalBeforeRecordDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 0, 4, 1, 1)
        self.label_2 = QtGui.QLabel(JournalBeforeRecordDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 4, 1, 1)
        self.edtEndDateRecord = CDateEdit(JournalBeforeRecordDialog)
        self.edtEndDateRecord.setEnabled(False)
        self.edtEndDateRecord.setCalendarPopup(True)
        self.edtEndDateRecord.setObjectName(_fromUtf8("edtEndDateRecord"))
        self.gridLayout.addWidget(self.edtEndDateRecord, 1, 5, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(21, 21, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 15, 2, 1, 1)
        self.cmbUserProfile = CRBComboBox(JournalBeforeRecordDialog)
        self.cmbUserProfile.setObjectName(_fromUtf8("cmbUserProfile"))
        self.gridLayout.addWidget(self.cmbUserProfile, 4, 3, 1, 5)
        self.cmbSpeciality = CRBComboBox(JournalBeforeRecordDialog)
        self.cmbSpeciality.setEnabled(False)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 6, 3, 1, 5)
        self.chkShowNotes = QtGui.QCheckBox(JournalBeforeRecordDialog)
        self.chkShowNotes.setObjectName(_fromUtf8("chkShowNotes"))
        self.gridLayout.addWidget(self.chkShowNotes, 14, 0, 1, 1)
        self.chkDetailExternalIS = QtGui.QCheckBox(JournalBeforeRecordDialog)
        self.chkDetailExternalIS.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.chkDetailExternalIS.setObjectName(_fromUtf8("chkDetailExternalIS"))
        self.gridLayout.addWidget(self.chkDetailExternalIS, 11, 0, 1, 1)
        self.lblSpeciality.setBuddy(self.cmbSpeciality)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(JournalBeforeRecordDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), JournalBeforeRecordDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), JournalBeforeRecordDialog.reject)
        QtCore.QObject.connect(self.chkOrgStructure, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cmbOrgStructure.setEnabled)
        QtCore.QObject.connect(self.chkOrgStructure, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cmbSpeciality.setEnabled)
        QtCore.QObject.connect(self.chkOrgStructure, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.cmbPerson.setEnabled)
        QtCore.QObject.connect(self.chkPeriodRecord, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtBegDate.setEnabled)
        QtCore.QObject.connect(self.chkPeriodRecord, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtEndDate.setEnabled)
        QtCore.QObject.connect(self.chkPeriodBeforeRecord, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtEndDateRecord.setEnabled)
        QtCore.QObject.connect(self.chkPeriodBeforeRecord, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtBegDateRecord.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(JournalBeforeRecordDialog)
        JournalBeforeRecordDialog.setTabOrder(self.chkPeriodRecord, self.edtBegDate)
        JournalBeforeRecordDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        JournalBeforeRecordDialog.setTabOrder(self.edtEndDate, self.chkPeriodBeforeRecord)
        JournalBeforeRecordDialog.setTabOrder(self.chkPeriodBeforeRecord, self.edtBegDateRecord)
        JournalBeforeRecordDialog.setTabOrder(self.edtBegDateRecord, self.edtEndDateRecord)
        JournalBeforeRecordDialog.setTabOrder(self.edtEndDateRecord, self.cmbUserId)
        JournalBeforeRecordDialog.setTabOrder(self.cmbUserId, self.cmbUserProfile)
        JournalBeforeRecordDialog.setTabOrder(self.cmbUserProfile, self.chkOrgStructure)
        JournalBeforeRecordDialog.setTabOrder(self.chkOrgStructure, self.cmbOrgStructure)
        JournalBeforeRecordDialog.setTabOrder(self.cmbOrgStructure, self.cmbSpeciality)
        JournalBeforeRecordDialog.setTabOrder(self.cmbSpeciality, self.cmbPerson)
        JournalBeforeRecordDialog.setTabOrder(self.cmbPerson, self.cmbQueueType)
        JournalBeforeRecordDialog.setTabOrder(self.cmbQueueType, self.chkDetailCallCentr)
        JournalBeforeRecordDialog.setTabOrder(self.chkDetailCallCentr, self.chkDetailExternalIS)
        JournalBeforeRecordDialog.setTabOrder(self.chkDetailExternalIS, self.chkShowWithoutOverTime)
        JournalBeforeRecordDialog.setTabOrder(self.chkShowWithoutOverTime, self.chkIgnoreRehabilitation)
        JournalBeforeRecordDialog.setTabOrder(self.chkIgnoreRehabilitation, self.chkShowNotes)
        JournalBeforeRecordDialog.setTabOrder(self.chkShowNotes, self.buttonBox)

    def retranslateUi(self, JournalBeforeRecordDialog):
        JournalBeforeRecordDialog.setWindowTitle(_translate("JournalBeforeRecordDialog", "Журнал предварительной записи", None))
        self.chkIgnoreRehabilitation.setText(_translate("JournalBeforeRecordDialog", "Не учитывать реабилитационное отделение", None))
        self.chkDetailCallCentr.setText(_translate("JournalBeforeRecordDialog", "Детализировать Call-центр", None))
        self.chkPeriodRecord.setText(_translate("JournalBeforeRecordDialog", "Период постановки в очередь с", None))
        self.lblUserProfile.setText(_translate("JournalBeforeRecordDialog", "Профиль пользователя", None))
        self.lblSpeciality.setText(_translate("JournalBeforeRecordDialog", "&Специальность", None))
        self.chkOrgStructure.setText(_translate("JournalBeforeRecordDialog", "&Подразделение", None))
        self.cmbQueueType.setItemText(0, _translate("JournalBeforeRecordDialog", "Амбулаторный прием", None))
        self.cmbQueueType.setItemText(1, _translate("JournalBeforeRecordDialog", "Вызовы", None))
        self.lblPerson.setText(_translate("JournalBeforeRecordDialog", "&Врач", None))
        self.chkShowWithoutOverTime.setText(_translate("JournalBeforeRecordDialog", "Не выводить пациентов сверх очереди", None))
        self.lblQueueType.setText(_translate("JournalBeforeRecordDialog", "Учитывать", None))
        self.lblUserId.setText(_translate("JournalBeforeRecordDialog", "Пользователь", None))
        self.chkPeriodBeforeRecord.setText(_translate("JournalBeforeRecordDialog", "Период предварительной записи с", None))
        self.lblEndDate.setText(_translate("JournalBeforeRecordDialog", "по", None))
        self.label_2.setText(_translate("JournalBeforeRecordDialog", "по", None))
        self.cmbSpeciality.setWhatsThis(_translate("JournalBeforeRecordDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.chkShowNotes.setText(_translate("JournalBeforeRecordDialog", "Выводить жалобы", None))
        self.chkDetailExternalIS.setToolTip(_translate("JournalBeforeRecordDialog", "<html><head/><body><p>В отчёт будут выведены только записи, выполненные через внешние ИС</p></body></html>", None))
        self.chkDetailExternalIS.setText(_translate("JournalBeforeRecordDialog", "Детализировать запись через внешние ИС", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.crbcombobox import CRBComboBox