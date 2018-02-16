# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ExportLOFOMSPage1.ui'
#
# Created: Fri Jun 15 12:16:12 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ExportLOFOMSPage1(object):
    def setupUi(self, ExportLOFOMSPage1):
        ExportLOFOMSPage1.setObjectName(_fromUtf8("ExportLOFOMSPage1"))
        ExportLOFOMSPage1.resize(400, 300)
        self.gridlayout = QtGui.QGridLayout(ExportLOFOMSPage1)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblFluorography = QtGui.QLabel(ExportLOFOMSPage1)
        self.lblFluorography.setObjectName(_fromUtf8("lblFluorography"))
        self.gridlayout.addWidget(self.lblFluorography, 0, 0, 1, 1)
        self.cmbActionTypeFluorography = CActionTypeComboBox(ExportLOFOMSPage1)
        self.cmbActionTypeFluorography.setObjectName(_fromUtf8("cmbActionTypeFluorography"))
        self.gridlayout.addWidget(self.cmbActionTypeFluorography, 1, 0, 1, 2)
        self.lblCytological = QtGui.QLabel(ExportLOFOMSPage1)
        self.lblCytological.setObjectName(_fromUtf8("lblCytological"))
        self.gridlayout.addWidget(self.lblCytological, 2, 0, 1, 1)
        self.cmbActionTypeCytological = CActionTypeComboBox(ExportLOFOMSPage1)
        self.cmbActionTypeCytological.setObjectName(_fromUtf8("cmbActionTypeCytological"))
        self.gridlayout.addWidget(self.cmbActionTypeCytological, 3, 0, 1, 2)
        self.gbAccountParams = QtGui.QGroupBox(ExportLOFOMSPage1)
        self.gbAccountParams.setObjectName(_fromUtf8("gbAccountParams"))
        self.verticalLayout = QtGui.QVBoxLayout(self.gbAccountParams)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.chkRFAccount = QtGui.QCheckBox(self.gbAccountParams)
        self.chkRFAccount.setObjectName(_fromUtf8("chkRFAccount"))
        self.verticalLayout.addWidget(self.chkRFAccount)
        self.lblAccountType = QtGui.QLabel(self.gbAccountParams)
        self.lblAccountType.setObjectName(_fromUtf8("lblAccountType"))
        self.verticalLayout.addWidget(self.lblAccountType)
        self.cmbAccountType = QtGui.QComboBox(self.gbAccountParams)
        self.cmbAccountType.setObjectName(_fromUtf8("cmbAccountType"))
        self.cmbAccountType.addItem(_fromUtf8(""))
        self.cmbAccountType.addItem(_fromUtf8(""))
        self.cmbAccountType.addItem(_fromUtf8(""))
        self.cmbAccountType.addItem(_fromUtf8(""))
        self.cmbAccountType.addItem(_fromUtf8(""))
        self.cmbAccountType.addItem(_fromUtf8(""))
        self.cmbAccountType.addItem(_fromUtf8(""))
        self.cmbAccountType.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.cmbAccountType)
        self.gridlayout.addWidget(self.gbAccountParams, 4, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 5, 0, 1, 1)

        self.retranslateUi(ExportLOFOMSPage1)
        QtCore.QMetaObject.connectSlotsByName(ExportLOFOMSPage1)

    def retranslateUi(self, ExportLOFOMSPage1):
        ExportLOFOMSPage1.setWindowTitle(QtGui.QApplication.translate("ExportLOFOMSPage1", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFluorography.setText(QtGui.QApplication.translate("ExportLOFOMSPage1", "Укажите тип действия для анализа \"Флюорография\":", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCytological.setText(QtGui.QApplication.translate("ExportLOFOMSPage1", "Укажите тип действия для анализа \"Цитологическое исследование\"", None, QtGui.QApplication.UnicodeUTF8))
        self.gbAccountParams.setTitle(QtGui.QApplication.translate("ExportLOFOMSPage1", "Свойства счета", None, QtGui.QApplication.UnicodeUTF8))
        self.chkRFAccount.setText(QtGui.QApplication.translate("ExportLOFOMSPage1", "Счет по РФ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAccountType.setText(QtGui.QApplication.translate("ExportLOFOMSPage1", "Категория счета:", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAccountType.setItemText(0, QtGui.QApplication.translate("ExportLOFOMSPage1", "счет за застрахованных жителей Лен.области", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAccountType.setItemText(1, QtGui.QApplication.translate("ExportLOFOMSPage1", "счет за иные категории граждан (условно застрахованные)", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAccountType.setItemText(2, QtGui.QApplication.translate("ExportLOFOMSPage1", "счет за жителей других субъектов РФ (кроме СПб)", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAccountType.setItemText(3, QtGui.QApplication.translate("ExportLOFOMSPage1", "счет за жителей Лен. обл., работающих на предприятиях РФ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAccountType.setItemText(4, QtGui.QApplication.translate("ExportLOFOMSPage1", "счет за застрахованных жителей Лен.обл. по стоматологии", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAccountType.setItemText(5, QtGui.QApplication.translate("ExportLOFOMSPage1", "счет за иные категории граждан (условно застрахованные) по стоматологии", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAccountType.setItemText(6, QtGui.QApplication.translate("ExportLOFOMSPage1", "счет за жителей других субъектов РФ (кроме СПб) по стоматологии", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbAccountType.setItemText(7, QtGui.QApplication.translate("ExportLOFOMSPage1", "счет за жителей Лен. обл., работающих на предприятиях РФ по стоматологии", None, QtGui.QApplication.UnicodeUTF8))

from Events.ActionTypeComboBox import CActionTypeComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ExportLOFOMSPage1 = QtGui.QWidget()
    ui = Ui_ExportLOFOMSPage1()
    ui.setupUi(ExportLOFOMSPage1)
    ExportLOFOMSPage1.show()
    sys.exit(app.exec_())

