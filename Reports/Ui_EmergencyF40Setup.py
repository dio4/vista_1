# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\EmergencyF40Setup.ui'
#
# Created: Fri Jun 15 12:16:27 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_EmergencyF40SetupDialog(object):
    def setupUi(self, EmergencyF40SetupDialog):
        EmergencyF40SetupDialog.setObjectName(_fromUtf8("EmergencyF40SetupDialog"))
        EmergencyF40SetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        EmergencyF40SetupDialog.resize(323, 117)
        EmergencyF40SetupDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(EmergencyF40SetupDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblBegDate = QtGui.QLabel(EmergencyF40SetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridlayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(EmergencyF40SetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridlayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(EmergencyF40SetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridlayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.edtEndDate = CDateEdit(EmergencyF40SetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridlayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 1, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem2, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(EmergencyF40SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 5, 0, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(EmergencyF40SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EmergencyF40SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EmergencyF40SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EmergencyF40SetupDialog)
        EmergencyF40SetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        EmergencyF40SetupDialog.setTabOrder(self.edtEndDate, self.buttonBox)

    def retranslateUi(self, EmergencyF40SetupDialog):
        EmergencyF40SetupDialog.setWindowTitle(QtGui.QApplication.translate("EmergencyF40SetupDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("EmergencyF40SetupDialog", "Дата &начала периода", None, QtGui.QApplication.UnicodeUTF8))
        self.edtBegDate.setDisplayFormat(QtGui.QApplication.translate("EmergencyF40SetupDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("EmergencyF40SetupDialog", "Дата &окончания периода", None, QtGui.QApplication.UnicodeUTF8))
        self.edtEndDate.setDisplayFormat(QtGui.QApplication.translate("EmergencyF40SetupDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))

from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    EmergencyF40SetupDialog = QtGui.QDialog()
    ui = Ui_EmergencyF40SetupDialog()
    ui.setupUi(EmergencyF40SetupDialog)
    EmergencyF40SetupDialog.show()
    sys.exit(app.exec_())

