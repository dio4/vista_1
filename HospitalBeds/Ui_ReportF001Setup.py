# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\HospitalBeds\ReportF001Setup.ui'
#
# Created: Fri Jun 15 12:17:27 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportF001SetupDialog(object):
    def setupUi(self, ReportF001SetupDialog):
        ReportF001SetupDialog.setObjectName(_fromUtf8("ReportF001SetupDialog"))
        ReportF001SetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportF001SetupDialog.resize(528, 240)
        ReportF001SetupDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ReportF001SetupDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        spacerItem = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 9, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportF001SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 10, 0, 1, 2)
        self.label = QtGui.QLabel(ReportF001SetupDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 4, 0, 1, 1)
        self.lblCondSort = QtGui.QLabel(ReportF001SetupDialog)
        self.lblCondSort.setObjectName(_fromUtf8("lblCondSort"))
        self.gridlayout.addWidget(self.lblCondSort, 0, 0, 1, 1)
        self.cmbCondSort = QtGui.QComboBox(ReportF001SetupDialog)
        self.cmbCondSort.setObjectName(_fromUtf8("cmbCondSort"))
        self.cmbCondSort.addItem(_fromUtf8(""))
        self.cmbCondSort.addItem(_fromUtf8(""))
        self.cmbCondSort.addItem(_fromUtf8(""))
        self.cmbCondSort.addItem(_fromUtf8(""))
        self.cmbCondSort.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbCondSort, 0, 1, 1, 1)
        self.lblCondOrgStructure = QtGui.QLabel(ReportF001SetupDialog)
        self.lblCondOrgStructure.setObjectName(_fromUtf8("lblCondOrgStructure"))
        self.gridlayout.addWidget(self.lblCondOrgStructure, 1, 0, 1, 1)
        self.cmbCondOrgStructure = QtGui.QComboBox(ReportF001SetupDialog)
        self.cmbCondOrgStructure.setObjectName(_fromUtf8("cmbCondOrgStructure"))
        self.cmbCondOrgStructure.addItem(_fromUtf8(""))
        self.cmbCondOrgStructure.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbCondOrgStructure, 1, 1, 1, 1)
        self.lblCondMKB = QtGui.QLabel(ReportF001SetupDialog)
        self.lblCondMKB.setObjectName(_fromUtf8("lblCondMKB"))
        self.gridlayout.addWidget(self.lblCondMKB, 2, 0, 1, 1)
        self.cmbPrintTypeMKB = QtGui.QComboBox(ReportF001SetupDialog)
        self.cmbPrintTypeMKB.setObjectName(_fromUtf8("cmbPrintTypeMKB"))
        self.cmbPrintTypeMKB.addItem(_fromUtf8(""))
        self.cmbPrintTypeMKB.addItem(_fromUtf8(""))
        self.cmbPrintTypeMKB.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbPrintTypeMKB, 2, 1, 1, 1)
        self.chkClientId = QtGui.QCheckBox(ReportF001SetupDialog)
        self.chkClientId.setChecked(True)
        self.chkClientId.setObjectName(_fromUtf8("chkClientId"))
        self.gridlayout.addWidget(self.chkClientId, 4, 1, 1, 1)
        self.chkEventId = QtGui.QCheckBox(ReportF001SetupDialog)
        self.chkEventId.setObjectName(_fromUtf8("chkEventId"))
        self.gridlayout.addWidget(self.chkEventId, 5, 1, 1, 1)
        self.chkExternalEventId = QtGui.QCheckBox(ReportF001SetupDialog)
        self.chkExternalEventId.setObjectName(_fromUtf8("chkExternalEventId"))
        self.gridlayout.addWidget(self.chkExternalEventId, 6, 1, 1, 1)
        self.chkPrintTypeEvent = QtGui.QCheckBox(ReportF001SetupDialog)
        self.chkPrintTypeEvent.setObjectName(_fromUtf8("chkPrintTypeEvent"))
        self.gridlayout.addWidget(self.chkPrintTypeEvent, 3, 1, 1, 1)

        self.retranslateUi(ReportF001SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportF001SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportF001SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportF001SetupDialog)

    def retranslateUi(self, ReportF001SetupDialog):
        ReportF001SetupDialog.setWindowTitle(QtGui.QApplication.translate("ReportF001SetupDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ReportF001SetupDialog", "Номер карты стационарного больного:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCondSort.setText(QtGui.QApplication.translate("ReportF001SetupDialog", "Сортировка отчета", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCondSort.setItemText(0, QtGui.QApplication.translate("ReportF001SetupDialog", "по ФИО", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCondSort.setItemText(1, QtGui.QApplication.translate("ReportF001SetupDialog", "по дате и времени поступления", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCondSort.setItemText(2, QtGui.QApplication.translate("ReportF001SetupDialog", "по идентификатору пациента", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCondSort.setItemText(3, QtGui.QApplication.translate("ReportF001SetupDialog", "по внутреннему идентификатору события", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCondSort.setItemText(4, QtGui.QApplication.translate("ReportF001SetupDialog", "по внешнему идентификатору события", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCondOrgStructure.setText(QtGui.QApplication.translate("ReportF001SetupDialog", "Графа \"Отделение\"", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCondOrgStructure.setItemText(0, QtGui.QApplication.translate("ReportF001SetupDialog", "название подразделения", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbCondOrgStructure.setItemText(1, QtGui.QApplication.translate("ReportF001SetupDialog", "код подразделения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCondMKB.setText(QtGui.QApplication.translate("ReportF001SetupDialog", "Графа \"диагноз\"", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPrintTypeMKB.setItemText(0, QtGui.QApplication.translate("ReportF001SetupDialog", "текст", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPrintTypeMKB.setItemText(1, QtGui.QApplication.translate("ReportF001SetupDialog", "шифр МКБ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbPrintTypeMKB.setItemText(2, QtGui.QApplication.translate("ReportF001SetupDialog", "шифр МКБ и текст", None, QtGui.QApplication.UnicodeUTF8))
        self.chkClientId.setText(QtGui.QApplication.translate("ReportF001SetupDialog", "Внутренний идентификатор пациента", None, QtGui.QApplication.UnicodeUTF8))
        self.chkEventId.setText(QtGui.QApplication.translate("ReportF001SetupDialog", "Внутренний идентификатор карточки", None, QtGui.QApplication.UnicodeUTF8))
        self.chkExternalEventId.setText(QtGui.QApplication.translate("ReportF001SetupDialog", "Внешний идентификатор карточки", None, QtGui.QApplication.UnicodeUTF8))
        self.chkPrintTypeEvent.setText(QtGui.QApplication.translate("ReportF001SetupDialog", "Выводить тип финансирования", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportF001SetupDialog = QtGui.QDialog()
    ui = Ui_ReportF001SetupDialog()
    ui.setupUi(ReportF001SetupDialog)
    ReportF001SetupDialog.show()
    sys.exit(app.exec_())

