# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\PersonVisitsSetup.ui'
#
# Created: Fri Jun 15 12:15:52 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PersonVisitsSetupDialog(object):
    def setupUi(self, PersonVisitsSetupDialog):
        PersonVisitsSetupDialog.setObjectName(_fromUtf8("PersonVisitsSetupDialog"))
        PersonVisitsSetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PersonVisitsSetupDialog.resize(341, 317)
        PersonVisitsSetupDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(PersonVisitsSetupDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblBegDate = QtGui.QLabel(PersonVisitsSetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridlayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(PersonVisitsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridlayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.lblEndDate = QtGui.QLabel(PersonVisitsSetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridlayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(PersonVisitsSetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridlayout.addWidget(self.edtEndDate, 1, 1, 1, 2)
        self.lblPerson = QtGui.QLabel(PersonVisitsSetupDialog)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridlayout.addWidget(self.lblPerson, 4, 0, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(PersonVisitsSetupDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbPerson, 4, 1, 1, 4)
        self.lblEventPurpose = QtGui.QLabel(PersonVisitsSetupDialog)
        self.lblEventPurpose.setObjectName(_fromUtf8("lblEventPurpose"))
        self.gridlayout.addWidget(self.lblEventPurpose, 5, 0, 1, 1)
        self.cmbEventPurpose = CRBComboBox(PersonVisitsSetupDialog)
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.gridlayout.addWidget(self.cmbEventPurpose, 5, 1, 1, 4)
        self.lblEventType = QtGui.QLabel(PersonVisitsSetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridlayout.addWidget(self.lblEventType, 6, 0, 1, 1)
        self.cmbEventType = CRBComboBox(PersonVisitsSetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridlayout.addWidget(self.cmbEventType, 6, 1, 1, 4)
        self.lblScene = QtGui.QLabel(PersonVisitsSetupDialog)
        self.lblScene.setObjectName(_fromUtf8("lblScene"))
        self.gridlayout.addWidget(self.lblScene, 7, 0, 1, 1)
        self.cmbScene = CRBComboBox(PersonVisitsSetupDialog)
        self.cmbScene.setObjectName(_fromUtf8("cmbScene"))
        self.gridlayout.addWidget(self.cmbScene, 7, 1, 1, 4)
        self.lblWorkOrganisation = QtGui.QLabel(PersonVisitsSetupDialog)
        self.lblWorkOrganisation.setObjectName(_fromUtf8("lblWorkOrganisation"))
        self.gridlayout.addWidget(self.lblWorkOrganisation, 8, 0, 1, 1)
        self.cmbWorkOrganisation = COrgComboBox(PersonVisitsSetupDialog)
        self.cmbWorkOrganisation.setObjectName(_fromUtf8("cmbWorkOrganisation"))
        self.gridlayout.addWidget(self.cmbWorkOrganisation, 8, 1, 1, 3)
        self.btnSelectWorkOrganisation = QtGui.QToolButton(PersonVisitsSetupDialog)
        self.btnSelectWorkOrganisation.setArrowType(QtCore.Qt.NoArrow)
        self.btnSelectWorkOrganisation.setObjectName(_fromUtf8("btnSelectWorkOrganisation"))
        self.gridlayout.addWidget(self.btnSelectWorkOrganisation, 8, 4, 1, 1)
        self.lblSex = QtGui.QLabel(PersonVisitsSetupDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridlayout.addWidget(self.lblSex, 9, 0, 1, 1)
        self.cmbSex = QtGui.QComboBox(PersonVisitsSetupDialog)
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
        self.gridlayout.addWidget(self.cmbSex, 9, 1, 1, 1)
        self.lblAge = QtGui.QLabel(PersonVisitsSetupDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridlayout.addWidget(self.lblAge, 10, 0, 1, 1)
        self.frmAge = QtGui.QFrame(PersonVisitsSetupDialog)
        self.frmAge.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAge.setFrameShadow(QtGui.QFrame.Raised)
        self.frmAge.setObjectName(_fromUtf8("frmAge"))
        self.hboxlayout = QtGui.QHBoxLayout(self.frmAge)
        self.hboxlayout.setSpacing(4)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.edtAgeFrom = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeFrom.sizePolicy().hasHeightForWidth())
        self.edtAgeFrom.setSizePolicy(sizePolicy)
        self.edtAgeFrom.setMaximum(150)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self.hboxlayout.addWidget(self.edtAgeFrom)
        self.lblAgeTo = QtGui.QLabel(self.frmAge)
        self.lblAgeTo.setObjectName(_fromUtf8("lblAgeTo"))
        self.hboxlayout.addWidget(self.lblAgeTo)
        self.edtAgeTo = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeTo.sizePolicy().hasHeightForWidth())
        self.edtAgeTo.setSizePolicy(sizePolicy)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self.hboxlayout.addWidget(self.edtAgeTo)
        self.lblAgeYears = QtGui.QLabel(self.frmAge)
        self.lblAgeYears.setObjectName(_fromUtf8("lblAgeYears"))
        self.hboxlayout.addWidget(self.lblAgeYears)
        spacerItem = QtGui.QSpacerItem(21, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.gridlayout.addWidget(self.frmAge, 10, 1, 1, 4)
        spacerItem1 = QtGui.QSpacerItem(111, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 11, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PersonVisitsSetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 12, 0, 1, 5)
        self.cmbOrgStructure = COrgStructureComboBox(PersonVisitsSetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridlayout.addWidget(self.cmbOrgStructure, 3, 1, 1, 4)
        self.lblOrgStructure = QtGui.QLabel(PersonVisitsSetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridlayout.addWidget(self.lblOrgStructure, 3, 0, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblEventPurpose.setBuddy(self.cmbPerson)
        self.lblEventType.setBuddy(self.cmbPerson)
        self.lblScene.setBuddy(self.cmbPerson)
        self.lblWorkOrganisation.setBuddy(self.cmbWorkOrganisation)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblAge.setBuddy(self.edtAgeFrom)
        self.lblAgeTo.setBuddy(self.edtAgeTo)
        self.lblAgeYears.setBuddy(self.edtAgeTo)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(PersonVisitsSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PersonVisitsSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PersonVisitsSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PersonVisitsSetupDialog)
        PersonVisitsSetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        PersonVisitsSetupDialog.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        PersonVisitsSetupDialog.setTabOrder(self.cmbOrgStructure, self.cmbPerson)
        PersonVisitsSetupDialog.setTabOrder(self.cmbPerson, self.cmbEventPurpose)
        PersonVisitsSetupDialog.setTabOrder(self.cmbEventPurpose, self.cmbEventType)
        PersonVisitsSetupDialog.setTabOrder(self.cmbEventType, self.cmbScene)
        PersonVisitsSetupDialog.setTabOrder(self.cmbScene, self.cmbWorkOrganisation)
        PersonVisitsSetupDialog.setTabOrder(self.cmbWorkOrganisation, self.btnSelectWorkOrganisation)
        PersonVisitsSetupDialog.setTabOrder(self.btnSelectWorkOrganisation, self.cmbSex)
        PersonVisitsSetupDialog.setTabOrder(self.cmbSex, self.edtAgeFrom)
        PersonVisitsSetupDialog.setTabOrder(self.edtAgeFrom, self.edtAgeTo)
        PersonVisitsSetupDialog.setTabOrder(self.edtAgeTo, self.buttonBox)

    def retranslateUi(self, PersonVisitsSetupDialog):
        PersonVisitsSetupDialog.setWindowTitle(QtGui.QApplication.translate("PersonVisitsSetupDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "Дата начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "Дата окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPerson.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "&Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPerson.setItemText(0, QtGui.QApplication.translate("PersonVisitsSetupDialog", "Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventPurpose.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "&Назначение обращения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventType.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "&Тип обращения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblScene.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "&Место", None, QtGui.QApplication.UnicodeUTF8))
        self.lblWorkOrganisation.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "Занятость", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectWorkOrganisation.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSex.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "По&л", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(1, QtGui.QApplication.translate("PersonVisitsSetupDialog", "М", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(2, QtGui.QApplication.translate("PersonVisitsSetupDialog", "Ж", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAge.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "Во&зраст с", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeTo.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeYears.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "лет", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("PersonVisitsSetupDialog", "&Подразделение", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.OrgComboBox import COrgComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PersonVisitsSetupDialog = QtGui.QDialog()
    ui = Ui_PersonVisitsSetupDialog()
    ui.setupUi(PersonVisitsSetupDialog)
    PersonVisitsSetupDialog.show()
    sys.exit(app.exec_())
