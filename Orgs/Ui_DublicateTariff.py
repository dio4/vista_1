# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DublicateTariff.ui'
#
# Created: Wed Mar 25 16:15:15 2015
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

class Ui_DublicateTariff(object):
    def setupUi(self, DublicateTariff):
        DublicateTariff.setObjectName(_fromUtf8("DublicateTariff"))
        DublicateTariff.resize(748, 605)
        self.gridLayout = QtGui.QGridLayout(DublicateTariff)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(DublicateTariff)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout, 4, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(DublicateTariff)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 2, 1, 1)
        self.tblBaseTariff = CInDocTableView(DublicateTariff)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblBaseTariff.sizePolicy().hasHeightForWidth())
        self.tblBaseTariff.setSizePolicy(sizePolicy)
        self.tblBaseTariff.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblBaseTariff.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblBaseTariff.setObjectName(_fromUtf8("tblBaseTariff"))
        self.gridLayout.addWidget(self.tblBaseTariff, 1, 0, 2, 3)
        self.tblDuplicateTariff = CInDocTableView(DublicateTariff)
        self.tblDuplicateTariff.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblDuplicateTariff.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblDuplicateTariff.setObjectName(_fromUtf8("tblDuplicateTariff"))
        self.gridLayout.addWidget(self.tblDuplicateTariff, 3, 0, 1, 3)
        self.groupBox = QtGui.QGroupBox(DublicateTariff)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.chkEvent = QtGui.QCheckBox(self.groupBox)
        self.chkEvent.setChecked(True)
        self.chkEvent.setObjectName(_fromUtf8("chkEvent"))
        self.gridLayout_2.addWidget(self.chkEvent, 0, 0, 1, 1)
        self.chkTariffCategory = QtGui.QCheckBox(self.groupBox)
        self.chkTariffCategory.setObjectName(_fromUtf8("chkTariffCategory"))
        self.gridLayout_2.addWidget(self.chkTariffCategory, 0, 1, 1, 1)
        self.chkTariff = QtGui.QCheckBox(self.groupBox)
        self.chkTariff.setChecked(True)
        self.chkTariff.setObjectName(_fromUtf8("chkTariff"))
        self.gridLayout_2.addWidget(self.chkTariff, 1, 0, 1, 1)
        self.chkSpeciality = QtGui.QCheckBox(self.groupBox)
        self.chkSpeciality.setObjectName(_fromUtf8("chkSpeciality"))
        self.gridLayout_2.addWidget(self.chkSpeciality, 1, 1, 1, 1)
        self.chkBegDate = QtGui.QCheckBox(self.groupBox)
        self.chkBegDate.setChecked(True)
        self.chkBegDate.setObjectName(_fromUtf8("chkBegDate"))
        self.gridLayout_2.addWidget(self.chkBegDate, 2, 0, 1, 1)
        self.chkSex = QtGui.QCheckBox(self.groupBox)
        self.chkSex.setObjectName(_fromUtf8("chkSex"))
        self.gridLayout_2.addWidget(self.chkSex, 2, 1, 1, 1)
        self.chkEndDate = QtGui.QCheckBox(self.groupBox)
        self.chkEndDate.setChecked(True)
        self.chkEndDate.setObjectName(_fromUtf8("chkEndDate"))
        self.gridLayout_2.addWidget(self.chkEndDate, 3, 0, 1, 1)
        self.chkAge = QtGui.QCheckBox(self.groupBox)
        self.chkAge.setObjectName(_fromUtf8("chkAge"))
        self.gridLayout_2.addWidget(self.chkAge, 3, 1, 1, 1)
        self.chkAmount = QtGui.QCheckBox(self.groupBox)
        self.chkAmount.setChecked(True)
        self.chkAmount.setObjectName(_fromUtf8("chkAmount"))
        self.gridLayout_2.addWidget(self.chkAmount, 4, 0, 1, 1)
        self.chkAttachType = QtGui.QCheckBox(self.groupBox)
        self.chkAttachType.setObjectName(_fromUtf8("chkAttachType"))
        self.gridLayout_2.addWidget(self.chkAttachType, 4, 1, 1, 1)
        self.chkPrice = QtGui.QCheckBox(self.groupBox)
        self.chkPrice.setChecked(True)
        self.chkPrice.setObjectName(_fromUtf8("chkPrice"))
        self.gridLayout_2.addWidget(self.chkPrice, 5, 0, 1, 1)
        self.chkUnit = QtGui.QCheckBox(self.groupBox)
        self.chkUnit.setObjectName(_fromUtf8("chkUnit"))
        self.gridLayout_2.addWidget(self.chkUnit, 5, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 3)

        self.retranslateUi(DublicateTariff)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DublicateTariff.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DublicateTariff.reject)
        QtCore.QMetaObject.connectSlotsByName(DublicateTariff)

    def retranslateUi(self, DublicateTariff):
        DublicateTariff.setWindowTitle(_translate("DublicateTariff", "Проверка дубликатов тарифов", None))
        self.label.setText(_translate("DublicateTariff", "Найдено тарифов:", None))
        self.groupBox.setTitle(_translate("DublicateTariff", "Критерии поиска", None))
        self.chkEvent.setText(_translate("DublicateTariff", "Событие", None))
        self.chkTariffCategory.setText(_translate("DublicateTariff", "Тарифная категория", None))
        self.chkTariff.setText(_translate("DublicateTariff", "Тарифицируется", None))
        self.chkSpeciality.setText(_translate("DublicateTariff", "Специальность", None))
        self.chkBegDate.setText(_translate("DublicateTariff", "Дата начала", None))
        self.chkSex.setText(_translate("DublicateTariff", "Пол", None))
        self.chkEndDate.setText(_translate("DublicateTariff", "Дата конца", None))
        self.chkAge.setText(_translate("DublicateTariff", "Возраст", None))
        self.chkAmount.setText(_translate("DublicateTariff", "Количество", None))
        self.chkAttachType.setText(_translate("DublicateTariff", "Тип", None))
        self.chkPrice.setText(_translate("DublicateTariff", "Цена", None))
        self.chkUnit.setText(_translate("DublicateTariff", "Единица учета", None))

from library.InDocTable import CInDocTableView
