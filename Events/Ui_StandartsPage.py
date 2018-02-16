# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StandartsPage.ui'
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

class Ui_QStandartPageWidget(object):
    def setupUi(self, QStandartPageWidget):
        QStandartPageWidget.setObjectName(_fromUtf8("QStandartPageWidget"))
        QStandartPageWidget.resize(1510, 582)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(QStandartPageWidget.sizePolicy().hasHeightForWidth())
        QStandartPageWidget.setSizePolicy(sizePolicy)
        self.gridLayout_4 = QtGui.QGridLayout(QStandartPageWidget)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.scrollArea = QtGui.QScrollArea(QStandartPageWidget)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1492, 564))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setMinimumSize(QtCore.QSize(0, 400))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.groupBox_2 = QtGui.QGroupBox(self.splitter)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(197, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 3, 1, 2)
        self.edtServiceFilter = QtGui.QLineEdit(self.groupBox_2)
        self.edtServiceFilter.setObjectName(_fromUtf8("edtServiceFilter"))
        self.gridLayout.addWidget(self.edtServiceFilter, 2, 2, 1, 1)
        self.lblFilter = QtGui.QLabel(self.groupBox_2)
        self.lblFilter.setObjectName(_fromUtf8("lblFilter"))
        self.gridLayout.addWidget(self.lblFilter, 2, 0, 1, 2)
        self.treeStandartList = QtGui.QTreeWidget(self.groupBox_2)
        self.treeStandartList.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.treeStandartList.setLineWidth(1)
        self.treeStandartList.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed|QtGui.QAbstractItemView.SelectedClicked)
        self.treeStandartList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.treeStandartList.setObjectName(_fromUtf8("treeStandartList"))
        self.treeStandartList.header().setCascadingSectionResizes(False)
        self.treeStandartList.header().setHighlightSections(False)
        self.treeStandartList.header().setMinimumSectionSize(27)
        self.gridLayout.addWidget(self.treeStandartList, 1, 0, 1, 5)
        self.lblMES = QtGui.QLabel(self.groupBox_2)
        self.lblMES.setObjectName(_fromUtf8("lblMES"))
        self.gridLayout.addWidget(self.lblMES, 0, 0, 1, 1)
        self.cmbMes = CMESComboBox(self.groupBox_2)
        self.cmbMes.setMinimumSize(QtCore.QSize(300, 0))
        self.cmbMes.setBaseSize(QtCore.QSize(0, 0))
        self.cmbMes.setObjectName(_fromUtf8("cmbMes"))
        self.gridLayout.addWidget(self.cmbMes, 0, 1, 1, 3)
        self.btnAdd = QtGui.QPushButton(self.groupBox_2)
        self.btnAdd.setObjectName(_fromUtf8("btnAdd"))
        self.gridLayout.addWidget(self.btnAdd, 0, 4, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(self.splitter)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tblStandart = QtGui.QTableView(self.groupBox_3)
        self.tblStandart.setObjectName(_fromUtf8("tblStandart"))
        self.gridLayout_3.addWidget(self.tblStandart, 1, 0, 1, 1)
        self.label = QtGui.QLabel(self.groupBox_3)
        self.label.setMinimumSize(QtCore.QSize(0, 23))
        self.label.setText(_fromUtf8(""))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblPerson = QtGui.QLabel(self.groupBox)
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.gridLayout_2.addWidget(self.lblPerson, 0, 2, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(self.groupBox)
        self.cmbPerson.setMinimumSize(QtCore.QSize(150, 0))
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout_2.addWidget(self.cmbPerson, 0, 3, 1, 1)
        self.lblSetDate = QtGui.QLabel(self.groupBox)
        self.lblSetDate.setObjectName(_fromUtf8("lblSetDate"))
        self.gridLayout_2.addWidget(self.lblSetDate, 0, 4, 1, 1)
        self.edtSetDate = CDateEdit(self.groupBox)
        self.edtSetDate.setObjectName(_fromUtf8("edtSetDate"))
        self.gridLayout_2.addWidget(self.edtSetDate, 0, 5, 1, 1)
        self.lblExecDate = QtGui.QLabel(self.groupBox)
        self.lblExecDate.setObjectName(_fromUtf8("lblExecDate"))
        self.gridLayout_2.addWidget(self.lblExecDate, 0, 6, 1, 1)
        self.edtExecDate = CDateEdit(self.groupBox)
        self.edtExecDate.setObjectName(_fromUtf8("edtExecDate"))
        self.gridLayout_2.addWidget(self.edtExecDate, 0, 7, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(180, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 0, 1, 1, 1)
        self.tblAPProps = CExActionPropertiesTableView(self.groupBox)
        self.tblAPProps.setObjectName(_fromUtf8("tblAPProps"))
        self.gridLayout_2.addWidget(self.tblAPProps, 1, 1, 1, 7)
        spacerItem2 = QtGui.QSpacerItem(338, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 2, 7, 1, 1)
        self.btnLoadTemplate = CActionTemplateChooseButton(self.groupBox)
        self.btnLoadTemplate.setObjectName(_fromUtf8("btnLoadTemplate"))
        self.gridLayout_2.addWidget(self.btnLoadTemplate, 2, 3, 1, 1)
        self.btnAPPrint = CPrintButton(self.groupBox)
        self.btnAPPrint.setObjectName(_fromUtf8("btnAPPrint"))
        self.gridLayout_2.addWidget(self.btnAPPrint, 2, 2, 1, 1)
        self.verticalLayout.addWidget(self.splitter)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_4.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(QStandartPageWidget)
        QtCore.QMetaObject.connectSlotsByName(QStandartPageWidget)

    def retranslateUi(self, QStandartPageWidget):
        QStandartPageWidget.setWindowTitle(_translate("QStandartPageWidget", "Form", None))
        self.groupBox_2.setTitle(_translate("QStandartPageWidget", "Стандарты", None))
        self.lblFilter.setText(_translate("QStandartPageWidget", "Поиск:", None))
        self.treeStandartList.headerItem().setText(0, _translate("QStandartPageWidget", "Название", None))
        self.treeStandartList.headerItem().setText(1, _translate("QStandartPageWidget", "Назначено", None))
        self.treeStandartList.headerItem().setText(2, _translate("QStandartPageWidget", "Выполнено", None))
        self.treeStandartList.headerItem().setText(3, _translate("QStandartPageWidget", "%", None))
        self.lblMES.setText(_translate("QStandartPageWidget", "МЭС:", None))
        self.btnAdd.setText(_translate("QStandartPageWidget", "Добавить", None))
        self.groupBox_3.setTitle(_translate("QStandartPageWidget", "Услуги по показаниям", None))
        self.groupBox.setTitle(_translate("QStandartPageWidget", "Описание услуги:", None))
        self.lblPerson.setText(_translate("QStandartPageWidget", "Исполнитель:", None))
        self.lblSetDate.setText(_translate("QStandartPageWidget", "Дата назначения:", None))
        self.lblExecDate.setText(_translate("QStandartPageWidget", "Дата выполнения:", None))
        self.btnLoadTemplate.setText(_translate("QStandartPageWidget", "Загрузить шаблон", None))
        self.btnAPPrint.setText(_translate("QStandartPageWidget", "Печать", None))

from Events.ActionPropertiesTable import CExActionPropertiesTableView
from Events.ActionTemplateChoose import CActionTemplateChooseButton
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from library.MES.MESComboBox import CMESComboBox
from library.PrintTemplates import CPrintButton
