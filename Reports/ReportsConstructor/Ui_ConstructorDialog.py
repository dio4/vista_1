# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ConstructorDialog.ui'
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

class Ui_ConstructorDialog(object):
    def setupUi(self, ConstructorDialog):
        ConstructorDialog.setObjectName(_fromUtf8("ConstructorDialog"))
        ConstructorDialog.setEnabled(True)
        ConstructorDialog.resize(1105, 786)
        self.gridLayout = QtGui.QGridLayout(ConstructorDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtReportName = QtGui.QLineEdit(ConstructorDialog)
        self.edtReportName.setObjectName(_fromUtf8("edtReportName"))
        self.gridLayout.addWidget(self.edtReportName, 0, 0, 1, 1)
        self.btnCreateReport = QtGui.QPushButton(ConstructorDialog)
        self.btnCreateReport.setObjectName(_fromUtf8("btnCreateReport"))
        self.gridLayout.addWidget(self.btnCreateReport, 0, 1, 1, 1)
        self.tabWidget = QtGui.QTabWidget(ConstructorDialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_10 = QtGui.QGridLayout(self.tab)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.groupOrders = QtGui.QGroupBox(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupOrders.sizePolicy().hasHeightForWidth())
        self.groupOrders.setSizePolicy(sizePolicy)
        self.groupOrders.setObjectName(_fromUtf8("groupOrders"))
        self.gridLayout_9 = QtGui.QGridLayout(self.groupOrders)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.tableOrders = CRCTableFieldsView(self.groupOrders)
        self.tableOrders.setObjectName(_fromUtf8("tableOrders"))
        self.gridLayout_9.addWidget(self.tableOrders, 1, 0, 1, 2)
        self.gridLayout_10.addWidget(self.groupOrders, 3, 1, 1, 1)
        self.groupFields = QtGui.QGroupBox(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupFields.sizePolicy().hasHeightForWidth())
        self.groupFields.setSizePolicy(sizePolicy)
        self.groupFields.setObjectName(_fromUtf8("groupFields"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupFields)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.tableFields = CRCTableFieldsView(self.groupFields)
        self.tableFields.setObjectName(_fromUtf8("tableFields"))
        self.gridLayout_2.addWidget(self.tableFields, 1, 0, 1, 2)
        self.gridLayout_10.addWidget(self.groupFields, 1, 0, 2, 2)
        self.groupTabTable = QtGui.QGroupBox(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupTabTable.sizePolicy().hasHeightForWidth())
        self.groupTabTable.setSizePolicy(sizePolicy)
        self.groupTabTable.setObjectName(_fromUtf8("groupTabTable"))
        self.gridLayout_4 = QtGui.QGridLayout(self.groupTabTable)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.groupBoxCellFormat = QtGui.QGroupBox(self.groupTabTable)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxCellFormat.sizePolicy().hasHeightForWidth())
        self.groupBoxCellFormat.setSizePolicy(sizePolicy)
        self.groupBoxCellFormat.setObjectName(_fromUtf8("groupBoxCellFormat"))
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBoxCellFormat)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.lblAlignmentCapItem = QtGui.QLabel(self.groupBoxCellFormat)
        self.lblAlignmentCapItem.setObjectName(_fromUtf8("lblAlignmentCapItem"))
        self.gridLayout_5.addWidget(self.lblAlignmentCapItem, 0, 0, 1, 1)
        self.cmbAlignmentCapItem = QtGui.QComboBox(self.groupBoxCellFormat)
        self.cmbAlignmentCapItem.setObjectName(_fromUtf8("cmbAlignmentCapItem"))
        self.cmbAlignmentCapItem.addItem(_fromUtf8(""))
        self.cmbAlignmentCapItem.addItem(_fromUtf8(""))
        self.cmbAlignmentCapItem.addItem(_fromUtf8(""))
        self.gridLayout_5.addWidget(self.cmbAlignmentCapItem, 0, 1, 1, 1)
        self.chkBoldCapItem = QtGui.QCheckBox(self.groupBoxCellFormat)
        self.chkBoldCapItem.setObjectName(_fromUtf8("chkBoldCapItem"))
        self.gridLayout_5.addWidget(self.chkBoldCapItem, 1, 0, 1, 2)
        self.gridLayout_4.addWidget(self.groupBoxCellFormat, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem, 9, 2, 1, 1)
        self.btnFillTableCap = QtGui.QPushButton(self.groupTabTable)
        self.btnFillTableCap.setObjectName(_fromUtf8("btnFillTableCap"))
        self.gridLayout_4.addWidget(self.btnFillTableCap, 2, 2, 1, 1)
        self.btnClearTableCap = QtGui.QPushButton(self.groupTabTable)
        self.btnClearTableCap.setObjectName(_fromUtf8("btnClearTableCap"))
        self.gridLayout_4.addWidget(self.btnClearTableCap, 4, 2, 1, 1)
        self.gridLayout_6 = QtGui.QGridLayout()
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.spinBoxColumnCount = QtGui.QSpinBox(self.groupTabTable)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxColumnCount.sizePolicy().hasHeightForWidth())
        self.spinBoxColumnCount.setSizePolicy(sizePolicy)
        self.spinBoxColumnCount.setMinimum(2)
        self.spinBoxColumnCount.setObjectName(_fromUtf8("spinBoxColumnCount"))
        self.gridLayout_6.addWidget(self.spinBoxColumnCount, 2, 2, 1, 1)
        self.spinBoxRowCount = QtGui.QSpinBox(self.groupTabTable)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxRowCount.sizePolicy().hasHeightForWidth())
        self.spinBoxRowCount.setSizePolicy(sizePolicy)
        self.spinBoxRowCount.setMinimum(2)
        self.spinBoxRowCount.setSingleStep(1)
        self.spinBoxRowCount.setProperty("value", 2)
        self.spinBoxRowCount.setObjectName(_fromUtf8("spinBoxRowCount"))
        self.gridLayout_6.addWidget(self.spinBoxRowCount, 2, 0, 1, 1)
        self.label = QtGui.QLabel(self.groupTabTable)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_6.addWidget(self.label, 2, 1, 1, 1)
        self.btnCreateTableCap = QtGui.QPushButton(self.groupTabTable)
        self.btnCreateTableCap.setObjectName(_fromUtf8("btnCreateTableCap"))
        self.gridLayout_6.addWidget(self.btnCreateTableCap, 0, 0, 1, 3)
        self.gridLayout_4.addLayout(self.gridLayout_6, 3, 2, 1, 1)
        self.btnDeleteTableCap = QtGui.QPushButton(self.groupTabTable)
        self.btnDeleteTableCap.setObjectName(_fromUtf8("btnDeleteTableCap"))
        self.gridLayout_4.addWidget(self.btnDeleteTableCap, 5, 2, 1, 1)
        self.groupBoxGroup = QtGui.QGroupBox(self.groupTabTable)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxGroup.sizePolicy().hasHeightForWidth())
        self.groupBoxGroup.setSizePolicy(sizePolicy)
        self.groupBoxGroup.setObjectName(_fromUtf8("groupBoxGroup"))
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBoxGroup)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.cmbGroupField = CRCComboBox(self.groupBoxGroup)
        self.cmbGroupField.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbGroupField.sizePolicy().hasHeightForWidth())
        self.cmbGroupField.setSizePolicy(sizePolicy)
        self.cmbGroupField.setObjectName(_fromUtf8("cmbGroupField"))
        self.gridLayout_7.addWidget(self.cmbGroupField, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBoxGroup, 1, 2, 1, 1)
        self.tblCap = CRCTableCapView(self.groupTabTable)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblCap.sizePolicy().hasHeightForWidth())
        self.tblCap.setSizePolicy(sizePolicy)
        self.tblCap.setObjectName(_fromUtf8("tblCap"))
        self.gridLayout_4.addWidget(self.tblCap, 0, 0, 10, 1)
        self.gridLayout_10.addWidget(self.groupTabTable, 4, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblMainTable = QtGui.QLabel(self.tab)
        self.lblMainTable.setObjectName(_fromUtf8("lblMainTable"))
        self.horizontalLayout.addWidget(self.lblMainTable)
        self.cmbMainTable = CRCComboBox(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbMainTable.sizePolicy().hasHeightForWidth())
        self.cmbMainTable.setSizePolicy(sizePolicy)
        self.cmbMainTable.setObjectName(_fromUtf8("cmbMainTable"))
        self.horizontalLayout.addWidget(self.cmbMainTable)
        self.gridLayout_10.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.groupGroups = QtGui.QGroupBox(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupGroups.sizePolicy().hasHeightForWidth())
        self.groupGroups.setSizePolicy(sizePolicy)
        self.groupGroups.setObjectName(_fromUtf8("groupGroups"))
        self.gridLayout_8 = QtGui.QGridLayout(self.groupGroups)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.tableGroups = CRCTableFieldsView(self.groupGroups)
        self.tableGroups.setObjectName(_fromUtf8("tableGroups"))
        self.gridLayout_8.addWidget(self.tableGroups, 1, 0, 1, 2)
        self.gridLayout_10.addWidget(self.groupGroups, 3, 0, 1, 1)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.groupConds = QtGui.QGroupBox(self.tab_2)
        self.groupConds.setObjectName(_fromUtf8("groupConds"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupConds)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.treeConds = CRCConditionsTreeView(self.groupConds)
        self.treeConds.setEnabled(True)
        self.treeConds.setObjectName(_fromUtf8("treeConds"))
        self.gridLayout_3.addWidget(self.treeConds, 0, 0, 1, 2)
        self.verticalLayout_3.addWidget(self.groupConds)
        self.groupParams = QtGui.QGroupBox(self.tab_2)
        self.groupParams.setObjectName(_fromUtf8("groupParams"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupParams)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.tableParams = CRCTableParamsView(self.groupParams)
        self.tableParams.setObjectName(_fromUtf8("tableParams"))
        self.horizontalLayout_2.addWidget(self.tableParams)
        self.verticalLayout_3.addWidget(self.groupParams)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ConstructorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)

        self.retranslateUi(ConstructorDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ConstructorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ConstructorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConstructorDialog)

    def retranslateUi(self, ConstructorDialog):
        ConstructorDialog.setWindowTitle(_translate("ConstructorDialog", "Dialog", None))
        self.btnCreateReport.setText(_translate("ConstructorDialog", "Построить отчёт", None))
        self.groupOrders.setTitle(_translate("ConstructorDialog", "Сортировки", None))
        self.groupFields.setTitle(_translate("ConstructorDialog", "Поля таблицы", None))
        self.groupTabTable.setTitle(_translate("ConstructorDialog", "Шапка таблицы", None))
        self.groupBoxCellFormat.setTitle(_translate("ConstructorDialog", "Формат ячейки", None))
        self.lblAlignmentCapItem.setText(_translate("ConstructorDialog", "Выравнивание", None))
        self.cmbAlignmentCapItem.setItemText(0, _translate("ConstructorDialog", "Слева", None))
        self.cmbAlignmentCapItem.setItemText(1, _translate("ConstructorDialog", "По центру", None))
        self.cmbAlignmentCapItem.setItemText(2, _translate("ConstructorDialog", "Справа", None))
        self.chkBoldCapItem.setText(_translate("ConstructorDialog", "Жирный", None))
        self.btnFillTableCap.setText(_translate("ConstructorDialog", "Заполнить поля", None))
        self.btnClearTableCap.setText(_translate("ConstructorDialog", "Очистить таблицу", None))
        self.label.setText(_translate("ConstructorDialog", "x", None))
        self.btnCreateTableCap.setText(_translate("ConstructorDialog", "Создать таблицу", None))
        self.btnDeleteTableCap.setText(_translate("ConstructorDialog", "Удалить таблицу", None))
        self.groupBoxGroup.setTitle(_translate("ConstructorDialog", "Группировка", None))
        self.lblMainTable.setText(_translate("ConstructorDialog", "Главная таблица", None))
        self.groupGroups.setTitle(_translate("ConstructorDialog", "Группировки", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ConstructorDialog", "Настройки таблицы", None))
        self.groupConds.setTitle(_translate("ConstructorDialog", "Условия", None))
        self.groupParams.setTitle(_translate("ConstructorDialog", "Параметры", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("ConstructorDialog", "Условия и параметры", None))

from Reports.ReportsConstructor.RCComboBox import CRCComboBox
from Reports.ReportsConstructor.RCTableView import CRCTableCapView, CRCTableFieldsView, CRCTableParamsView
from Reports.ReportsConstructor.RCTreeView import CRCConditionsTreeView