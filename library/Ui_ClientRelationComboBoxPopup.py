# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ClientRelationComboBoxPopup.ui'
#
# Created: Mon Sep 08 20:00:05 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_ClientRelationComboBoxPopup(object):
    def setupUi(self, ClientRelationComboBoxPopup):
        ClientRelationComboBoxPopup.setObjectName(_fromUtf8("ClientRelationComboBoxPopup"))
        ClientRelationComboBoxPopup.resize(508, 310)
        self.gridlayout = QtGui.QGridLayout(ClientRelationComboBoxPopup)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.tabWidget = QtGui.QTabWidget(ClientRelationComboBoxPopup)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabClientRelation = QtGui.QWidget()
        self.tabClientRelation.setObjectName(_fromUtf8("tabClientRelation"))
        self.vboxlayout = QtGui.QVBoxLayout(self.tabClientRelation)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setMargin(4)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.tblClientRelation = CTableView(self.tabClientRelation)
        self.tblClientRelation.setObjectName(_fromUtf8("tblClientRelation"))
        self.vboxlayout.addWidget(self.tblClientRelation)
        self.tabWidget.addTab(self.tabClientRelation, _fromUtf8(""))
        self.tabSearch = QtGui.QWidget()
        self.tabSearch.setObjectName(_fromUtf8("tabSearch"))
        self.gridlayout1 = QtGui.QGridLayout(self.tabSearch)
        self.gridlayout1.setMargin(4)
        self.gridlayout1.setSpacing(4)
        self.gridlayout1.setObjectName(_fromUtf8("gridlayout1"))
        self.edtNumber = QtGui.QLineEdit(self.tabSearch)
        self.edtNumber.setObjectName(_fromUtf8("edtNumber"))
        self.gridlayout1.addWidget(self.edtNumber, 7, 1, 1, 4)
        self.edtLastName = QtGui.QLineEdit(self.tabSearch)
        self.edtLastName.setObjectName(_fromUtf8("edtLastName"))
        self.gridlayout1.addWidget(self.edtLastName, 1, 1, 1, 4)
        self.edtWork = QtGui.QLineEdit(self.tabSearch)
        self.edtWork.setObjectName(_fromUtf8("edtWork"))
        self.gridlayout1.addWidget(self.edtWork, 9, 1, 1, 4)
        self.lblLastName = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblLastName.sizePolicy().hasHeightForWidth())
        self.lblLastName.setSizePolicy(sizePolicy)
        self.lblLastName.setObjectName(_fromUtf8("lblLastName"))
        self.gridlayout1.addWidget(self.lblLastName, 1, 0, 1, 1)
        self.lblFirstName = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFirstName.sizePolicy().hasHeightForWidth())
        self.lblFirstName.setSizePolicy(sizePolicy)
        self.lblFirstName.setObjectName(_fromUtf8("lblFirstName"))
        self.gridlayout1.addWidget(self.lblFirstName, 2, 0, 1, 1)
        self.lblBirthDate = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblBirthDate.sizePolicy().hasHeightForWidth())
        self.lblBirthDate.setSizePolicy(sizePolicy)
        self.lblBirthDate.setObjectName(_fromUtf8("lblBirthDate"))
        self.gridlayout1.addWidget(self.lblBirthDate, 4, 0, 1, 1)
        self.lblPatrName = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPatrName.sizePolicy().hasHeightForWidth())
        self.lblPatrName.setSizePolicy(sizePolicy)
        self.lblPatrName.setObjectName(_fromUtf8("lblPatrName"))
        self.gridlayout1.addWidget(self.lblPatrName, 3, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 141, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem, 11, 0, 1, 1)
        self.lblSerial = QtGui.QLabel(self.tabSearch)
        self.lblSerial.setObjectName(_fromUtf8("lblSerial"))
        self.gridlayout1.addWidget(self.lblSerial, 6, 0, 1, 1)
        self.edtPatrName = CPatrNameEditor(self.tabSearch)
        self.edtPatrName.setObjectName(_fromUtf8("edtPatrName"))
        self.gridlayout1.addWidget(self.edtPatrName, 3, 1, 1, 4)
        self.lblDocument = QtGui.QLabel(self.tabSearch)
        self.lblDocument.setObjectName(_fromUtf8("lblDocument"))
        self.gridlayout1.addWidget(self.lblDocument, 5, 0, 1, 1)
        self.cmbDocType = CRBComboBox(self.tabSearch)
        self.cmbDocType.setObjectName(_fromUtf8("cmbDocType"))
        self.gridlayout1.addWidget(self.cmbDocType, 5, 1, 1, 4)
        self.lblNumber = QtGui.QLabel(self.tabSearch)
        self.lblNumber.setObjectName(_fromUtf8("lblNumber"))
        self.gridlayout1.addWidget(self.lblNumber, 7, 0, 1, 1)
        self.edtLeftSerial = QtGui.QLineEdit(self.tabSearch)
        self.edtLeftSerial.setObjectName(_fromUtf8("edtLeftSerial"))
        self.gridlayout1.addWidget(self.edtLeftSerial, 6, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem1, 4, 4, 1, 1)
        self.edtRightSerial = QtGui.QLineEdit(self.tabSearch)
        self.edtRightSerial.setObjectName(_fromUtf8("edtRightSerial"))
        self.gridlayout1.addWidget(self.edtRightSerial, 6, 4, 1, 1)
        self.edtBirthDate = CDateEdit(self.tabSearch)
        self.edtBirthDate.setCalendarPopup(True)
        self.edtBirthDate.setObjectName(_fromUtf8("edtBirthDate"))
        self.gridlayout1.addWidget(self.edtBirthDate, 4, 1, 1, 1)
        self.btnFillingFilter = QtGui.QPushButton(self.tabSearch)
        self.btnFillingFilter.setObjectName(_fromUtf8("btnFillingFilter"))
        self.gridlayout1.addWidget(self.btnFillingFilter, 0, 0, 1, 5)
        self.btnRegistry = QtGui.QPushButton(self.tabSearch)
        self.btnRegistry.setObjectName(_fromUtf8("btnRegistry"))
        self.gridlayout1.addWidget(self.btnRegistry, 12, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem2, 12, 1, 1, 1)
        self.lblWork = QtGui.QLabel(self.tabSearch)
        self.lblWork.setObjectName(_fromUtf8("lblWork"))
        self.gridlayout1.addWidget(self.lblWork, 9, 0, 1, 1)
        self.btnCreateEntry = QtGui.QPushButton(self.tabSearch)
        self.btnCreateEntry.setObjectName(_fromUtf8("btnCreateEntry"))
        self.gridlayout1.addWidget(self.btnCreateEntry, 12, 4, 1, 1)
        self.lblSex = QtGui.QLabel(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblSex.sizePolicy().hasHeightForWidth())
        self.lblSex.setSizePolicy(sizePolicy)
        self.lblSex.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridlayout1.addWidget(self.lblSex, 4, 2, 1, 1)
        self.cmbSex = QtGui.QComboBox(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSex.sizePolicy().hasHeightForWidth())
        self.cmbSex.setSizePolicy(sizePolicy)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridlayout1.addWidget(self.cmbSex, 4, 3, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout1.addWidget(self.buttonBox, 12, 2, 1, 2)
        self.lblComment = QtGui.QLabel(self.tabSearch)
        self.lblComment.setObjectName(_fromUtf8("lblComment"))
        self.gridlayout1.addWidget(self.lblComment, 10, 0, 1, 1)
        self.edtComment = QtGui.QLineEdit(self.tabSearch)
        self.edtComment.setObjectName(_fromUtf8("edtComment"))
        self.gridlayout1.addWidget(self.edtComment, 10, 1, 1, 4)
        self.edtFirstName = CFirstNameEditor(self.tabSearch)
        self.edtFirstName.setObjectName(_fromUtf8("edtFirstName"))
        self.gridlayout1.addWidget(self.edtFirstName, 2, 1, 1, 4)
        self.tabWidget.addTab(self.tabSearch, _fromUtf8(""))
        self.gridlayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.lblLastName.setBuddy(self.edtLastName)
        self.lblFirstName.setBuddy(self.edtFirstName)

        self.retranslateUi(ClientRelationComboBoxPopup)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(ClientRelationComboBoxPopup)
        ClientRelationComboBoxPopup.setTabOrder(self.tabWidget, self.btnFillingFilter)
        ClientRelationComboBoxPopup.setTabOrder(self.btnFillingFilter, self.edtLastName)
        ClientRelationComboBoxPopup.setTabOrder(self.edtLastName, self.edtFirstName)
        ClientRelationComboBoxPopup.setTabOrder(self.edtFirstName, self.edtPatrName)
        ClientRelationComboBoxPopup.setTabOrder(self.edtPatrName, self.edtBirthDate)
        ClientRelationComboBoxPopup.setTabOrder(self.edtBirthDate, self.cmbDocType)
        ClientRelationComboBoxPopup.setTabOrder(self.cmbDocType, self.edtLeftSerial)
        ClientRelationComboBoxPopup.setTabOrder(self.edtLeftSerial, self.edtRightSerial)
        ClientRelationComboBoxPopup.setTabOrder(self.edtRightSerial, self.edtNumber)
        ClientRelationComboBoxPopup.setTabOrder(self.edtNumber, self.tblClientRelation)

    def retranslateUi(self, ClientRelationComboBoxPopup):
        ClientRelationComboBoxPopup.setWindowTitle(_translate("ClientRelationComboBoxPopup", "Form", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabClientRelation), _translate("ClientRelationComboBoxPopup", "Результат поиска", None))
        self.lblLastName.setText(_translate("ClientRelationComboBoxPopup", "Фамилия", None))
        self.lblFirstName.setText(_translate("ClientRelationComboBoxPopup", "Имя", None))
        self.lblBirthDate.setText(_translate("ClientRelationComboBoxPopup", "Дата рождения", None))
        self.lblPatrName.setText(_translate("ClientRelationComboBoxPopup", "Отчество", None))
        self.lblSerial.setText(_translate("ClientRelationComboBoxPopup", "Серия", None))
        self.lblDocument.setText(_translate("ClientRelationComboBoxPopup", "Документ", None))
        self.lblNumber.setText(_translate("ClientRelationComboBoxPopup", "Номер", None))
        self.edtBirthDate.setDisplayFormat(_translate("ClientRelationComboBoxPopup", "dd.MM.yyyy", None))
        self.btnFillingFilter.setText(_translate("ClientRelationComboBoxPopup", "Автозаполнение данных", None))
        self.btnRegistry.setText(_translate("ClientRelationComboBoxPopup", "Регистрация", None))
        self.lblWork.setText(_translate("ClientRelationComboBoxPopup", "Занятость", None))
        self.btnCreateEntry.setText(_translate("ClientRelationComboBoxPopup", "Создать запись", None))
        self.lblSex.setText(_translate("ClientRelationComboBoxPopup", "Пол", None))
        self.cmbSex.setItemText(1, _translate("ClientRelationComboBoxPopup", "Мужской", None))
        self.cmbSex.setItemText(2, _translate("ClientRelationComboBoxPopup", "Женский", None))
        self.lblComment.setText(_translate("ClientRelationComboBoxPopup", "Прочее", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSearch), _translate("ClientRelationComboBoxPopup", "&Поиск", None))

from Registry.NamesEditor import CPatrNameEditor, CFirstNameEditor
from library.crbcombobox import CRBComboBox
from library.TableView import CTableView
from library.DateEdit import CDateEdit
