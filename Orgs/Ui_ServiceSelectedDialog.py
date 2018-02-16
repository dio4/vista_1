# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ServiceSelectedDialog.ui'
#
# Created: Fri Mar 20 16:24:24 2015
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_ServiceSelectedDialog(object):
    def setupUi(self, ServiceSelectedDialog):
        ServiceSelectedDialog.setObjectName(_fromUtf8("ServiceSelectedDialog"))
        ServiceSelectedDialog.resize(400, 304)
        self.gridLayout_3 = QtGui.QGridLayout(ServiceSelectedDialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblFindByCode = QtGui.QLabel(ServiceSelectedDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFindByCode.sizePolicy().hasHeightForWidth())
        self.lblFindByCode.setSizePolicy(sizePolicy)
        self.lblFindByCode.setObjectName(_fromUtf8("lblFindByCode"))
        self.horizontalLayout.addWidget(self.lblFindByCode)
        self.btnSearchMode = QtGui.QPushButton(ServiceSelectedDialog)
        self.btnSearchMode.setCheckable(True)
        self.btnSearchMode.setChecked(True)
        self.btnSearchMode.setObjectName(_fromUtf8("btnSearchMode"))
        self.horizontalLayout.addWidget(self.btnSearchMode)
        self.edtFindByCode = QtGui.QLineEdit(ServiceSelectedDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtFindByCode.sizePolicy().hasHeightForWidth())
        self.edtFindByCode.setSizePolicy(sizePolicy)
        self.edtFindByCode.setObjectName(_fromUtf8("edtFindByCode"))
        self.horizontalLayout.addWidget(self.edtFindByCode)
        self.gridLayout_3.addLayout(self.horizontalLayout, 2, 0, 1, 2)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ServiceSelectedDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(ServiceSelectedDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 4, 1, 1)
        self.edtBegDate = CDateEdit(ServiceSelectedDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 5, 1, 1)
        self.edtEndDate = CDateEdit(ServiceSelectedDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 5, 1, 1)
        self.chkNotEIS = QtGui.QCheckBox(ServiceSelectedDialog)
        self.chkNotEIS.setObjectName(_fromUtf8("chkNotEIS"))
        self.gridLayout.addWidget(self.chkNotEIS, 2, 0, 1, 3)
        self.label_2 = QtGui.QLabel(ServiceSelectedDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_4 = QtGui.QLabel(ServiceSelectedDialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 1, 4, 1, 1)
        self.cmbTariffType = QtGui.QComboBox(ServiceSelectedDialog)
        self.cmbTariffType.setObjectName(_fromUtf8("cmbTariffType"))
        self.gridLayout.addWidget(self.cmbTariffType, 1, 1, 1, 2)
        self.cmbEventType = CRBComboBox(ServiceSelectedDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 0, 1, 1, 2)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.splitter = QtGui.QSplitter(ServiceSelectedDialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tblSelectedService = CInDocTableView(self.splitter)
        self.tblSelectedService.setObjectName(_fromUtf8("tblSelectedService"))
        self.tblService = CTableView(self.splitter)
        self.tblService.setObjectName(_fromUtf8("tblService"))
        self.gridLayout_2.addWidget(self.splitter, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 2, 2)
        self.buttonBox = QtGui.QDialogButtonBox(ServiceSelectedDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 3, 0, 1, 1)

        self.retranslateUi(ServiceSelectedDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ServiceSelectedDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ServiceSelectedDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ServiceSelectedDialog)

    def retranslateUi(self, ServiceSelectedDialog):
        ServiceSelectedDialog.setWindowTitle(_translate("ServiceSelectedDialog", "Выберите услуги", None))
        self.lblFindByCode.setText(_translate("ServiceSelectedDialog", "| Поиск по", None))
        self.btnSearchMode.setText(_translate("ServiceSelectedDialog", "наименованию", None))
        self.label.setText(_translate("ServiceSelectedDialog", "Событие", None))
        self.label_3.setText(_translate("ServiceSelectedDialog", "Дата начала", None))
        self.chkNotEIS.setText(_translate("ServiceSelectedDialog", "Скрыть услуги из ЕИС", None))
        self.label_2.setText(_translate("ServiceSelectedDialog", "Тарифицируется", None))
        self.label_4.setText(_translate("ServiceSelectedDialog", "Дата окончания", None))

from library.InDocTable import CInDocTableView
from library.crbcombobox import CRBComboBox
from library.TableView import CTableView
from library.DateEdit import CDateEdit
