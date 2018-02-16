# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Timeline\AbsenceDialog.ui'
#
# Created: Fri Jun 15 12:16:41 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_AbsenceDialog(object):
    def setupUi(self, AbsenceDialog):
        AbsenceDialog.setObjectName(_fromUtf8("AbsenceDialog"))
        AbsenceDialog.resize(353, 130)
        self.gridLayout = QtGui.QGridLayout(AbsenceDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.dateRangeLayout = QtGui.QHBoxLayout()
        self.dateRangeLayout.setSpacing(4)
        self.dateRangeLayout.setObjectName(_fromUtf8("dateRangeLayout"))
        self.lblBegDate = QtGui.QLabel(AbsenceDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.dateRangeLayout.addWidget(self.lblBegDate)
        self.edtBegDate = CDateEdit(AbsenceDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.dateRangeLayout.addWidget(self.edtBegDate)
        self.lblEndDate = QtGui.QLabel(AbsenceDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.dateRangeLayout.addWidget(self.lblEndDate)
        self.edtEndDate = CDateEdit(AbsenceDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.dateRangeLayout.addWidget(self.edtEndDate)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.dateRangeLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.dateRangeLayout, 0, 0, 1, 3)
        self.chkFillRedDays = QtGui.QCheckBox(AbsenceDialog)
        self.chkFillRedDays.setChecked(True)
        self.chkFillRedDays.setObjectName(_fromUtf8("chkFillRedDays"))
        self.gridLayout.addWidget(self.chkFillRedDays, 3, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(AbsenceDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 2, 1, 1)
        self.lblReasonOfAbsence = QtGui.QLabel(AbsenceDialog)
        self.lblReasonOfAbsence.setAlignment(QtCore.Qt.AlignCenter)
        self.lblReasonOfAbsence.setObjectName(_fromUtf8("lblReasonOfAbsence"))
        self.gridLayout.addWidget(self.lblReasonOfAbsence, 1, 0, 1, 1)
        self.cmbReasonOfAbsence = CRBComboBox(AbsenceDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbReasonOfAbsence.sizePolicy().hasHeightForWidth())
        self.cmbReasonOfAbsence.setSizePolicy(sizePolicy)
        self.cmbReasonOfAbsence.setObjectName(_fromUtf8("cmbReasonOfAbsence"))
        self.gridLayout.addWidget(self.cmbReasonOfAbsence, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 4, 0, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(AbsenceDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AbsenceDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AbsenceDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AbsenceDialog)
        AbsenceDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        AbsenceDialog.setTabOrder(self.edtEndDate, self.cmbReasonOfAbsence)
        AbsenceDialog.setTabOrder(self.cmbReasonOfAbsence, self.chkFillRedDays)
        AbsenceDialog.setTabOrder(self.chkFillRedDays, self.buttonBox)

    def retranslateUi(self, AbsenceDialog):
        AbsenceDialog.setWindowTitle(QtGui.QApplication.translate("AbsenceDialog", "Шаблон планировщика", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("AbsenceDialog", "В период &с", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("AbsenceDialog", "&По", None, QtGui.QApplication.UnicodeUTF8))
        self.chkFillRedDays.setText(QtGui.QApplication.translate("AbsenceDialog", "&Заполнять выходные дни", None, QtGui.QApplication.UnicodeUTF8))
        self.lblReasonOfAbsence.setText(QtGui.QApplication.translate("AbsenceDialog", "Причина отсутствия", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    AbsenceDialog = QtGui.QDialog()
    ui = Ui_AbsenceDialog()
    ui.setupUi(AbsenceDialog)
    AbsenceDialog.show()
    sys.exit(app.exec_())

