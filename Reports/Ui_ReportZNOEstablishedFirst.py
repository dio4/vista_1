# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportZNOEstablishedFirst.ui'
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

class Ui_ReportZNOEstablishedFirst(object):
    def setupUi(self, ReportZNOEstablishedFirst):
        ReportZNOEstablishedFirst.setObjectName(_fromUtf8("ReportZNOEstablishedFirst"))
        ReportZNOEstablishedFirst.resize(967, 746)
        self.gridLayout = QtGui.QGridLayout(ReportZNOEstablishedFirst)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbEmployment = QtGui.QComboBox(ReportZNOEstablishedFirst)
        self.cmbEmployment.setEnabled(False)
        self.cmbEmployment.setObjectName(_fromUtf8("cmbEmployment"))
        self.cmbEmployment.addItem(_fromUtf8(""))
        self.cmbEmployment.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbEmployment, 7, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportZNOEstablishedFirst)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 19, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.gbZNO = QtGui.QGroupBox(ReportZNOEstablishedFirst)
        self.gbZNO.setObjectName(_fromUtf8("gbZNO"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gbZNO)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.cmbZNOFirst = QtGui.QComboBox(self.gbZNO)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbZNOFirst.sizePolicy().hasHeightForWidth())
        self.cmbZNOFirst.setSizePolicy(sizePolicy)
        self.cmbZNOFirst.setObjectName(_fromUtf8("cmbZNOFirst"))
        self.gridLayout_2.addWidget(self.cmbZNOFirst, 0, 1, 1, 1)
        self.cmbZNOMorph = QtGui.QComboBox(self.gbZNO)
        self.cmbZNOMorph.setObjectName(_fromUtf8("cmbZNOMorph"))
        self.gridLayout_2.addWidget(self.cmbZNOMorph, 1, 1, 1, 1)
        self.lblZNOFirst = QtGui.QLabel(self.gbZNO)
        self.lblZNOFirst.setObjectName(_fromUtf8("lblZNOFirst"))
        self.gridLayout_2.addWidget(self.lblZNOFirst, 0, 0, 1, 1)
        self.lblZNOMorph = QtGui.QLabel(self.gbZNO)
        self.lblZNOMorph.setObjectName(_fromUtf8("lblZNOMorph"))
        self.gridLayout_2.addWidget(self.lblZNOMorph, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.gbZNO, 2, 0, 1, 2)
        self.chkEmployment = QtGui.QCheckBox(ReportZNOEstablishedFirst)
        self.chkEmployment.setObjectName(_fromUtf8("chkEmployment"))
        self.gridLayout.addWidget(self.chkEmployment, 7, 0, 1, 1)
        self.chkSex = QtGui.QCheckBox(ReportZNOEstablishedFirst)
        self.chkSex.setObjectName(_fromUtf8("chkSex"))
        self.gridLayout.addWidget(self.chkSex, 6, 0, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportZNOEstablishedFirst)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridLayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.lstOrgStructure = CRBListBox(ReportZNOEstablishedFirst)
        self.lstOrgStructure.setObjectName(_fromUtf8("lstOrgStructure"))
        self.gridLayout.addWidget(self.lstOrgStructure, 13, 0, 1, 3)
        self.lstEventType = CRBListBox(ReportZNOEstablishedFirst)
        self.lstEventType.setObjectName(_fromUtf8("lstEventType"))
        self.gridLayout.addWidget(self.lstEventType, 10, 0, 1, 3)
        self.chkMKB = QtGui.QCheckBox(ReportZNOEstablishedFirst)
        self.chkMKB.setObjectName(_fromUtf8("chkMKB"))
        self.gridLayout.addWidget(self.chkMKB, 4, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportZNOEstablishedFirst)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridLayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.cmbEventType = CRBComboBox(ReportZNOEstablishedFirst)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 8, 1, 1, 2)
        self.edtBegDate = CDateEdit(ReportZNOEstablishedFirst)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.cmbDistrict = CRBComboBox(ReportZNOEstablishedFirst)
        self.cmbDistrict.setObjectName(_fromUtf8("cmbDistrict"))
        self.gridLayout.addWidget(self.cmbDistrict, 14, 1, 1, 2)
        self.chkOrgStructureMulti = QtGui.QCheckBox(ReportZNOEstablishedFirst)
        self.chkOrgStructureMulti.setObjectName(_fromUtf8("chkOrgStructureMulti"))
        self.gridLayout.addWidget(self.chkOrgStructureMulti, 11, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.edtMKBFrom = CICDCodeEdit(ReportZNOEstablishedFirst)
        self.edtMKBFrom.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMKBFrom.sizePolicy().hasHeightForWidth())
        self.edtMKBFrom.setSizePolicy(sizePolicy)
        self.edtMKBFrom.setMaximumSize(QtCore.QSize(40, 16777215))
        self.edtMKBFrom.setMaxLength(6)
        self.edtMKBFrom.setObjectName(_fromUtf8("edtMKBFrom"))
        self.horizontalLayout.addWidget(self.edtMKBFrom)
        self.edtMKBTo = CICDCodeEdit(ReportZNOEstablishedFirst)
        self.edtMKBTo.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMKBTo.sizePolicy().hasHeightForWidth())
        self.edtMKBTo.setSizePolicy(sizePolicy)
        self.edtMKBTo.setMaximumSize(QtCore.QSize(40, 16777215))
        self.edtMKBTo.setMaxLength(6)
        self.edtMKBTo.setObjectName(_fromUtf8("edtMKBTo"))
        self.horizontalLayout.addWidget(self.edtMKBTo)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.gridLayout.addLayout(self.horizontalLayout, 4, 1, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(ReportZNOEstablishedFirst)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 11, 1, 1, 2)
        self.cmbSex = QtGui.QComboBox(ReportZNOEstablishedFirst)
        self.cmbSex.setEnabled(False)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbSex, 6, 1, 1, 1)
        self.chkDistrictMulti = QtGui.QCheckBox(ReportZNOEstablishedFirst)
        self.chkDistrictMulti.setObjectName(_fromUtf8("chkDistrictMulti"))
        self.gridLayout.addWidget(self.chkDistrictMulti, 14, 0, 1, 1)
        self.chkEventTypeMulti = QtGui.QCheckBox(ReportZNOEstablishedFirst)
        self.chkEventTypeMulti.setObjectName(_fromUtf8("chkEventTypeMulti"))
        self.gridLayout.addWidget(self.chkEventTypeMulti, 8, 0, 1, 1)
        self.edtEndDate = CDateEdit(ReportZNOEstablishedFirst)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 1, 1, 1, 1)
        self.lstDistrict = CRBListBox(ReportZNOEstablishedFirst)
        self.lstDistrict.setObjectName(_fromUtf8("lstDistrict"))
        self.gridLayout.addWidget(self.lstDistrict, 15, 0, 1, 3)
        self.chkAge = QtGui.QCheckBox(ReportZNOEstablishedFirst)
        self.chkAge.setObjectName(_fromUtf8("chkAge"))
        self.gridLayout.addWidget(self.chkAge, 5, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.edtAgeFrom = QtGui.QSpinBox(ReportZNOEstablishedFirst)
        self.edtAgeFrom.setEnabled(False)
        self.edtAgeFrom.setMaximum(160)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self.horizontalLayout_2.addWidget(self.edtAgeFrom)
        self.edtAgeTo = QtGui.QSpinBox(ReportZNOEstablishedFirst)
        self.edtAgeTo.setEnabled(False)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setProperty("value", 150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self.horizontalLayout_2.addWidget(self.edtAgeTo)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.gridLayout.addLayout(self.horizontalLayout_2, 5, 1, 1, 2)
        self.chkGroupOrgStructure = QtGui.QCheckBox(ReportZNOEstablishedFirst)
        self.chkGroupOrgStructure.setObjectName(_fromUtf8("chkGroupOrgStructure"))
        self.gridLayout.addWidget(self.chkGroupOrgStructure, 12, 0, 1, 3)
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem4, 18, 0, 1, 1)
        self.cmbFinanceType = CRBComboBox(ReportZNOEstablishedFirst)
        self.cmbFinanceType.setObjectName(_fromUtf8("cmbFinanceType"))
        self.gridLayout.addWidget(self.cmbFinanceType, 16, 1, 1, 2)
        self.chkFinanceTypeMulti = QtGui.QCheckBox(ReportZNOEstablishedFirst)
        self.chkFinanceTypeMulti.setObjectName(_fromUtf8("chkFinanceTypeMulti"))
        self.gridLayout.addWidget(self.chkFinanceTypeMulti, 16, 0, 1, 1)
        self.lstFinanceType = CRBListBox(ReportZNOEstablishedFirst)
        self.lstFinanceType.setObjectName(_fromUtf8("lstFinanceType"))
        self.gridLayout.addWidget(self.lstFinanceType, 17, 0, 1, 3)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblBegDate.setBuddy(self.edtBegDate)

        self.retranslateUi(ReportZNOEstablishedFirst)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportZNOEstablishedFirst.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportZNOEstablishedFirst.reject)
        QtCore.QObject.connect(self.chkMKB, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtMKBTo.setEnabled)
        QtCore.QObject.connect(self.chkMKB, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtMKBFrom.setEnabled)
        QtCore.QObject.connect(self.chkSex, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbSex.setEnabled)
        QtCore.QObject.connect(self.chkAge, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtAgeTo.setEnabled)
        QtCore.QObject.connect(self.chkAge, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.edtAgeFrom.setEnabled)
        QtCore.QObject.connect(self.chkEmployment, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbEmployment.setEnabled)
        QtCore.QObject.connect(self.chkEventTypeMulti, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbEventType.setHidden)
        QtCore.QObject.connect(self.chkEventTypeMulti, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lstEventType.setVisible)
        QtCore.QObject.connect(self.chkOrgStructureMulti, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbOrgStructure.setHidden)
        QtCore.QObject.connect(self.chkOrgStructureMulti, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lstOrgStructure.setVisible)
        QtCore.QObject.connect(self.chkDistrictMulti, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbDistrict.setHidden)
        QtCore.QObject.connect(self.chkDistrictMulti, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lstDistrict.setVisible)
        QtCore.QObject.connect(self.chkFinanceTypeMulti, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.cmbFinanceType.setHidden)
        QtCore.QObject.connect(self.chkFinanceTypeMulti, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.lstFinanceType.setVisible)
        QtCore.QMetaObject.connectSlotsByName(ReportZNOEstablishedFirst)

    def retranslateUi(self, ReportZNOEstablishedFirst):
        ReportZNOEstablishedFirst.setWindowTitle(_translate("ReportZNOEstablishedFirst", "Dialog", None))
        self.cmbEmployment.setItemText(0, _translate("ReportZNOEstablishedFirst", "Да", None))
        self.cmbEmployment.setItemText(1, _translate("ReportZNOEstablishedFirst", "Нет", None))
        self.gbZNO.setTitle(_translate("ReportZNOEstablishedFirst", "ЗНО", None))
        self.lblZNOFirst.setText(_translate("ReportZNOEstablishedFirst", "ЗНО установлен впервые", None))
        self.lblZNOMorph.setText(_translate("ReportZNOEstablishedFirst", "ЗНО подтверждён морфологически", None))
        self.chkEmployment.setText(_translate("ReportZNOEstablishedFirst", "Трудоспособность", None))
        self.chkSex.setText(_translate("ReportZNOEstablishedFirst", "Пол", None))
        self.lblEndDate.setText(_translate("ReportZNOEstablishedFirst", "Дата &окончания периода", None))
        self.chkMKB.setText(_translate("ReportZNOEstablishedFirst", "Коды диагнозов по МКБ", None))
        self.lblBegDate.setText(_translate("ReportZNOEstablishedFirst", "Дата &начала периода", None))
        self.chkOrgStructureMulti.setText(_translate("ReportZNOEstablishedFirst", "Подразделение", None))
        self.edtMKBFrom.setInputMask(_translate("ReportZNOEstablishedFirst", "a00.00; ", None))
        self.edtMKBFrom.setText(_translate("ReportZNOEstablishedFirst", "A.", None))
        self.edtMKBTo.setInputMask(_translate("ReportZNOEstablishedFirst", "a00.00; ", None))
        self.edtMKBTo.setText(_translate("ReportZNOEstablishedFirst", "Z99.9", None))
        self.cmbSex.setItemText(0, _translate("ReportZNOEstablishedFirst", "Не указано", None))
        self.cmbSex.setItemText(1, _translate("ReportZNOEstablishedFirst", "М", None))
        self.cmbSex.setItemText(2, _translate("ReportZNOEstablishedFirst", "Ж", None))
        self.chkDistrictMulti.setText(_translate("ReportZNOEstablishedFirst", "Район", None))
        self.chkEventTypeMulti.setText(_translate("ReportZNOEstablishedFirst", "Тип обращения", None))
        self.chkAge.setText(_translate("ReportZNOEstablishedFirst", "Возраст", None))
        self.chkGroupOrgStructure.setText(_translate("ReportZNOEstablishedFirst", "Группировать по подразделениям", None))
        self.chkFinanceTypeMulti.setText(_translate("ReportZNOEstablishedFirst", "Тип финансирования", None))

from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from library.DateEdit import CDateEdit
from library.ICDCodeEdit import CICDCodeEdit
from library.RBListBox import CRBListBox
from library.crbcombobox import CRBComboBox
