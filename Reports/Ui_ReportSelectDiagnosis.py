# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportSelectDiagnosis.ui'
#
# Created: Mon Feb 10 19:53:52 2014
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

class Ui_ReportSelectionDiagnosis(object):
    def setupUi(self, ReportSelectionDiagnosis):
        ReportSelectionDiagnosis.setObjectName(_fromUtf8("ReportSelectionDiagnosis"))
        ReportSelectionDiagnosis.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportSelectionDiagnosis.resize(442, 217)
        ReportSelectionDiagnosis.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ReportSelectionDiagnosis)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.frmMKBEx = QtGui.QFrame(ReportSelectionDiagnosis)
        self.frmMKBEx.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmMKBEx.setFrameShadow(QtGui.QFrame.Raised)
        self.frmMKBEx.setObjectName(_fromUtf8("frmMKBEx"))
        self.gridlayout = QtGui.QGridLayout(self.frmMKBEx)
        self.gridlayout.setMargin(0)
        self.gridlayout.setHorizontalSpacing(4)
        self.gridlayout.setVerticalSpacing(0)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.gridLayout.addWidget(self.frmMKBEx, 6, 1, 2, 4)
        self.lblOrgStructure = QtGui.QLabel(ReportSelectionDiagnosis)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 2, 0, 1, 1)
        self.lblPerson = QtGui.QLabel(ReportSelectionDiagnosis)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout.addWidget(self.lblPerson, 3, 0, 1, 1)
        self.lblMKB = QtGui.QLabel(ReportSelectionDiagnosis)
        self.lblMKB.setObjectName(_fromUtf8("lblMKB"))
        self.gridLayout.addWidget(self.lblMKB, 5, 0, 1, 1)
        self.frmMKB = QtGui.QFrame(ReportSelectionDiagnosis)
        self.frmMKB.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmMKB.setFrameShadow(QtGui.QFrame.Raised)
        self.frmMKB.setObjectName(_fromUtf8("frmMKB"))
        self.gridlayout1 = QtGui.QGridLayout(self.frmMKB)
        self.gridlayout1.setMargin(0)
        self.gridlayout1.setHorizontalSpacing(4)
        self.gridlayout1.setVerticalSpacing(0)
        self.gridlayout1.setObjectName(_fromUtf8("gridlayout1"))
        self.cmbMKBFilter = QtGui.QComboBox(self.frmMKB)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbMKBFilter.sizePolicy().hasHeightForWidth())
        self.cmbMKBFilter.setSizePolicy(sizePolicy)
        self.cmbMKBFilter.setObjectName(_fromUtf8("cmbMKBFilter"))
        self.cmbMKBFilter.addItem(_fromUtf8(""))
        self.cmbMKBFilter.addItem(_fromUtf8(""))
        self.gridlayout1.addWidget(self.cmbMKBFilter, 0, 0, 1, 1)
        self.edtMKBFrom = CICDCodeEdit(self.frmMKB)
        self.edtMKBFrom.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMKBFrom.sizePolicy().hasHeightForWidth())
        self.edtMKBFrom.setSizePolicy(sizePolicy)
        self.edtMKBFrom.setMaximumSize(QtCore.QSize(40, 16777215))
        self.edtMKBFrom.setMaxLength(6)
        self.edtMKBFrom.setObjectName(_fromUtf8("edtMKBFrom"))
        self.gridlayout1.addWidget(self.edtMKBFrom, 0, 1, 1, 1)
        self.edtMKBTo = CICDCodeEdit(self.frmMKB)
        self.edtMKBTo.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMKBTo.sizePolicy().hasHeightForWidth())
        self.edtMKBTo.setSizePolicy(sizePolicy)
        self.edtMKBTo.setMaximumSize(QtCore.QSize(40, 16777215))
        self.edtMKBTo.setMaxLength(6)
        self.edtMKBTo.setObjectName(_fromUtf8("edtMKBTo"))
        self.gridlayout1.addWidget(self.edtMKBTo, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.frmMKB, 5, 1, 1, 4)
        self.cmbPerson = CPersonComboBoxEx(ReportSelectionDiagnosis)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.cmbPerson.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbPerson, 3, 1, 1, 4)
        self.edtBegDate = CDateEdit(ReportSelectionDiagnosis)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ReportSelectionDiagnosis)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 8, 0, 1, 5)
        self.cmbOrgStructure = COrgStructureComboBox(ReportSelectionDiagnosis)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 2, 1, 1, 4)
        self.frmAge = QtGui.QFrame(ReportSelectionDiagnosis)
        self.frmAge.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAge.setFrameShadow(QtGui.QFrame.Raised)
        self.frmAge.setObjectName(_fromUtf8("frmAge"))
        self.hboxlayout = QtGui.QHBoxLayout(self.frmAge)
        self.hboxlayout.setSpacing(4)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.gridLayout.addWidget(self.frmAge, 4, 1, 1, 4)
        self.lblBegDate = QtGui.QLabel(ReportSelectionDiagnosis)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 3, 1, 2)
        self.edtEndDate = CDateEdit(ReportSelectionDiagnosis)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 3, 1, 2)
        self.lblEndDate = QtGui.QLabel(ReportSelectionDiagnosis)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblPerson.setBuddy(self.cmbPerson)
        self.lblMKB.setBuddy(self.cmbMKBFilter)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(ReportSelectionDiagnosis)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportSelectionDiagnosis.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportSelectionDiagnosis.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportSelectionDiagnosis)
        ReportSelectionDiagnosis.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportSelectionDiagnosis.setTabOrder(self.edtEndDate, self.cmbOrgStructure)
        ReportSelectionDiagnosis.setTabOrder(self.cmbOrgStructure, self.cmbPerson)
        ReportSelectionDiagnosis.setTabOrder(self.cmbPerson, self.cmbMKBFilter)
        ReportSelectionDiagnosis.setTabOrder(self.cmbMKBFilter, self.edtMKBFrom)
        ReportSelectionDiagnosis.setTabOrder(self.edtMKBFrom, self.edtMKBTo)
        ReportSelectionDiagnosis.setTabOrder(self.edtMKBTo, self.buttonBox)

    def retranslateUi(self, ReportSelectionDiagnosis):
        ReportSelectionDiagnosis.setWindowTitle(_translate("ReportSelectionDiagnosis", "параметры отчёта", None))
        self.lblOrgStructure.setText(_translate("ReportSelectionDiagnosis", "&Подразделение", None))
        self.lblPerson.setText(_translate("ReportSelectionDiagnosis", "&Врач", None))
        self.lblMKB.setText(_translate("ReportSelectionDiagnosis", "Коды диагнозов по &МКБ", None))
        self.cmbMKBFilter.setItemText(0, _translate("ReportSelectionDiagnosis", "Игнор.", None))
        self.cmbMKBFilter.setItemText(1, _translate("ReportSelectionDiagnosis", "Интервал", None))
        self.edtMKBFrom.setInputMask(_translate("ReportSelectionDiagnosis", "a00.00; ", None))
        self.edtMKBFrom.setText(_translate("ReportSelectionDiagnosis", "A.", None))
        self.edtMKBTo.setInputMask(_translate("ReportSelectionDiagnosis", "a00.00; ", None))
        self.edtMKBTo.setText(_translate("ReportSelectionDiagnosis", "Z99.9", None))
        self.cmbPerson.setWhatsThis(_translate("ReportSelectionDiagnosis", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None))
        self.cmbPerson.setItemText(0, _translate("ReportSelectionDiagnosis", "Врач", None))
        self.lblBegDate.setText(_translate("ReportSelectionDiagnosis", "Дата &начала периода", None))
        self.lblEndDate.setText(_translate("ReportSelectionDiagnosis", "Дата &окончания периода", None))

from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.ICDCodeEdit import CICDCodeEdit
from library.DateEdit import CDateEdit
from Orgs.OrgStructComboBoxes import COrgStructureComboBox