# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\EmergencyTalonSignal.ui'
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

class Ui_EmergencyTalonSignalDialog(object):
    def setupUi(self, EmergencyTalonSignalDialog):
        EmergencyTalonSignalDialog.setObjectName(_fromUtf8("EmergencyTalonSignalDialog"))
        EmergencyTalonSignalDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        EmergencyTalonSignalDialog.resize(323, 146)
        EmergencyTalonSignalDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(EmergencyTalonSignalDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblBegDate = QtGui.QLabel(EmergencyTalonSignalDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridlayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(EmergencyTalonSignalDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridlayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(EmergencyTalonSignalDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridlayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 6, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(EmergencyTalonSignalDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 7, 0, 1, 3)
        self.lblTypeOrder = QtGui.QLabel(EmergencyTalonSignalDialog)
        self.lblTypeOrder.setObjectName(_fromUtf8("lblTypeOrder"))
        self.gridlayout.addWidget(self.lblTypeOrder, 2, 0, 1, 1)
        self.cmbTypeOrder = QtGui.QComboBox(EmergencyTalonSignalDialog)
        self.cmbTypeOrder.setObjectName(_fromUtf8("cmbTypeOrder"))
        self.cmbTypeOrder.addItem(_fromUtf8(""))
        self.cmbTypeOrder.setItemText(0, _fromUtf8(""))
        self.cmbTypeOrder.addItem(_fromUtf8(""))
        self.cmbTypeOrder.addItem(_fromUtf8(""))
        self.cmbTypeOrder.addItem(_fromUtf8(""))
        self.cmbTypeOrder.addItem(_fromUtf8(""))
        self.cmbTypeOrder.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbTypeOrder, 2, 1, 1, 2)
        self.edtBegTime = QtGui.QTimeEdit(EmergencyTalonSignalDialog)
        self.edtBegTime.setObjectName(_fromUtf8("edtBegTime"))
        self.gridlayout.addWidget(self.edtBegTime, 1, 1, 1, 1)
        self.edtEndTime = QtGui.QTimeEdit(EmergencyTalonSignalDialog)
        self.edtEndTime.setTime(QtCore.QTime(23, 59, 0))
        self.edtEndTime.setObjectName(_fromUtf8("edtEndTime"))
        self.gridlayout.addWidget(self.edtEndTime, 1, 2, 1, 1)
        self.chkWriteMKB = QtGui.QCheckBox(EmergencyTalonSignalDialog)
        self.chkWriteMKB.setCheckable(True)
        self.chkWriteMKB.setObjectName(_fromUtf8("chkWriteMKB"))
        self.gridlayout.addWidget(self.chkWriteMKB, 5, 0, 1, 3)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(EmergencyTalonSignalDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EmergencyTalonSignalDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EmergencyTalonSignalDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EmergencyTalonSignalDialog)
        EmergencyTalonSignalDialog.setTabOrder(self.edtBegDate, self.edtBegTime)
        EmergencyTalonSignalDialog.setTabOrder(self.edtBegTime, self.edtEndTime)
        EmergencyTalonSignalDialog.setTabOrder(self.edtEndTime, self.cmbTypeOrder)
        EmergencyTalonSignalDialog.setTabOrder(self.cmbTypeOrder, self.chkWriteMKB)
        EmergencyTalonSignalDialog.setTabOrder(self.chkWriteMKB, self.buttonBox)

    def retranslateUi(self, EmergencyTalonSignalDialog):
        EmergencyTalonSignalDialog.setWindowTitle(QtGui.QApplication.translate("EmergencyTalonSignalDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegDate.setText(QtGui.QApplication.translate("EmergencyTalonSignalDialog", "Дата", None, QtGui.QApplication.UnicodeUTF8))
        self.edtBegDate.setDisplayFormat(QtGui.QApplication.translate("EmergencyTalonSignalDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEndDate.setText(QtGui.QApplication.translate("EmergencyTalonSignalDialog", "Время", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTypeOrder.setText(QtGui.QApplication.translate("EmergencyTalonSignalDialog", "Тип вызова", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbTypeOrder.setItemText(1, QtGui.QApplication.translate("EmergencyTalonSignalDialog", "Первичный", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbTypeOrder.setItemText(2, QtGui.QApplication.translate("EmergencyTalonSignalDialog", "Повторный", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbTypeOrder.setItemText(3, QtGui.QApplication.translate("EmergencyTalonSignalDialog", "Активное посещение", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbTypeOrder.setItemText(4, QtGui.QApplication.translate("EmergencyTalonSignalDialog", "Перевозка", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbTypeOrder.setItemText(5, QtGui.QApplication.translate("EmergencyTalonSignalDialog", "Амбулаторно", None, QtGui.QApplication.UnicodeUTF8))
        self.edtBegTime.setDisplayFormat(QtGui.QApplication.translate("EmergencyTalonSignalDialog", "HH:mm", None, QtGui.QApplication.UnicodeUTF8))
        self.edtEndTime.setDisplayFormat(QtGui.QApplication.translate("EmergencyTalonSignalDialog", "HH:mm", None, QtGui.QApplication.UnicodeUTF8))
        self.chkWriteMKB.setText(QtGui.QApplication.translate("EmergencyTalonSignalDialog", "Выводить шифры МКБ", None, QtGui.QApplication.UnicodeUTF8))

from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    EmergencyTalonSignalDialog = QtGui.QDialog()
    ui = Ui_EmergencyTalonSignalDialog()
    ui.setupUi(EmergencyTalonSignalDialog)
    EmergencyTalonSignalDialog.show()
    sys.exit(app.exec_())

