# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ExportFedRegPerPage1.ui'
#
# Created: Fri Apr 11 13:40:12 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_ExportFedRegPerPage1SetupDialog(object):
    def setupUi(self, ExportFedRegPerPage1SetupDialog):
        ExportFedRegPerPage1SetupDialog.setObjectName(_fromUtf8("ExportFedRegPerPage1SetupDialog"))
        ExportFedRegPerPage1SetupDialog.resize(473, 394)
        self.gridLayout = QtGui.QGridLayout(ExportFedRegPerPage1SetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.btnExport = QtGui.QPushButton(ExportFedRegPerPage1SetupDialog)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.hboxlayout.addWidget(self.btnExport)
        self.btnClose = QtGui.QPushButton(ExportFedRegPerPage1SetupDialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.hboxlayout, 5, 1, 1, 1)
        self.splitter = QtGui.QSplitter(ExportFedRegPerPage1SetupDialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.vboxlayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem1)
        self.progressBar = CProgressBar(self.layoutWidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.vboxlayout.addWidget(self.progressBar)
        self.gridLayout.addWidget(self.splitter, 4, 1, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.lblOrganisation = QtGui.QLabel(ExportFedRegPerPage1SetupDialog)
        self.lblOrganisation.setObjectName(_fromUtf8("lblOrganisation"))
        self.horizontalLayout_4.addWidget(self.lblOrganisation)
        self.cmbOrganisation = COrgComboBox(ExportFedRegPerPage1SetupDialog)
        self.cmbOrganisation.setObjectName(_fromUtf8("cmbOrganisation"))
        self.horizontalLayout_4.addWidget(self.cmbOrganisation)
        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.lblOrgStructure = QtGui.QLabel(ExportFedRegPerPage1SetupDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.horizontalLayout_3.addWidget(self.lblOrgStructure)
        self.cmbOrgStructure = COrgStructureComboBox(ExportFedRegPerPage1SetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.horizontalLayout_3.addWidget(self.cmbOrgStructure)
        self.gridLayout.addLayout(self.horizontalLayout_3, 3, 1, 1, 1)

        self.retranslateUi(ExportFedRegPerPage1SetupDialog)
        QtCore.QMetaObject.connectSlotsByName(ExportFedRegPerPage1SetupDialog)
        ExportFedRegPerPage1SetupDialog.setTabOrder(self.btnExport, self.btnClose)

    def retranslateUi(self, ExportFedRegPerPage1SetupDialog):
        ExportFedRegPerPage1SetupDialog.setWindowTitle(_translate("ExportFedRegPerPage1SetupDialog", "Dialog", None))
        self.btnExport.setText(_translate("ExportFedRegPerPage1SetupDialog", "начать экспорт", None))
        self.btnClose.setText(_translate("ExportFedRegPerPage1SetupDialog", "прервать", None))
        self.lblOrganisation.setText(_translate("ExportFedRegPerPage1SetupDialog", "Организация", None))
        self.lblOrgStructure.setText(_translate("ExportFedRegPerPage1SetupDialog", "Подразделение", None))

from Orgs.OrgComboBox import COrgComboBox
from library.ProgressBar import CProgressBar
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
