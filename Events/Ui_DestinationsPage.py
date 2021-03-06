# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DestinationsPage.ui'
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

class Ui_DestinationsPageWidget(object):
    def setupUi(self, DestinationsPageWidget):
        DestinationsPageWidget.setObjectName(_fromUtf8("DestinationsPageWidget"))
        DestinationsPageWidget.resize(1334, 262)
        self.gridLayout = QtGui.QGridLayout(DestinationsPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.scrollArea = QtGui.QScrollArea(DestinationsPageWidget)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1322, 250))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        self.btnDestAdd = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btnDestAdd.setObjectName(_fromUtf8("btnDestAdd"))
        self.horizontalLayout_13.addWidget(self.btnDestAdd)
        self.btnDestAddToComplex = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btnDestAddToComplex.setObjectName(_fromUtf8("btnDestAddToComplex"))
        self.horizontalLayout_13.addWidget(self.btnDestAddToComplex)
        self.btnDestSet = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btnDestSet.setObjectName(_fromUtf8("btnDestSet"))
        self.horizontalLayout_13.addWidget(self.btnDestSet)
        self.btnDestSave = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btnDestSave.setObjectName(_fromUtf8("btnDestSave"))
        self.horizontalLayout_13.addWidget(self.btnDestSave)
        self.btnDestDelete = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btnDestDelete.setObjectName(_fromUtf8("btnDestDelete"))
        self.horizontalLayout_13.addWidget(self.btnDestDelete)
        self.btnDestCancel = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btnDestCancel.setObjectName(_fromUtf8("btnDestCancel"))
        self.horizontalLayout_13.addWidget(self.btnDestCancel)
        self.btnDestFind = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btnDestFind.setObjectName(_fromUtf8("btnDestFind"))
        self.horizontalLayout_13.addWidget(self.btnDestFind)
        self.btnDestPrint = CPrintButton(self.scrollAreaWidgetContents)
        self.btnDestPrint.setObjectName(_fromUtf8("btnDestPrint"))
        self.horizontalLayout_13.addWidget(self.btnDestPrint)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem)
        self.btnDestAll = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btnDestAll.setObjectName(_fromUtf8("btnDestAll"))
        self.horizontalLayout_13.addWidget(self.btnDestAll)
        self.gridLayout_2.addLayout(self.horizontalLayout_13, 0, 0, 1, 1)
        self.tblDestinations = CDestinationsTableView(self.scrollAreaWidgetContents)
        self.tblDestinations.setMinimumSize(QtCore.QSize(0, 200))
        self.tblDestinations.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed)
        self.tblDestinations.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblDestinations.setObjectName(_fromUtf8("tblDestinations"))
        self.gridLayout_2.addWidget(self.tblDestinations, 1, 0, 1, 1)
        self.grpDestFilter = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpDestFilter.sizePolicy().hasHeightForWidth())
        self.grpDestFilter.setSizePolicy(sizePolicy)
        self.grpDestFilter.setMaximumSize(QtCore.QSize(400, 16777215))
        self.grpDestFilter.setObjectName(_fromUtf8("grpDestFilter"))
        self.gridLayout_28 = QtGui.QGridLayout(self.grpDestFilter)
        self.gridLayout_28.setObjectName(_fromUtf8("gridLayout_28"))
        self.bbxDestFilter = CApplyResetDialogButtonBox(self.grpDestFilter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bbxDestFilter.sizePolicy().hasHeightForWidth())
        self.bbxDestFilter.setSizePolicy(sizePolicy)
        self.bbxDestFilter.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.bbxDestFilter.setObjectName(_fromUtf8("bbxDestFilter"))
        self.gridLayout_28.addWidget(self.bbxDestFilter, 9, 2, 1, 1)
        self.label_7 = QtGui.QLabel(self.grpDestFilter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_28.addWidget(self.label_7, 1, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.grpDestFilter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_28.addWidget(self.label_5, 0, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 316, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_28.addItem(spacerItem1, 8, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_28.addItem(spacerItem2, 9, 0, 1, 1)
        self.lblDestFilterStatus = QtGui.QLabel(self.grpDestFilter)
        self.lblDestFilterStatus.setObjectName(_fromUtf8("lblDestFilterStatus"))
        self.gridLayout_28.addWidget(self.lblDestFilterStatus, 6, 0, 1, 1)
        self.lblDestFilterDrug = QtGui.QLabel(self.grpDestFilter)
        self.lblDestFilterDrug.setObjectName(_fromUtf8("lblDestFilterDrug"))
        self.gridLayout_28.addWidget(self.lblDestFilterDrug, 5, 0, 1, 1)
        self.cmbDestFilterStatus = QtGui.QComboBox(self.grpDestFilter)
        self.cmbDestFilterStatus.setMinimumSize(QtCore.QSize(170, 0))
        self.cmbDestFilterStatus.setObjectName(_fromUtf8("cmbDestFilterStatus"))
        self.cmbDestFilterStatus.addItem(_fromUtf8(""))
        self.cmbDestFilterStatus.addItem(_fromUtf8(""))
        self.cmbDestFilterStatus.addItem(_fromUtf8(""))
        self.cmbDestFilterStatus.addItem(_fromUtf8(""))
        self.cmbDestFilterStatus.addItem(_fromUtf8(""))
        self.cmbDestFilterStatus.addItem(_fromUtf8(""))
        self.gridLayout_28.addWidget(self.cmbDestFilterStatus, 6, 2, 1, 2)
        self.edtDestFilterDrug = QtGui.QLineEdit(self.grpDestFilter)
        self.edtDestFilterDrug.setMinimumSize(QtCore.QSize(170, 0))
        self.edtDestFilterDrug.setObjectName(_fromUtf8("edtDestFilterDrug"))
        self.gridLayout_28.addWidget(self.edtDestFilterDrug, 5, 2, 1, 2)
        self.edtDestFilterEndDate = QtGui.QDateEdit(self.grpDestFilter)
        self.edtDestFilterEndDate.setMinimumSize(QtCore.QSize(170, 0))
        self.edtDestFilterEndDate.setCalendarPopup(True)
        self.edtDestFilterEndDate.setObjectName(_fromUtf8("edtDestFilterEndDate"))
        self.gridLayout_28.addWidget(self.edtDestFilterEndDate, 1, 2, 1, 2)
        self.edtDestFilterBegDate = QtGui.QDateEdit(self.grpDestFilter)
        self.edtDestFilterBegDate.setMinimumSize(QtCore.QSize(170, 0))
        self.edtDestFilterBegDate.setCalendarPopup(True)
        self.edtDestFilterBegDate.setObjectName(_fromUtf8("edtDestFilterBegDate"))
        self.gridLayout_28.addWidget(self.edtDestFilterBegDate, 0, 2, 1, 2)
        self.gridLayout_2.addWidget(self.grpDestFilter, 0, 1, 2, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(DestinationsPageWidget)
        QtCore.QMetaObject.connectSlotsByName(DestinationsPageWidget)

    def retranslateUi(self, DestinationsPageWidget):
        DestinationsPageWidget.setWindowTitle(_translate("DestinationsPageWidget", "Form", None))
        self.btnDestAdd.setText(_translate("DestinationsPageWidget", "Добавить..", None))
        self.btnDestAddToComplex.setText(_translate("DestinationsPageWidget", "Добавить в комплекс", None))
        self.btnDestSet.setText(_translate("DestinationsPageWidget", "Назначить", None))
        self.btnDestSave.setText(_translate("DestinationsPageWidget", "Сохранить", None))
        self.btnDestDelete.setText(_translate("DestinationsPageWidget", "Удалить", None))
        self.btnDestCancel.setText(_translate("DestinationsPageWidget", "Отменить", None))
        self.btnDestFind.setText(_translate("DestinationsPageWidget", "Найти", None))
        self.btnDestPrint.setText(_translate("DestinationsPageWidget", "Печать", None))
        self.btnDestAll.setText(_translate("DestinationsPageWidget", "Показать все назначения", None))
        self.grpDestFilter.setTitle(_translate("DestinationsPageWidget", "Фильтр", None))
        self.label_7.setText(_translate("DestinationsPageWidget", "по", None))
        self.label_5.setText(_translate("DestinationsPageWidget", "В период с", None))
        self.lblDestFilterStatus.setText(_translate("DestinationsPageWidget", "Статус", None))
        self.lblDestFilterDrug.setText(_translate("DestinationsPageWidget", "Препарат", None))
        self.cmbDestFilterStatus.setItemText(0, _translate("DestinationsPageWidget", "все", None))
        self.cmbDestFilterStatus.setItemText(1, _translate("DestinationsPageWidget", "новый", None))
        self.cmbDestFilterStatus.setItemText(2, _translate("DestinationsPageWidget", "создан", None))
        self.cmbDestFilterStatus.setItemText(3, _translate("DestinationsPageWidget", "назначен", None))
        self.cmbDestFilterStatus.setItemText(4, _translate("DestinationsPageWidget", "отменён", None))
        self.cmbDestFilterStatus.setItemText(5, _translate("DestinationsPageWidget", "выполнен", None))

from Events.DestinationsTable import CDestinationsTableView
from library.DialogButtonBox import CApplyResetDialogButtonBox
from library.PrintTemplates import CPrintButton
