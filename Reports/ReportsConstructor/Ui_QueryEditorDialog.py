# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QueryEditorDialog.ui'
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

class Ui_QueryDialog(object):
    def setupUi(self, QueryDialog):
        QueryDialog.setObjectName(_fromUtf8("QueryDialog"))
        QueryDialog.setEnabled(True)
        QueryDialog.resize(845, 571)
        self.gridLayout = QtGui.QGridLayout(QueryDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupGroups = QtGui.QGroupBox(QueryDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupGroups.sizePolicy().hasHeightForWidth())
        self.groupGroups.setSizePolicy(sizePolicy)
        self.groupGroups.setObjectName(_fromUtf8("groupGroups"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupGroups)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.tableGroups = CRCTableFieldsView(self.groupGroups)
        self.tableGroups.setObjectName(_fromUtf8("tableGroups"))
        self.gridLayout_4.addWidget(self.tableGroups, 1, 0, 1, 2)
        self.gridLayout.addWidget(self.groupGroups, 9, 0, 1, 1)
        self.groupOrders = QtGui.QGroupBox(QueryDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupOrders.sizePolicy().hasHeightForWidth())
        self.groupOrders.setSizePolicy(sizePolicy)
        self.groupOrders.setObjectName(_fromUtf8("groupOrders"))
        self.gridLayout_5 = QtGui.QGridLayout(self.groupOrders)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.tableOrders = CRCTableFieldsView(self.groupOrders)
        self.tableOrders.setObjectName(_fromUtf8("tableOrders"))
        self.gridLayout_5.addWidget(self.tableOrders, 1, 0, 1, 2)
        self.gridLayout.addWidget(self.groupOrders, 9, 1, 1, 1)
        self.groupConds = QtGui.QGroupBox(QueryDialog)
        self.groupConds.setObjectName(_fromUtf8("groupConds"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupConds)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.treeConds = CRCConditionsTreeView(self.groupConds)
        self.treeConds.setEnabled(True)
        self.treeConds.setObjectName(_fromUtf8("treeConds"))
        self.gridLayout_3.addWidget(self.treeConds, 0, 0, 1, 2)
        self.gridLayout.addWidget(self.groupConds, 8, 0, 1, 2)
        self.groupFields = QtGui.QGroupBox(QueryDialog)
        self.groupFields.setObjectName(_fromUtf8("groupFields"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupFields)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.tableFields = CRCTableFieldsView(self.groupFields)
        self.tableFields.setObjectName(_fromUtf8("tableFields"))
        self.gridLayout_2.addWidget(self.tableFields, 1, 0, 1, 2)
        self.gridLayout.addWidget(self.groupFields, 1, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblName = QtGui.QLabel(QueryDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.horizontalLayout.addWidget(self.lblName)
        self.edtName = QtGui.QLineEdit(QueryDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.horizontalLayout.addWidget(self.edtName)
        self.lblMainTable = QtGui.QLabel(QueryDialog)
        self.lblMainTable.setObjectName(_fromUtf8("lblMainTable"))
        self.horizontalLayout.addWidget(self.lblMainTable)
        self.cmbMainTable = CRCComboBox(QueryDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbMainTable.sizePolicy().hasHeightForWidth())
        self.cmbMainTable.setSizePolicy(sizePolicy)
        self.cmbMainTable.setObjectName(_fromUtf8("cmbMainTable"))
        self.horizontalLayout.addWidget(self.cmbMainTable)
        self.lblReference = QtGui.QLabel(QueryDialog)
        self.lblReference.setObjectName(_fromUtf8("lblReference"))
        self.horizontalLayout.addWidget(self.lblReference)
        self.cmbReference = CRCFieldsComboBox(QueryDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbReference.sizePolicy().hasHeightForWidth())
        self.cmbReference.setSizePolicy(sizePolicy)
        self.cmbReference.setObjectName(_fromUtf8("cmbReference"))
        self.horizontalLayout.addWidget(self.cmbReference)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(QueryDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 2)

        self.retranslateUi(QueryDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), QueryDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), QueryDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(QueryDialog)

    def retranslateUi(self, QueryDialog):
        QueryDialog.setWindowTitle(_translate("QueryDialog", "Dialog", None))
        self.groupGroups.setTitle(_translate("QueryDialog", "Поля Группировок", None))
        self.groupOrders.setTitle(_translate("QueryDialog", "Поля для сортировки", None))
        self.groupConds.setTitle(_translate("QueryDialog", "Условия", None))
        self.groupFields.setTitle(_translate("QueryDialog", "Поля таблицы", None))
        self.lblName.setText(_translate("QueryDialog", "Наименование", None))
        self.lblMainTable.setText(_translate("QueryDialog", "Главная таблица", None))
        self.lblReference.setText(_translate("QueryDialog", "Ссылка на поле", None))

from Reports.ReportsConstructor.RCComboBox import CRCComboBox, CRCFieldsComboBox
from Reports.ReportsConstructor.RCTableView import CRCTableFieldsView
from Reports.ReportsConstructor.RCTreeView import CRCConditionsTreeView
