# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/craz/s11_local/Reports/ReportRecordPersonVisitsSetup.ui'
#
# Created: Sun Dec 23 03:36:20 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportRecordPersonVisitsSetupDialog(object):
    def setupUi(self, ReportRecordPersonVisitsSetupDialog):
        ReportRecordPersonVisitsSetupDialog.setObjectName(_fromUtf8("ReportRecordPersonVisitsSetupDialog"))
        ReportRecordPersonVisitsSetupDialog.resize(434, 607)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ReportRecordPersonVisitsSetupDialog.sizePolicy().hasHeightForWidth())
        ReportRecordPersonVisitsSetupDialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(ReportRecordPersonVisitsSetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.lblBegDate = QtGui.QLabel(ReportRecordPersonVisitsSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.lblBegDate)
        self.edtBegDate = CDateEdit(ReportRecordPersonVisitsSetupDialog)
        self.edtBegDate.setMinimumSize(QtCore.QSize(252, 0))
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.edtBegDate)
        self.lblEndDate = QtGui.QLabel(ReportRecordPersonVisitsSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lblEndDate)
        self.edtEndDate = CDateEdit(ReportRecordPersonVisitsSetupDialog)
        self.edtEndDate.setMinimumSize(QtCore.QSize(252, 0))
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.edtEndDate)
        self.chkDetailChildren = QtGui.QCheckBox(ReportRecordPersonVisitsSetupDialog)
        self.chkDetailChildren.setObjectName(_fromUtf8("chkDetailChildren"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.chkDetailChildren)
        self.chkVisitHospital = QtGui.QCheckBox(ReportRecordPersonVisitsSetupDialog)
        self.chkVisitHospital.setObjectName(_fromUtf8("chkVisitHospital"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.chkVisitHospital)
        self.lblEventPurpose = QtGui.QLabel(ReportRecordPersonVisitsSetupDialog)
        self.lblEventPurpose.setObjectName(_fromUtf8("lblEventPurpose"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.lblEventPurpose)
        self.cmbEventPurpose = CRBComboBox(ReportRecordPersonVisitsSetupDialog)
        self.cmbEventPurpose.setMinimumSize(QtCore.QSize(252, 0))
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.cmbEventPurpose)
        self.lblEventType = QtGui.QLabel(ReportRecordPersonVisitsSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.lblEventType)
        self.cmbEventType = CRBComboBox(ReportRecordPersonVisitsSetupDialog)
        self.cmbEventType.setMinimumSize(QtCore.QSize(252, 0))
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.cmbEventType)
        self.lblOrgStructure = QtGui.QLabel(ReportRecordPersonVisitsSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.lblOrgStructure)
        self.cmbOrgStructure = COrgStructureComboBox(ReportRecordPersonVisitsSetupDialog)
        self.cmbOrgStructure.setMinimumSize(QtCore.QSize(252, 25))
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.cmbOrgStructure)
        self.lblPerson = QtGui.QLabel(ReportRecordPersonVisitsSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.LabelRole, self.lblPerson)
        self.cmbPerson = CPersonComboBoxEx(ReportRecordPersonVisitsSetupDialog)
        self.cmbPerson.setMinimumSize(QtCore.QSize(252, 0))
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.formLayout.setWidget(7, QtGui.QFormLayout.FieldRole, self.cmbPerson)
        self.lblSex = QtGui.QLabel(ReportRecordPersonVisitsSetupDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.LabelRole, self.lblSex)
        self.cmbSex = QtGui.QComboBox(ReportRecordPersonVisitsSetupDialog)
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
        self.formLayout.setWidget(8, QtGui.QFormLayout.FieldRole, self.cmbSex)
        self.lblAge = QtGui.QLabel(ReportRecordPersonVisitsSetupDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.formLayout.setWidget(9, QtGui.QFormLayout.LabelRole, self.lblAge)
        self.frmAge = QtGui.QFrame(ReportRecordPersonVisitsSetupDialog)
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
        spacerItem = QtGui.QSpacerItem(21, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self._2.addItem(spacerItem)
        self.formLayout.setWidget(9, QtGui.QFormLayout.FieldRole, self.frmAge)
        self.lblRowGrouping = QtGui.QLabel(ReportRecordPersonVisitsSetupDialog)
        self.lblRowGrouping.setObjectName(_fromUtf8("lblRowGrouping"))
        self.formLayout.setWidget(10, QtGui.QFormLayout.LabelRole, self.lblRowGrouping)
        self.cmbRowGrouping = QtGui.QComboBox(ReportRecordPersonVisitsSetupDialog)
        self.cmbRowGrouping.setMinimumSize(QtCore.QSize(252, 0))
        self.cmbRowGrouping.setObjectName(_fromUtf8("cmbRowGrouping"))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.cmbRowGrouping.addItem(_fromUtf8(""))
        self.formLayout.setWidget(10, QtGui.QFormLayout.FieldRole, self.cmbRowGrouping)
        self.lblVisitPayStatus = QtGui.QLabel(ReportRecordPersonVisitsSetupDialog)
        self.lblVisitPayStatus.setObjectName(_fromUtf8("lblVisitPayStatus"))
        self.formLayout.setWidget(11, QtGui.QFormLayout.LabelRole, self.lblVisitPayStatus)
        self.cmbVisitPayStatus = QtGui.QComboBox(ReportRecordPersonVisitsSetupDialog)
        self.cmbVisitPayStatus.setMinimumSize(QtCore.QSize(252, 0))
        self.cmbVisitPayStatus.setObjectName(_fromUtf8("cmbVisitPayStatus"))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.cmbVisitPayStatus.addItem(_fromUtf8(""))
        self.formLayout.setWidget(11, QtGui.QFormLayout.FieldRole, self.cmbVisitPayStatus)
        self.splitterTree = QtGui.QSplitter(ReportRecordPersonVisitsSetupDialog)
        self.splitterTree.setOrientation(QtCore.Qt.Horizontal)
        self.splitterTree.setObjectName(_fromUtf8("splitterTree"))
        self.treeItems = CSocStatusTreeView(self.splitterTree)
        self.treeItems.setMinimumSize(QtCore.QSize(204, 0))
        self.treeItems.setObjectName(_fromUtf8("treeItems"))
        self.lstItems = CRBListBox(self.splitterTree)
        self.lstItems.setMinimumSize(QtCore.QSize(204, 0))
        self.lstItems.setObjectName(_fromUtf8("lstItems"))
        self.formLayout.setWidget(12, QtGui.QFormLayout.SpanningRole, self.splitterTree)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportRecordPersonVisitsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblEventPurpose.setBuddy(self.cmbEventPurpose)
        self.lblEventType.setBuddy(self.cmbEventType)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblAge.setBuddy(self.edtAgeFrom)
        self.lblAgeTo.setBuddy(self.edtAgeTo)
        self.lblAgeYears.setBuddy(self.edtAgeTo)
        self.lblRowGrouping.setBuddy(self.cmbRowGrouping)

        self.retranslateUi(ReportRecordPersonVisitsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportRecordPersonVisitsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportRecordPersonVisitsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportRecordPersonVisitsSetupDialog)

    def retranslateUi(self, ReportRecordPersonVisitsSetupDialog):
        ReportRecordPersonVisitsSetupDialog.setWindowTitle(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Дата &начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Дата &окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDetailChildren.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Детализация по подросткам", None, QtGui.QApplication.UnicodeUTF8))
        self.chkVisitHospital.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Учитывать посещения ДС", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventPurpose.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "&Назначение обращения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventType.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "&Тип обращения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "&Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPerson.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "&Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPerson.setItemText(0, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSex.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "По&л", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(1, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "М", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(2, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Ж", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAge.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Во&зраст с", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeTo.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeYears.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "лет", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRowGrouping.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "&Строки по", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRowGrouping.setItemText(0, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Датам", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRowGrouping.setItemText(1, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Врачам", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRowGrouping.setItemText(2, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Подразделениям", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRowGrouping.setItemText(3, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Специальности", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRowGrouping.setItemText(4, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Должности", None, QtGui.QApplication.UnicodeUTF8))
        self.lblVisitPayStatus.setText(QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "Флаг финансирования", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbVisitPayStatus.setItemText(0, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "не задано", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbVisitPayStatus.setItemText(1, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "не выставлено", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbVisitPayStatus.setItemText(2, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "выставлено", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbVisitPayStatus.setItemText(3, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "отказано", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbVisitPayStatus.setItemText(4, QtGui.QApplication.translate("ReportRecordPersonVisitsSetupDialog", "оплачено", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.RBListBox import CRBListBox
from Registry.SocStatusComboBox import CSocStatusTreeView
from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportRecordPersonVisitsSetupDialog = QtGui.QDialog()
    ui = Ui_ReportRecordPersonVisitsSetupDialog()
    ui.setupUi(ReportRecordPersonVisitsSetupDialog)
    ReportRecordPersonVisitsSetupDialog.show()
    sys.exit(app.exec_())
