# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AddDestinationDialog.ui'
#
# Created: Tue Dec 16 16:34:12 2014
#      by: PyQt4 UI code generator 4.11
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

class Ui_AddDestinationDialog(object):
    def setupUi(self, AddDestinationDialog):
        AddDestinationDialog.setObjectName(_fromUtf8("AddDestinationDialog"))
        AddDestinationDialog.resize(1075, 496)
        self.gridLayout = QtGui.QGridLayout(AddDestinationDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblSelectedDrugs = QtGui.QTableView(AddDestinationDialog)
        self.tblSelectedDrugs.setObjectName(_fromUtf8("tblSelectedDrugs"))
        self.tblSelectedDrugs.horizontalHeader().setVisible(False)
        self.tblSelectedDrugs.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tblSelectedDrugs, 4, 0, 1, 3)
        self.tblIssueForm = QtGui.QTableView(AddDestinationDialog)
        self.tblIssueForm.setObjectName(_fromUtf8("tblIssueForm"))
        self.tblIssueForm.horizontalHeader().setVisible(False)
        self.tblIssueForm.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tblIssueForm, 1, 1, 1, 1)
        self.tblMNN = QtGui.QTableView(AddDestinationDialog)
        self.tblMNN.setObjectName(_fromUtf8("tblMNN"))
        self.tblMNN.horizontalHeader().setVisible(False)
        self.tblMNN.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tblMNN, 1, 0, 1, 1)
        self.tblTradeName = QtGui.QTableView(AddDestinationDialog)
        self.tblTradeName.setObjectName(_fromUtf8("tblTradeName"))
        self.tblTradeName.horizontalHeader().setVisible(False)
        self.tblTradeName.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tblTradeName, 1, 2, 1, 1)
        self.edtMNN = QtGui.QLineEdit(AddDestinationDialog)
        self.edtMNN.setObjectName(_fromUtf8("edtMNN"))
        self.gridLayout.addWidget(self.edtMNN, 2, 0, 1, 1)
        self.edtIssueForm = QtGui.QLineEdit(AddDestinationDialog)
        self.edtIssueForm.setObjectName(_fromUtf8("edtIssueForm"))
        self.gridLayout.addWidget(self.edtIssueForm, 2, 1, 1, 1)
        self.edtTradeName = QtGui.QLineEdit(AddDestinationDialog)
        self.edtTradeName.setObjectName(_fromUtf8("edtTradeName"))
        self.gridLayout.addWidget(self.edtTradeName, 2, 2, 1, 1)
        self.chkCurrentFormulary = QtGui.QCheckBox(AddDestinationDialog)
        self.chkCurrentFormulary.setAcceptDrops(False)
        self.chkCurrentFormulary.setObjectName(_fromUtf8("chkCurrentFormulary"))
        self.gridLayout.addWidget(self.chkCurrentFormulary, 6, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(AddDestinationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnAdd = QtGui.QPushButton(AddDestinationDialog)
        self.btnAdd.setObjectName(_fromUtf8("btnAdd"))
        self.horizontalLayout.addWidget(self.btnAdd)
        self.btnDelete = QtGui.QPushButton(AddDestinationDialog)
        self.btnDelete.setObjectName(_fromUtf8("btnDelete"))
        self.horizontalLayout.addWidget(self.btnDelete)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 1, 1, 1)
        self.lblMnn = QtGui.QLabel(AddDestinationDialog)
        self.lblMnn.setObjectName(_fromUtf8("lblMnn"))
        self.gridLayout.addWidget(self.lblMnn, 0, 0, 1, 1)
        self.lblIssueForm = QtGui.QLabel(AddDestinationDialog)
        self.lblIssueForm.setObjectName(_fromUtf8("lblIssueForm"))
        self.gridLayout.addWidget(self.lblIssueForm, 0, 1, 1, 1)
        self.lblTradeName = QtGui.QLabel(AddDestinationDialog)
        self.lblTradeName.setObjectName(_fromUtf8("lblTradeName"))
        self.gridLayout.addWidget(self.lblTradeName, 0, 2, 1, 1)
        self.chkOrgStructureStock = QtGui.QCheckBox(AddDestinationDialog)
        self.chkOrgStructureStock.setObjectName(_fromUtf8("chkOrgStructureStock"))
        self.gridLayout.addWidget(self.chkOrgStructureStock, 7, 0, 1, 1)
        self.prbLoad = QtGui.QProgressBar(AddDestinationDialog)
        self.prbLoad.setProperty("value", 24)
        self.prbLoad.setObjectName(_fromUtf8("prbLoad"))
        self.gridLayout.addWidget(self.prbLoad, 3, 2, 1, 1)

        self.retranslateUi(AddDestinationDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AddDestinationDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AddDestinationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddDestinationDialog)

    def retranslateUi(self, AddDestinationDialog):
        AddDestinationDialog.setWindowTitle(_translate("AddDestinationDialog", "Добавить препарат", None))
        self.chkCurrentFormulary.setText(_translate("AddDestinationDialog", "Только текущий формуляр", None))
        self.btnAdd.setText(_translate("AddDestinationDialog", "Добавить", None))
        self.btnDelete.setText(_translate("AddDestinationDialog", "Удалить", None))
        self.lblMnn.setText(_translate("AddDestinationDialog", "Действующие вещества (МНН)", None))
        self.lblIssueForm.setText(_translate("AddDestinationDialog", "Формы выпуска", None))
        self.lblTradeName.setText(_translate("AddDestinationDialog", "Торговые наименования", None))
        self.chkOrgStructureStock.setText(_translate("AddDestinationDialog", "Только остатки в подразделениях", None))

