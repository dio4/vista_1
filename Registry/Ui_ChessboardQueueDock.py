# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ChessboardQueueDock.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(399, 659)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.treeOrgStructure = CTreeView(self.splitter)
        self.treeOrgStructure.setObjectName(_fromUtf8("treeOrgStructure"))
        self.tblSpeciality = CRBListBox(self.splitter)
        self.tblSpeciality.setObjectName(_fromUtf8("tblSpeciality"))
        self.tblPersonnel = CRBListBox(self.splitter)
        self.tblPersonnel.setObjectName(_fromUtf8("tblPersonnel"))
        self.gridLayout.addWidget(self.splitter, 0, 1, 1, 9)
        self.edtEndDate = CDateEdit(Form)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 9, 1, 1)
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 6, 1, 1)
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 8, 1, 1)
        self.edtBegDate = CDateEdit(Form)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 7, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 5, 1, 1)
        self.tblChessboardAmbQueue = CTableView(Form)
        self.tblChessboardAmbQueue.setObjectName(_fromUtf8("tblChessboardAmbQueue"))
        self.gridLayout.addWidget(self.tblChessboardAmbQueue, 2, 1, 1, 9)
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 3, 1, 1)
        self.btnRefresh = QtGui.QToolButton(Form)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        font.setStrikeOut(True)
        self.btnRefresh.setFont(font)
        self.btnRefresh.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/new/prefix1/icons/refresh.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnRefresh.setIcon(icon)
        self.btnRefresh.setObjectName(_fromUtf8("btnRefresh"))
        self.gridLayout.addWidget(self.btnRefresh, 1, 2, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_3.setText(_translate("Form", "с", None))
        self.label_2.setText(_translate("Form", "по", None))
        self.label.setText(_translate("Form", "Дата ", None))
        self.btnRefresh.setToolTip(_translate("Form", "Обновить список номерков", None))

from library.DateEdit import CDateEdit
from library.RBListBox import CRBListBox
from library.TableView import CTableView
from library.TreeView import CTreeView
