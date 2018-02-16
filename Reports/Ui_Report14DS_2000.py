# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\StationaryMESF14DCSetup.ui'
#
# Created: Fri Jun 15 12:17:33 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Report14DS_2000_SetupDialog(object):
    def setupUi(self, StationaryMESF14DCDialog):
        StationaryMESF14DCDialog.setObjectName(_fromUtf8("StationaryMESF14DCDialog"))
        StationaryMESF14DCDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        StationaryMESF14DCDialog.resize(438, 267)
        StationaryMESF14DCDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(StationaryMESF14DCDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(StationaryMESF14DCDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(StationaryMESF14DCDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(StationaryMESF14DCDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.lblProfile = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblProfile.setObjectName(_fromUtf8("lblProfile"))
        self.gridLayout.addWidget(self.lblProfile, 5, 0, 1, 1)

        self.label = QtGui.QLabel(StationaryMESF14DCDialog)
        self.label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.label.setObjectName(_fromUtf8("label"))
        self.lstFilterProfile = CRBListBox(StationaryMESF14DCDialog)
        self.lstFilterProfile.setObjectName(_fromUtf8("lstFilterProfile"))
        self.gridLayout.addWidget(self.lstFilterProfile, 5, 1, 1, 2)

        self.lblAge = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout.addWidget(self.lblAge, 6, 0, 1, 1)
        self.cmbAge = QtGui.QComboBox(StationaryMESF14DCDialog)
        self.cmbAge.setObjectName(_fromUtf8("cmbAge"))
        self.cmbAge.addItem(_fromUtf8(""))
        self.cmbAge.addItem(_fromUtf8(""))
        self.cmbAge.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbAge, 6, 1, 1, 2)
        self.label.setBuddy(self.lstFilterProfile)

        self.lblRegularBed = QtGui.QLabel(StationaryMESF14DCDialog)
        self.lblRegularBed.setObjectName(_fromUtf8("lblRegularBed"))
        self.gridLayout.addWidget(self.lblRegularBed, 8, 0, 1, 1)
        self.cmbRegularBed = QtGui.QComboBox(StationaryMESF14DCDialog)
        self.cmbRegularBed.setObjectName(_fromUtf8("cmbRegularBed"))
        self.cmbRegularBed.addItem(_fromUtf8(""))
        self.cmbRegularBed.addItem(_fromUtf8(""))
        self.cmbRegularBed.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbRegularBed, 8, 1, 1, 2)

        spacerItem2 = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 11, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(StationaryMESF14DCDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 12, 0, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)

        self.retranslateUi(StationaryMESF14DCDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StationaryMESF14DCDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StationaryMESF14DCDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StationaryMESF14DCDialog)
        StationaryMESF14DCDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        StationaryMESF14DCDialog.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        StationaryMESF14DCDialog.setTabOrder(self.cmbOrgStructure, self.lstFilterProfile)
        StationaryMESF14DCDialog.setTabOrder(self.lstFilterProfile, self.buttonBox)
        # StationaryMESF14DCDialog.setTabOrder(self.cmbFilterDS, self.buttonBox)
        # StationaryMESF14DCDialog.setTabOrder(self.cmbrbNet)


    def retranslateUi(self, StationaryMESF14DCDialog):
        StationaryMESF14DCDialog.setWindowTitle(QtGui.QApplication.translate("StationaryMESF14DCDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "Дата &начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.edtBegDate.setDisplayFormat(QtGui.QApplication.translate("StationaryMESF14DCDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "Дата &окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.edtEndDate.setDisplayFormat(QtGui.QApplication.translate("StationaryMESF14DCDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "&Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblProfile.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "Профиль койки", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAge.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "Возраст", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRegularBed.setText(QtGui.QApplication.translate("StationaryMESF14DCDialog", "Учитывать штатные койки", None,
                                                        QtGui.QApplication.UnicodeUTF8))

        self.cmbAge.setItemText(0, QtGui.QApplication.translate("StationaryMESF14DCDialog", "Все", None,
                                                                      QtGui.QApplication.UnicodeUTF8))
        self.cmbAge.setItemText(1, QtGui.QApplication.translate("StationaryMESF14DCDialog", "0-18", None,
                                                                      QtGui.QApplication.UnicodeUTF8))
        self.cmbAge.setItemText(2, QtGui.QApplication.translate("StationaryMESF14DCDialog", "18-150", None,
                                                                      QtGui.QApplication.UnicodeUTF8))

        self.cmbRegularBed.setItemText(0, QtGui.QApplication.translate("StationaryMESF14DCDialog", "Все", None,
                                                                QtGui.QApplication.UnicodeUTF8))
        self.cmbRegularBed.setItemText(1, QtGui.QApplication.translate("StationaryMESF14DCDialog", "Учитывать штатные койки", None,
                                                                QtGui.QApplication.UnicodeUTF8))
        self.cmbRegularBed.setItemText(2, QtGui.QApplication.translate("StationaryMESF14DCDialog", "Учитывать нештатные койки", None,
                                                                QtGui.QApplication.UnicodeUTF8))


from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.RBListBox import CRBListBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    StationaryMESF14DCDialog = QtGui.QDialog()
    ui = Ui_Report14DS_2000_SetupDialog()
    ui.setupUi(StationaryMESF14DCDialog)
    StationaryMESF14DCDialog.show()
    sys.exit(app.exec_())

