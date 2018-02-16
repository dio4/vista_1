# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\StationaryF007DCSetup.ui'
#
# Created: Fri Jun 15 12:17:58 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_StationaryF007DCSetupDialog(object):
    def setupUi(self, StationaryF007DCSetupDialog):
        StationaryF007DCSetupDialog.setObjectName(_fromUtf8("StationaryF007DCSetupDialog"))
        StationaryF007DCSetupDialog.resize(333, 300)
        StationaryF007DCSetupDialog.setSizeGripEnabled(False)
        self.label = QtGui.QLabel(StationaryF007DCSetupDialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 131, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(StationaryF007DCSetupDialog)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 131, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(StationaryF007DCSetupDialog)
        self.label_3.setGeometry(QtCore.QRect(10, 70, 131, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(StationaryF007DCSetupDialog)
        self.label_4.setGeometry(QtCore.QRect(10, 100, 131, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(StationaryF007DCSetupDialog)
        self.label_5.setGeometry(QtCore.QRect(10, 130, 131, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(StationaryF007DCSetupDialog)
        self.label_6.setGeometry(QtCore.QRect(10, 160, 131, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(StationaryF007DCSetupDialog)
        self.label_7.setGeometry(QtCore.QRect(10, 190, 131, 16))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.edtBegDate = CDateEdit(StationaryF007DCSetupDialog)
        self.edtBegDate.setGeometry(QtCore.QRect(150, 10, 110, 22))
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.edtEndDate = CDateEdit(StationaryF007DCSetupDialog)
        self.edtEndDate.setGeometry(QtCore.QRect(150, 40, 110, 22))
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.cmbEventType = CRBComboBox(StationaryF007DCSetupDialog)
        self.cmbEventType.setGeometry(QtCore.QRect(150, 70, 181, 22))
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.cmbSocStatusClass = CSocStatusComboBox(StationaryF007DCSetupDialog)
        self.cmbSocStatusClass.setGeometry(QtCore.QRect(150, 130, 181, 22))
        self.cmbSocStatusClass.setObjectName(_fromUtf8("cmbSocStatusClass"))
        self.cmbSocStatusType = CRBComboBox(StationaryF007DCSetupDialog)
        self.cmbSocStatusType.setGeometry(QtCore.QRect(150, 160, 181, 22))
        self.cmbSocStatusType.setObjectName(_fromUtf8("cmbSocStatusType"))
        self.cmbOrgStructure = COrgStructureComboBox(StationaryF007DCSetupDialog)
        self.cmbOrgStructure.setGeometry(QtCore.QRect(150, 100, 181, 22))
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.cmbLocality = QtGui.QComboBox(StationaryF007DCSetupDialog)
        self.cmbLocality.setGeometry(QtCore.QRect(150, 190, 181, 22))
        self.cmbLocality.setObjectName(_fromUtf8("cmbLocality"))
        self.cmbLocality.addItem(_fromUtf8(""))
        self.cmbLocality.addItem(_fromUtf8(""))
        self.cmbLocality.addItem(_fromUtf8(""))
        self.buttonBox = QtGui.QDialogButtonBox(StationaryF007DCSetupDialog)
        self.buttonBox.setGeometry(QtCore.QRect(5, 270, 321, 23))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(StationaryF007DCSetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StationaryF007DCSetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StationaryF007DCSetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StationaryF007DCSetupDialog)

    def retranslateUi(self, StationaryF007DCSetupDialog):
        StationaryF007DCSetupDialog.setWindowTitle(QtGui.QApplication.translate("StationaryF007DCSetupDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("StationaryF007DCSetupDialog", "Дата начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("StationaryF007DCSetupDialog", "Дата окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("StationaryF007DCSetupDialog", "Тип обращения", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("StationaryF007DCSetupDialog", "Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("StationaryF007DCSetupDialog", "Класс соц. статуса", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("StationaryF007DCSetupDialog", "Тип соц. статуса", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("StationaryF007DCSetupDialog", "Местность", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbLocality.setItemText(0, QtGui.QApplication.translate("StationaryF007DCSetupDialog", "Не учитывать", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbLocality.setItemText(1, QtGui.QApplication.translate("StationaryF007DCSetupDialog", "Городские жители", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbLocality.setItemText(2, QtGui.QApplication.translate("StationaryF007DCSetupDialog", "Сельские жители", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from Registry.SocStatusComboBox import CSocStatusComboBox
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    StationaryF007DCSetupDialog = QtGui.QDialog()
    ui = Ui_StationaryF007DCSetupDialog()
    ui.setupUi(StationaryF007DCSetupDialog)
    StationaryF007DCSetupDialog.show()
    sys.exit(app.exec_())

