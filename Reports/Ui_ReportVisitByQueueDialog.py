# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\ReportVisitByQueueDialog.ui'
#
# Created: Fri Jun 15 12:17:49 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportVisitByQueueDialog(object):
    def setupUi(self, ReportVisitByQueueDialog):
        ReportVisitByQueueDialog.setObjectName(_fromUtf8("ReportVisitByQueueDialog"))
        ReportVisitByQueueDialog.resize(418, 279)
        self.gridLayout = QtGui.QGridLayout(ReportVisitByQueueDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(ReportVisitByQueueDialog)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.edtBeginDateVisitBeforeRecordClient = CDateEdit(ReportVisitByQueueDialog)
        self.edtBeginDateVisitBeforeRecordClient.setCalendarPopup(True)
        self.edtBeginDateVisitBeforeRecordClient.setObjectName(_fromUtf8("edtBeginDateVisitBeforeRecordClient"))
        self.horizontalLayout.addWidget(self.edtBeginDateVisitBeforeRecordClient)
        self.label_2 = QtGui.QLabel(ReportVisitByQueueDialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.edtEndDateVisitBeforeRecordClient = CDateEdit(ReportVisitByQueueDialog)
        self.edtEndDateVisitBeforeRecordClient.setCalendarPopup(True)
        self.edtEndDateVisitBeforeRecordClient.setObjectName(_fromUtf8("edtEndDateVisitBeforeRecordClient"))
        self.horizontalLayout.addWidget(self.edtEndDateVisitBeforeRecordClient)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 3)
        self.label_3 = QtGui.QLabel(ReportVisitByQueueDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.cmbOrgStructureVisitBeforeRecordClient = COrgStructureComboBox(ReportVisitByQueueDialog)
        self.cmbOrgStructureVisitBeforeRecordClient.setObjectName(_fromUtf8("cmbOrgStructureVisitBeforeRecordClient"))
        self.gridLayout.addWidget(self.cmbOrgStructureVisitBeforeRecordClient, 1, 1, 1, 2)
        self.label_4 = QtGui.QLabel(ReportVisitByQueueDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.cmbSpecialityVisitBeforeRecordClient = CRBComboBox(ReportVisitByQueueDialog)
        self.cmbSpecialityVisitBeforeRecordClient.setObjectName(_fromUtf8("cmbSpecialityVisitBeforeRecordClient"))
        self.gridLayout.addWidget(self.cmbSpecialityVisitBeforeRecordClient, 2, 1, 1, 2)
        self.label_5 = QtGui.QLabel(ReportVisitByQueueDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.cmbPersonVisitBeforeRecordClient = CPersonComboBoxEx(ReportVisitByQueueDialog)
        self.cmbPersonVisitBeforeRecordClient.setObjectName(_fromUtf8("cmbPersonVisitBeforeRecordClient"))
        self.gridLayout.addWidget(self.cmbPersonVisitBeforeRecordClient, 3, 1, 1, 2)
        self.chkNextVisitBeforeRecordClient = QtGui.QCheckBox(ReportVisitByQueueDialog)
        self.chkNextVisitBeforeRecordClient.setObjectName(_fromUtf8("chkNextVisitBeforeRecordClient"))
        self.gridLayout.addWidget(self.chkNextVisitBeforeRecordClient, 4, 0, 1, 3)
        self.chkNoVisitBeforeRecordClient = QtGui.QCheckBox(ReportVisitByQueueDialog)
        self.chkNoVisitBeforeRecordClient.setObjectName(_fromUtf8("chkNoVisitBeforeRecordClient"))
        self.gridLayout.addWidget(self.chkNoVisitBeforeRecordClient, 5, 0, 1, 3)
        self.chkVisitOtherSpeciality = QtGui.QCheckBox(ReportVisitByQueueDialog)
        self.chkVisitOtherSpeciality.setObjectName(_fromUtf8("chkVisitOtherSpeciality"))
        self.gridLayout.addWidget(self.chkVisitOtherSpeciality, 6, 0, 1, 3)
        self.lblSorting = QtGui.QLabel(ReportVisitByQueueDialog)
        self.lblSorting.setObjectName(_fromUtf8("lblSorting"))
        self.gridLayout.addWidget(self.lblSorting, 7, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 8, 0, 1, 1)
        self.cmbSorting = QtGui.QComboBox(ReportVisitByQueueDialog)
        self.cmbSorting.setObjectName(_fromUtf8("cmbSorting"))
        self.cmbSorting.addItem(_fromUtf8(""))
        self.cmbSorting.addItem(_fromUtf8(""))
        self.cmbSorting.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbSorting, 7, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportVisitByQueueDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 3)

        self.retranslateUi(ReportVisitByQueueDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportVisitByQueueDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportVisitByQueueDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportVisitByQueueDialog)
        ReportVisitByQueueDialog.setTabOrder(self.edtBeginDateVisitBeforeRecordClient, self.edtEndDateVisitBeforeRecordClient)
        ReportVisitByQueueDialog.setTabOrder(self.edtEndDateVisitBeforeRecordClient, self.cmbOrgStructureVisitBeforeRecordClient)
        ReportVisitByQueueDialog.setTabOrder(self.cmbOrgStructureVisitBeforeRecordClient, self.cmbSpecialityVisitBeforeRecordClient)
        ReportVisitByQueueDialog.setTabOrder(self.cmbSpecialityVisitBeforeRecordClient, self.cmbPersonVisitBeforeRecordClient)
        ReportVisitByQueueDialog.setTabOrder(self.cmbPersonVisitBeforeRecordClient, self.chkNextVisitBeforeRecordClient)

    def retranslateUi(self, ReportVisitByQueueDialog):
        ReportVisitByQueueDialog.setWindowTitle(QtGui.QApplication.translate("ReportVisitByQueueDialog", "Протокол обращений пациента по предварительной записи", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ReportVisitByQueueDialog", "с", None, QtGui.QApplication.UnicodeUTF8))
        self.edtBeginDateVisitBeforeRecordClient.setDisplayFormat(QtGui.QApplication.translate("ReportVisitByQueueDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ReportVisitByQueueDialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.edtEndDateVisitBeforeRecordClient.setDisplayFormat(QtGui.QApplication.translate("ReportVisitByQueueDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ReportVisitByQueueDialog", "Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ReportVisitByQueueDialog", "Специальность", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ReportVisitByQueueDialog", "Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.chkNextVisitBeforeRecordClient.setText(QtGui.QApplication.translate("ReportVisitByQueueDialog", "Учитывать назначение следующей явки", None, QtGui.QApplication.UnicodeUTF8))
        self.chkNoVisitBeforeRecordClient.setText(QtGui.QApplication.translate("ReportVisitByQueueDialog", "Учитывать только не явившихся на прием", None, QtGui.QApplication.UnicodeUTF8))
        self.chkVisitOtherSpeciality.setText(QtGui.QApplication.translate("ReportVisitByQueueDialog", "Не учитывать явившихся к другому врачу данной специальности", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSorting.setText(QtGui.QApplication.translate("ReportVisitByQueueDialog", "Сортировка", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSorting.setItemText(0, QtGui.QApplication.translate("ReportVisitByQueueDialog", "по дате", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSorting.setItemText(1, QtGui.QApplication.translate("ReportVisitByQueueDialog", "по ФИО пациента", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSorting.setItemText(2, QtGui.QApplication.translate("ReportVisitByQueueDialog", "по идентификатору пациента", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportVisitByQueueDialog = QtGui.QDialog()
    ui = Ui_ReportVisitByQueueDialog()
    ui.setupUi(ReportVisitByQueueDialog)
    ReportVisitByQueueDialog.show()
    sys.exit(app.exec_())

