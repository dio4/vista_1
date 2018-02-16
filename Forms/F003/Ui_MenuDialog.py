# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MenuDialog.ui'
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

class Ui_MenuDialog(object):
    def setupUi(self, MenuDialog):
        MenuDialog.setObjectName(_fromUtf8("MenuDialog"))
        MenuDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        MenuDialog.resize(593, 450)
        MenuDialog.setSizeGripEnabled(True)
        MenuDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(MenuDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblPeriod = QtGui.QLabel(MenuDialog)
        self.lblPeriod.setObjectName(_fromUtf8("lblPeriod"))
        self.gridLayout.addWidget(self.lblPeriod, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(MenuDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.lblFor = QtGui.QLabel(MenuDialog)
        self.lblFor.setAlignment(QtCore.Qt.AlignCenter)
        self.lblFor.setObjectName(_fromUtf8("lblFor"))
        self.gridLayout.addWidget(self.lblFor, 0, 2, 1, 1)
        self.edtEndDate = CDateEdit(MenuDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 0, 3, 1, 1)
        self.chkUpdate = QtGui.QCheckBox(MenuDialog)
        self.chkUpdate.setObjectName(_fromUtf8("chkUpdate"))
        self.gridLayout.addWidget(self.chkUpdate, 0, 4, 1, 1)
        spacerItem = QtGui.QSpacerItem(287, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 5, 1, 1)
        self.tblItems = CTableView(MenuDialog)
        self.tblItems.setTabKeyNavigation(False)
        self.tblItems.setAlternatingRowColors(True)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 1, 0, 1, 6)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(MenuDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.btnSelected = QtGui.QPushButton(MenuDialog)
        self.btnSelected.setObjectName(_fromUtf8("btnSelected"))
        self.hboxlayout.addWidget(self.btnSelected)
        self.btnEdit = QtGui.QPushButton(MenuDialog)
        self.btnEdit.setDefault(True)
        self.btnEdit.setObjectName(_fromUtf8("btnEdit"))
        self.hboxlayout.addWidget(self.btnEdit)
        self.btnPrint = QtGui.QPushButton(MenuDialog)
        self.btnPrint.setObjectName(_fromUtf8("btnPrint"))
        self.hboxlayout.addWidget(self.btnPrint)
        self.btnCancel = QtGui.QPushButton(MenuDialog)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.hboxlayout.addWidget(self.btnCancel)
        self.gridLayout.addLayout(self.hboxlayout, 2, 0, 1, 6)
        self.statusBar = QtGui.QStatusBar(MenuDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusBar.sizePolicy().hasHeightForWidth())
        self.statusBar.setSizePolicy(sizePolicy)
        self.statusBar.setSizeGripEnabled(False)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        self.gridLayout.addWidget(self.statusBar, 3, 0, 1, 1)

        self.retranslateUi(MenuDialog)
        QtCore.QObject.connect(self.btnCancel, QtCore.SIGNAL(_fromUtf8("clicked()")), MenuDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(MenuDialog)
        MenuDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        MenuDialog.setTabOrder(self.edtEndDate, self.chkUpdate)
        MenuDialog.setTabOrder(self.chkUpdate, self.tblItems)
        MenuDialog.setTabOrder(self.tblItems, self.btnSelected)
        MenuDialog.setTabOrder(self.btnSelected, self.btnEdit)
        MenuDialog.setTabOrder(self.btnEdit, self.btnPrint)
        MenuDialog.setTabOrder(self.btnPrint, self.btnCancel)

    def retranslateUi(self, MenuDialog):
        MenuDialog.setWindowTitle(_translate("MenuDialog", "Список записей", None))
        self.lblPeriod.setText(_translate("MenuDialog", "Период с", None))
        self.edtBegDate.setDisplayFormat(_translate("MenuDialog", "dd.MM.yyyy", None))
        self.lblFor.setText(_translate("MenuDialog", "по", None))
        self.edtEndDate.setDisplayFormat(_translate("MenuDialog", "dd.MM.yyyy", None))
        self.chkUpdate.setText(_translate("MenuDialog", "Обновить", None))
        self.tblItems.setWhatsThis(_translate("MenuDialog", "список записей", "ура!"))
        self.label.setText(_translate("MenuDialog", "всего: ", None))
        self.btnSelected.setText(_translate("MenuDialog", "Выбрать", None))
        self.btnEdit.setWhatsThis(_translate("MenuDialog", "изменить текущую запись", None))
        self.btnEdit.setText(_translate("MenuDialog", "Просмотр", None))
        self.btnEdit.setShortcut(_translate("MenuDialog", "F4", None))
        self.btnPrint.setText(_translate("MenuDialog", "Печать", None))
        self.btnCancel.setWhatsThis(_translate("MenuDialog", "выйти из списка без выбора", None))
        self.btnCancel.setText(_translate("MenuDialog", "Закрыть", None))
        self.statusBar.setToolTip(_translate("MenuDialog", "A status bar", None))
        self.statusBar.setWhatsThis(_translate("MenuDialog", "A status bar.", None))

from library.DateEdit import CDateEdit
from library.TableView import CTableView
