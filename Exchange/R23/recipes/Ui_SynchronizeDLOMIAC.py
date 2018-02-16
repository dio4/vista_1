# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SynchronizeDLOMIAC.ui'
#
# Created: Tue Dec 29 05:40:45 2015
#      by: PyQt4 UI code generator 4.11.1
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

class Ui_SynchronizeDLOMIACDialog(object):
    def setupUi(self, SynchronizeDLOMIACDialog):
        SynchronizeDLOMIACDialog.setObjectName(_fromUtf8("SynchronizeDLOMIACDialog"))
        SynchronizeDLOMIACDialog.resize(1052, 425)
        self.gridLayout = QtGui.QGridLayout(SynchronizeDLOMIACDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btnDeselectAll = QtGui.QPushButton(SynchronizeDLOMIACDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDeselectAll.sizePolicy().hasHeightForWidth())
        self.btnDeselectAll.setSizePolicy(sizePolicy)
        self.btnDeselectAll.setObjectName(_fromUtf8("btnDeselectAll"))
        self.gridLayout.addWidget(self.btnDeselectAll, 1, 7, 1, 1)
        self.label = QtGui.QLabel(SynchronizeDLOMIACDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.edtBegDate = CDateEdit(SynchronizeDLOMIACDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegDate.sizePolicy().hasHeightForWidth())
        self.edtBegDate.setSizePolicy(sizePolicy)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 1, 1, 1, 2)
        self.label_2 = QtGui.QLabel(SynchronizeDLOMIACDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 3, 1, 1)
        self.edtEndDate = CDateEdit(SynchronizeDLOMIACDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndDate.sizePolicy().hasHeightForWidth())
        self.edtEndDate.setSizePolicy(sizePolicy)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 4, 1, 1)
        self.btnLoad = QtGui.QPushButton(SynchronizeDLOMIACDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnLoad.sizePolicy().hasHeightForWidth())
        self.btnLoad.setSizePolicy(sizePolicy)
        self.btnLoad.setObjectName(_fromUtf8("btnLoad"))
        self.gridLayout.addWidget(self.btnLoad, 1, 5, 1, 1)
        self.lblStatus = QtGui.QLabel(SynchronizeDLOMIACDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblStatus.sizePolicy().hasHeightForWidth())
        self.lblStatus.setSizePolicy(sizePolicy)
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.gridLayout.addWidget(self.lblStatus, 3, 0, 1, 2)
        self.btnSelectAll = QtGui.QPushButton(SynchronizeDLOMIACDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSelectAll.sizePolicy().hasHeightForWidth())
        self.btnSelectAll.setSizePolicy(sizePolicy)
        self.btnSelectAll.setObjectName(_fromUtf8("btnSelectAll"))
        self.gridLayout.addWidget(self.btnSelectAll, 1, 6, 1, 1)
        self.btnSync = QtGui.QPushButton(SynchronizeDLOMIACDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSync.sizePolicy().hasHeightForWidth())
        self.btnSync.setSizePolicy(sizePolicy)
        self.btnSync.setObjectName(_fromUtf8("btnSync"))
        self.gridLayout.addWidget(self.btnSync, 1, 8, 1, 1)
        self.tblDrugRecipe = CInDocTableView(SynchronizeDLOMIACDialog)
        self.tblDrugRecipe.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblDrugRecipe.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblDrugRecipe.setObjectName(_fromUtf8("tblDrugRecipe"))
        self.gridLayout.addWidget(self.tblDrugRecipe, 0, 0, 1, 9)
        self.btnClose = QtGui.QPushButton(SynchronizeDLOMIACDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnClose.sizePolicy().hasHeightForWidth())
        self.btnClose.setSizePolicy(sizePolicy)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 3, 8, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 7, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 3, 6, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 3, 5, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 3, 4, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 3, 2, 1, 1)

        self.retranslateUi(SynchronizeDLOMIACDialog)
        QtCore.QMetaObject.connectSlotsByName(SynchronizeDLOMIACDialog)
        SynchronizeDLOMIACDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        SynchronizeDLOMIACDialog.setTabOrder(self.edtEndDate, self.btnLoad)
        SynchronizeDLOMIACDialog.setTabOrder(self.btnLoad, self.btnSelectAll)
        SynchronizeDLOMIACDialog.setTabOrder(self.btnSelectAll, self.btnDeselectAll)
        SynchronizeDLOMIACDialog.setTabOrder(self.btnDeselectAll, self.btnSync)
        SynchronizeDLOMIACDialog.setTabOrder(self.btnSync, self.btnClose)
        SynchronizeDLOMIACDialog.setTabOrder(self.btnClose, self.tblDrugRecipe)

    def retranslateUi(self, SynchronizeDLOMIACDialog):
        SynchronizeDLOMIACDialog.setWindowTitle(_translate("SynchronizeDLOMIACDialog", "Dialog", None))
        self.btnDeselectAll.setText(_translate("SynchronizeDLOMIACDialog", "Снять выделение", None))
        self.label.setText(_translate("SynchronizeDLOMIACDialog", "Невыгруженные рецепты за период с", None))
        self.label_2.setText(_translate("SynchronizeDLOMIACDialog", "по", None))
        self.btnLoad.setText(_translate("SynchronizeDLOMIACDialog", "Загрузить", None))
        self.lblStatus.setText(_translate("SynchronizeDLOMIACDialog", "Записей в таблице выделено/всего: 0/0", None))
        self.btnSelectAll.setText(_translate("SynchronizeDLOMIACDialog", "Выделить всё", None))
        self.btnSync.setText(_translate("SynchronizeDLOMIACDialog", "Отослать выделенное", None))
        self.btnClose.setText(_translate("SynchronizeDLOMIACDialog", "Закрыть", None))

from library.DateEdit import CDateEdit
from library.InDocTable import CInDocTableView
