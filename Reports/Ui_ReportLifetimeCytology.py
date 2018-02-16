# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportLifetimeCytology.ui'
#
# Created: Thu Feb  6 14:20:24 2014
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ReportLifetimeCytology(object):
    def setupUi(self, ReportLifetimeCytology):
        ReportLifetimeCytology.setObjectName(_fromUtf8("ReportLifetimeCytology"))
        ReportLifetimeCytology.resize(351, 153)
        ReportLifetimeCytology.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.gridLayout = QtGui.QGridLayout(ReportLifetimeCytology)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegDate = QtGui.QLabel(ReportLifetimeCytology)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportLifetimeCytology)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 2, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportLifetimeCytology)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 1, 1, 2)
        self.edtBegDate = CDateEdit(ReportLifetimeCytology)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        self.edtEndDate = CDateEdit(ReportLifetimeCytology)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 2, 2, 1, 1)
        self.label = QtGui.QLabel(ReportLifetimeCytology)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 5, 0, 1, 1)
        self.cmbComplexityCategory = QtGui.QComboBox(ReportLifetimeCytology)
        self.cmbComplexityCategory.setObjectName(_fromUtf8("cmbComplexityCategory"))
        self.cmbComplexityCategory.addItem(_fromUtf8(""))
        self.cmbComplexityCategory.addItem(_fromUtf8(""))
        self.cmbComplexityCategory.addItem(_fromUtf8(""))
        self.cmbComplexityCategory.addItem(_fromUtf8(""))
        self.cmbComplexityCategory.addItem(_fromUtf8(""))
        self.cmbComplexityCategory.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbComplexityCategory, 5, 2, 1, 1)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportLifetimeCytology)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportLifetimeCytology.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportLifetimeCytology.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportLifetimeCytology)
        ReportLifetimeCytology.setTabOrder(self.edtBegDate, self.edtEndDate)

    def retranslateUi(self, ReportLifetimeCytology):
        ReportLifetimeCytology.setWindowTitle(_translate("ReportLifetimeCytology", "Dialog", None))
        self.lblBegDate.setText(_translate("ReportLifetimeCytology", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportLifetimeCytology", "Дата &окончания периода", None))
        self.label.setText(_translate("ReportLifetimeCytology", "Категория сложности", None))
        self.cmbComplexityCategory.setItemText(0, _translate("ReportLifetimeCytology", "не задано", None))
        self.cmbComplexityCategory.setItemText(1, _translate("ReportLifetimeCytology", "I", None))
        self.cmbComplexityCategory.setItemText(2, _translate("ReportLifetimeCytology", "II", None))
        self.cmbComplexityCategory.setItemText(3, _translate("ReportLifetimeCytology", "III", None))
        self.cmbComplexityCategory.setItemText(4, _translate("ReportLifetimeCytology", "IV", None))
        self.cmbComplexityCategory.setItemText(5, _translate("ReportLifetimeCytology", "V", None))

from library.DateEdit import CDateEdit
