# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\ReportF39ModSetup.ui'
#
# Created: Fri Jun 15 12:15:54 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportF39ModSetupDialog(object):
    def setupUi(self, ReportF39ModSetupDialog):
        ReportF39ModSetupDialog.setObjectName(_fromUtf8("ReportF39ModSetupDialog"))
        ReportF39ModSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportF39ModSetupDialog.resize(342, 344)
        ReportF39ModSetupDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ReportF39ModSetupDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblBegDate = QtGui.QLabel(ReportF39ModSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridlayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(ReportF39ModSetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridlayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportF39ModSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridlayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportF39ModSetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridlayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(ReportF39ModSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridlayout.addWidget(self.lblOrgStructure, 8, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(ReportF39ModSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridlayout.addWidget(self.cmbOrgStructure, 8, 1, 1, 2)
        self.lblPerson = QtGui.QLabel(ReportF39ModSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridlayout.addWidget(self.lblPerson, 9, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(ReportF39ModSetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbPerson, 9, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportF39ModSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 16, 0, 1, 3)
        self.lblRowGrouping = QtGui.QLabel(ReportF39ModSetupDialog)
        self.lblRowGrouping.setObjectName(_fromUtf8("lblRowGrouping"))
        self.gridlayout.addWidget(self.lblRowGrouping, 12, 0, 1, 1)
        self.cmbRowGrouping = QtGui.QComboBox(ReportF39ModSetupDialog)
        self.cmbRowGrouping.setObjectName(_fromUtf8("cmbRowGrouping"))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbRowGrouping, 12, 1, 1, 2)
        self.cmbEventType = CRBComboBox(ReportF39ModSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridlayout.addWidget(self.cmbEventType, 7, 1, 1, 2)
        self.cmbEventPurpose = CRBComboBox(ReportF39ModSetupDialog)
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.gridlayout.addWidget(self.cmbEventPurpose, 4, 1, 1, 2)
        self.lblEventPurpose = QtGui.QLabel(ReportF39ModSetupDialog)
        self.lblEventPurpose.setObjectName(_fromUtf8("lblEventPurpose"))
        self.gridlayout.addWidget(self.lblEventPurpose, 4, 0, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportF39ModSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridlayout.addWidget(self.lblEventType, 7, 0, 1, 1)
        self.lblVisitPayStatus = QtGui.QLabel(ReportF39ModSetupDialog)
        self.lblVisitPayStatus.setObjectName(_fromUtf8("lblVisitPayStatus"))
        self.gridlayout.addWidget(self.lblVisitPayStatus, 14, 0, 1, 1)
        self.cmbVisitPayStatus = QtGui.QComboBox(ReportF39ModSetupDialog)
        self.cmbVisitPayStatus.setObjectName(_fromUtf8("cmbVisitPayStatus"))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbVisitPayStatus, 14, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem2, 15, 0, 1, 1)
        self.chkDetailChildren = QtGui.QCheckBox(ReportF39ModSetupDialog)
        self.chkDetailChildren.setObjectName(_fromUtf8("chkDetailChildren"))
        self.gridlayout.addWidget(self.chkDetailChildren, 2, 1, 1, 2)
        self.chkVisitHospital = QtGui.QCheckBox(ReportF39ModSetupDialog)
        self.chkVisitHospital.setObjectName(_fromUtf8("chkVisitHospital"))
        self.gridlayout.addWidget(self.chkVisitHospital, 3, 1, 1, 2)
        self.lblSex = QtGui.QLabel(ReportF39ModSetupDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridlayout.addWidget(self.lblSex, 10, 0, 1, 1)
        self.cmbSex = QtGui.QComboBox(ReportF39ModSetupDialog)
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
        self.gridlayout.addWidget(self.cmbSex, 10, 1, 1, 1)
        self.lblAge = QtGui.QLabel(ReportF39ModSetupDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridlayout.addWidget(self.lblAge, 11, 0, 1, 1)
        self.frmAge = QtGui.QFrame(ReportF39ModSetupDialog)
        self.frmAge.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAge.setFrameShadow(QtGui.QFrame.Raised)
        self.frmAge.setObjectName(_fromUtf8("frmAge"))
        self._2 = QtGui.QHBoxLayout(self.frmAge)
        self._2.setSpacing(4)
        self._2.setMargin(0)
        self._2.setObjectName(_fromUtf8("_2"))
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
        spacerItem3 = QtGui.QSpacerItem(21, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self._2.addItem(spacerItem3)
        self.gridlayout.addWidget(self.frmAge, 11, 1, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblRowGrouping.setBuddy(self.cmbRowGrouping)
        self.lblEventPurpose.setBuddy(self.cmbEventPurpose)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblAge.setBuddy(self.edtAgeFrom)
        self.lblAgeTo.setBuddy(self.edtAgeTo)
        self.lblAgeYears.setBuddy(self.edtAgeTo)

        self.retranslateUi(ReportF39ModSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF39ModSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF39ModSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF39ModSetupDialog)
        ReportF39ModSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportF39ModSetupDialog.setTabOrder(self.edtEndDate, self.chkDetailChildren)
        ReportF39ModSetupDialog.setTabOrder(self.chkDetailChildren, self.chkVisitHospital)
        ReportF39ModSetupDialog.setTabOrder(self.chkVisitHospital, self.cmbEventPurpose)
        ReportF39ModSetupDialog.setTabOrder(self.cmbEventPurpose, self.cmbEventType)
        ReportF39ModSetupDialog.setTabOrder(self.cmbEventType, self.cmbOrgStructure)
        ReportF39ModSetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbPerson)
        ReportF39ModSetupDialog.setTabOrder(self.cmbPerson, self.cmbSex)
        ReportF39ModSetupDialog.setTabOrder(self.cmbSex, self.edtAgeFrom)
        ReportF39ModSetupDialog.setTabOrder(self.edtAgeFrom, self.edtAgeTo)
        ReportF39ModSetupDialog.setTabOrder(self.edtAgeTo, self.cmbRowGrouping)
        ReportF39ModSetupDialog.setTabOrder(self.cmbRowGrouping, self.cmbVisitPayStatus)
        ReportF39ModSetupDialog.setTabOrder(self.cmbVisitPayStatus, self.buttonBox)

    def retranslateUi(self, ReportF39ModSetupDialog):
        ReportF39ModSetupDialog.setWindowTitle(QtGui.QApplication.translate("ReportF39ModSetupDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "Дата &начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "Дата &окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "&Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPerson.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "&Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPerson.setItemText(0, QtGui.QApplication.translate("ReportF39ModSetupDialog", "Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRowGrouping.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "&Строки по", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRowGrouping.setItemText(0, QtGui.QApplication.translate("ReportF39ModSetupDialog", "Датам", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRowGrouping.setItemText(1, QtGui.QApplication.translate("ReportF39ModSetupDialog", "Врачам", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRowGrouping.setItemText(2, QtGui.QApplication.translate("ReportF39ModSetupDialog", "Подразделениям", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRowGrouping.setItemText(3, QtGui.QApplication.translate("ReportF39ModSetupDialog", "Специальности", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRowGrouping.setItemText(4, QtGui.QApplication.translate("ReportF39ModSetupDialog", "Должности", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventPurpose.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "&Назначение обращения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventType.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "&Тип обращения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblVisitPayStatus.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "Флаг финансирования", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbVisitPayStatus.setItemText(0, QtGui.QApplication.translate("ReportF39ModSetupDialog", "не задано", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbVisitPayStatus.setItemText(1, QtGui.QApplication.translate("ReportF39ModSetupDialog", "не выставлено", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbVisitPayStatus.setItemText(2, QtGui.QApplication.translate("ReportF39ModSetupDialog", "выставлено", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbVisitPayStatus.setItemText(3, QtGui.QApplication.translate("ReportF39ModSetupDialog", "отказано", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbVisitPayStatus.setItemText(4, QtGui.QApplication.translate("ReportF39ModSetupDialog", "оплачено", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDetailChildren.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "Детализация по подросткам", None, QtGui.QApplication.UnicodeUTF8))
        self.chkVisitHospital.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "Учитывать посещения ДС", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSex.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "По&л", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(1, QtGui.QApplication.translate("ReportF39ModSetupDialog", "М", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(2, QtGui.QApplication.translate("ReportF39ModSetupDialog", "Ж", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAge.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "Во&зраст с", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeTo.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeYears.setText(QtGui.QApplication.translate("ReportF39ModSetupDialog", "лет", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportF39ModSetupDialog = QtGui.QDialog()
    ui = Ui_ReportF39ModSetupDialog()
    ui.setupUi(ReportF39ModSetupDialog)
    ReportF39ModSetupDialog.show()
    sys.exit(app.exec_())

