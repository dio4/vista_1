# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReportDD2013WeeklySetup.ui'
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

class Ui_ReportDD2013WeeklySetupDialog(object):
    def setupUi(self, ReportDD2013WeeklySetupDialog):
        ReportDD2013WeeklySetupDialog.setObjectName(_fromUtf8("ReportDD2013WeeklySetupDialog"))
        ReportDD2013WeeklySetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ReportDD2013WeeklySetupDialog.resize(532, 304)
        ReportDD2013WeeklySetupDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ReportDD2013WeeklySetupDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblSex = QtGui.QLabel(ReportDD2013WeeklySetupDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridlayout.addWidget(self.lblSex, 4, 0, 1, 1)
        self.frmAge = QtGui.QFrame(ReportDD2013WeeklySetupDialog)
        self.frmAge.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAge.setFrameShadow(QtGui.QFrame.Raised)
        self.frmAge.setObjectName(_fromUtf8("frmAge"))
        self._2 = QtGui.QHBoxLayout(self.frmAge)
        self._2.setMargin(0)
        self._2.setSpacing(4)
        self._2.setObjectName(_fromUtf8("_2"))
        self.edtAgeFrom = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeFrom.sizePolicy().hasHeightForWidth())
        self.edtAgeFrom.setSizePolicy(sizePolicy)
        self.edtAgeFrom.setMaximum(150)
        self.edtAgeFrom.setObjectName(_fromUtf8("edtAgeFrom"))
        self._2.addWidget(self.edtAgeFrom)
        self.lblAgeTo = QtGui.QLabel(self.frmAge)
        self.lblAgeTo.setObjectName(_fromUtf8("lblAgeTo"))
        self._2.addWidget(self.lblAgeTo)
        self.edtAgeTo = QtGui.QSpinBox(self.frmAge)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAgeTo.sizePolicy().hasHeightForWidth())
        self.edtAgeTo.setSizePolicy(sizePolicy)
        self.edtAgeTo.setMaximum(150)
        self.edtAgeTo.setObjectName(_fromUtf8("edtAgeTo"))
        self._2.addWidget(self.edtAgeTo)
        self.lblAgeYears = QtGui.QLabel(self.frmAge)
        self.lblAgeYears.setObjectName(_fromUtf8("lblAgeYears"))
        self._2.addWidget(self.lblAgeYears)
        spacerItem = QtGui.QSpacerItem(21, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self._2.addItem(spacerItem)
        self.gridlayout.addWidget(self.frmAge, 6, 2, 1, 2)
        self.lblTerType = QtGui.QLabel(ReportDD2013WeeklySetupDialog)
        self.lblTerType.setObjectName(_fromUtf8("lblTerType"))
        self.gridlayout.addWidget(self.lblTerType, 10, 0, 1, 1)
        self.lblEventType = QtGui.QLabel(ReportDD2013WeeklySetupDialog)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridlayout.addWidget(self.lblEventType, 7, 0, 1, 1)
        self.cmbEventType = CRBComboBox(ReportDD2013WeeklySetupDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridlayout.addWidget(self.cmbEventType, 7, 2, 1, 1)
        self.lblPayStatus = QtGui.QLabel(ReportDD2013WeeklySetupDialog)
        self.lblPayStatus.setObjectName(_fromUtf8("lblPayStatus"))
        self.gridlayout.addWidget(self.lblPayStatus, 14, 0, 1, 1)
        self.cmbSex = QtGui.QComboBox(ReportDD2013WeeklySetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSex.sizePolicy().hasHeightForWidth())
        self.cmbSex.setSizePolicy(sizePolicy)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbSex, 4, 2, 1, 1)
        self.lblAge = QtGui.QLabel(ReportDD2013WeeklySetupDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridlayout.addWidget(self.lblAge, 6, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 0, 3, 1, 1)
        self.edtBegDate = CDateEdit(ReportDD2013WeeklySetupDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridlayout.addWidget(self.edtBegDate, 0, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem2, 18, 0, 1, 1)
        self.lblBegDate = QtGui.QLabel(ReportDD2013WeeklySetupDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.gridlayout.addWidget(self.lblBegDate, 0, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(91, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem3, 1, 3, 1, 1)
        self.cmbSource = QtGui.QComboBox(ReportDD2013WeeklySetupDialog)
        self.cmbSource.setObjectName(_fromUtf8("cmbSource"))
        self.cmbSource.addItem(_fromUtf8(""))
        self.cmbSource.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbSource, 11, 2, 1, 1)
        self.chkCountUnfinished = QtGui.QCheckBox(ReportDD2013WeeklySetupDialog)
        self.chkCountUnfinished.setObjectName(_fromUtf8("chkCountUnfinished"))
        self.gridlayout.addWidget(self.chkCountUnfinished, 15, 2, 1, 1)
        self.lblEndDate = QtGui.QLabel(ReportDD2013WeeklySetupDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.gridlayout.addWidget(self.lblEndDate, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ReportDD2013WeeklySetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 19, 0, 1, 4)
        self.grbPopulation = QtGui.QGroupBox(ReportDD2013WeeklySetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grbPopulation.sizePolicy().hasHeightForWidth())
        self.grbPopulation.setSizePolicy(sizePolicy)
        self.grbPopulation.setMinimumSize(QtCore.QSize(0, 100))
        self.grbPopulation.setCheckable(True)
        self.grbPopulation.setChecked(False)
        self.grbPopulation.setObjectName(_fromUtf8("grbPopulation"))
        self.gridLayoutWidget = QtGui.QWidget(self.grbPopulation)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 340, 93))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblWomen = QtGui.QLabel(self.gridLayoutWidget)
        self.lblWomen.setObjectName(_fromUtf8("lblWomen"))
        self.gridLayout_2.addWidget(self.lblWomen, 0, 3, 1, 1)
        self.lblWomenPlan = QtGui.QLabel(self.gridLayoutWidget)
        self.lblWomenPlan.setObjectName(_fromUtf8("lblWomenPlan"))
        self.gridLayout_2.addWidget(self.lblWomenPlan, 0, 4, 1, 1)
        self.lblYoung = QtGui.QLabel(self.gridLayoutWidget)
        self.lblYoung.setObjectName(_fromUtf8("lblYoung"))
        self.gridLayout_2.addWidget(self.lblYoung, 1, 0, 1, 1)
        self.lblMenPlan = QtGui.QLabel(self.gridLayoutWidget)
        self.lblMenPlan.setObjectName(_fromUtf8("lblMenPlan"))
        self.gridLayout_2.addWidget(self.lblMenPlan, 0, 2, 1, 1)
        self.lblMiddle = QtGui.QLabel(self.gridLayoutWidget)
        self.lblMiddle.setObjectName(_fromUtf8("lblMiddle"))
        self.gridLayout_2.addWidget(self.lblMiddle, 2, 0, 1, 1)
        self.lblOld = QtGui.QLabel(self.gridLayoutWidget)
        self.lblOld.setObjectName(_fromUtf8("lblOld"))
        self.gridLayout_2.addWidget(self.lblOld, 3, 0, 1, 1)
        self.lblMen = QtGui.QLabel(self.gridLayoutWidget)
        self.lblMen.setObjectName(_fromUtf8("lblMen"))
        self.gridLayout_2.addWidget(self.lblMen, 0, 1, 1, 1)
        self.edtYoungMen = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtYoungMen.setObjectName(_fromUtf8("edtYoungMen"))
        self.gridLayout_2.addWidget(self.edtYoungMen, 1, 1, 1, 1)
        self.edtMiddleMen = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtMiddleMen.setObjectName(_fromUtf8("edtMiddleMen"))
        self.gridLayout_2.addWidget(self.edtMiddleMen, 2, 1, 1, 1)
        self.edtOldMen = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtOldMen.setObjectName(_fromUtf8("edtOldMen"))
        self.gridLayout_2.addWidget(self.edtOldMen, 3, 1, 1, 1)
        self.edtYoungMenPlan = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtYoungMenPlan.setObjectName(_fromUtf8("edtYoungMenPlan"))
        self.gridLayout_2.addWidget(self.edtYoungMenPlan, 1, 2, 1, 1)
        self.edtMiddleMenPlan = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtMiddleMenPlan.setObjectName(_fromUtf8("edtMiddleMenPlan"))
        self.gridLayout_2.addWidget(self.edtMiddleMenPlan, 2, 2, 1, 1)
        self.edtOldMenPlan = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtOldMenPlan.setObjectName(_fromUtf8("edtOldMenPlan"))
        self.gridLayout_2.addWidget(self.edtOldMenPlan, 3, 2, 1, 1)
        self.edtYoungWomen = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtYoungWomen.setObjectName(_fromUtf8("edtYoungWomen"))
        self.gridLayout_2.addWidget(self.edtYoungWomen, 1, 3, 1, 1)
        self.edtMiddleWomen = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtMiddleWomen.setObjectName(_fromUtf8("edtMiddleWomen"))
        self.gridLayout_2.addWidget(self.edtMiddleWomen, 2, 3, 1, 1)
        self.edtOldWomen = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtOldWomen.setObjectName(_fromUtf8("edtOldWomen"))
        self.gridLayout_2.addWidget(self.edtOldWomen, 3, 3, 1, 1)
        self.edtYoungWomenPlan = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtYoungWomenPlan.setObjectName(_fromUtf8("edtYoungWomenPlan"))
        self.gridLayout_2.addWidget(self.edtYoungWomenPlan, 1, 4, 1, 1)
        self.edtMiddleWomenPlan = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtMiddleWomenPlan.setObjectName(_fromUtf8("edtMiddleWomenPlan"))
        self.gridLayout_2.addWidget(self.edtMiddleWomenPlan, 2, 4, 1, 1)
        self.edtOldWomenPlan = QtGui.QLineEdit(self.gridLayoutWidget)
        self.edtOldWomenPlan.setObjectName(_fromUtf8("edtOldWomenPlan"))
        self.gridLayout_2.addWidget(self.edtOldWomenPlan, 3, 4, 1, 1)
        self.gridlayout.addWidget(self.grbPopulation, 13, 0, 1, 3)
        self.cmbTerType = QtGui.QComboBox(ReportDD2013WeeklySetupDialog)
        self.cmbTerType.setObjectName(_fromUtf8("cmbTerType"))
        self.cmbTerType.addItem(_fromUtf8(""))
        self.cmbTerType.addItem(_fromUtf8(""))
        self.cmbTerType.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbTerType, 10, 2, 1, 1)
        self.edtEndDate = CDateEdit(ReportDD2013WeeklySetupDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridlayout.addWidget(self.edtEndDate, 1, 2, 1, 1)
        self.cmbPayStatus = QtGui.QComboBox(ReportDD2013WeeklySetupDialog)
        self.cmbPayStatus.setObjectName(_fromUtf8("cmbPayStatus"))
        self.gridlayout.addWidget(self.cmbPayStatus, 14, 2, 1, 1)
        self.lblSocStatusClass = QtGui.QLabel(ReportDD2013WeeklySetupDialog)
        self.lblSocStatusClass.setObjectName(_fromUtf8("lblSocStatusClass"))
        self.gridlayout.addWidget(self.lblSocStatusClass, 16, 0, 1, 1)
        self.cmbSocStatusClass = CSocStatusComboBox(ReportDD2013WeeklySetupDialog)
        self.cmbSocStatusClass.setObjectName(_fromUtf8("cmbSocStatusClass"))
        self.gridlayout.addWidget(self.cmbSocStatusClass, 16, 2, 1, 1)
        self.lblSocStatusType = QtGui.QLabel(ReportDD2013WeeklySetupDialog)
        self.lblSocStatusType.setObjectName(_fromUtf8("lblSocStatusType"))
        self.gridlayout.addWidget(self.lblSocStatusType, 17, 0, 1, 1)
        self.cmbSocStatusType = CRBComboBox(ReportDD2013WeeklySetupDialog)
        self.cmbSocStatusType.setObjectName(_fromUtf8("cmbSocStatusType"))
        self.gridlayout.addWidget(self.cmbSocStatusType, 17, 2, 1, 1)
        self.lblSource = QtGui.QLabel(ReportDD2013WeeklySetupDialog)
        self.lblSource.setObjectName(_fromUtf8("lblSource"))
        self.gridlayout.addWidget(self.lblSource, 11, 0, 1, 1)
        self.lblDDPlan = QtGui.QLabel(ReportDD2013WeeklySetupDialog)
        self.lblDDPlan.setObjectName(_fromUtf8("lblDDPlan"))
        self.gridlayout.addWidget(self.lblDDPlan, 12, 0, 1, 1)
        self.edtDDPlan = QtGui.QLineEdit(ReportDD2013WeeklySetupDialog)
        self.edtDDPlan.setInputMask(_fromUtf8(""))
        self.edtDDPlan.setObjectName(_fromUtf8("edtDDPlan"))
        self.gridlayout.addWidget(self.edtDDPlan, 12, 2, 1, 1)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblAgeTo.setBuddy(self.edtAgeTo)
        self.lblAgeYears.setBuddy(self.edtAgeTo)
        self.lblTerType.setBuddy(self.cmbTerType)
        self.lblPayStatus.setBuddy(self.cmbPayStatus)
        self.lblAge.setBuddy(self.edtAgeFrom)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)
        self.lblDDPlan.setBuddy(self.edtDDPlan)

        self.retranslateUi(ReportDD2013WeeklySetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportDD2013WeeklySetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportDD2013WeeklySetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportDD2013WeeklySetupDialog)
        ReportDD2013WeeklySetupDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ReportDD2013WeeklySetupDialog.setTabOrder(self.edtEndDate, self.cmbSex)
        ReportDD2013WeeklySetupDialog.setTabOrder(self.cmbSex, self.edtAgeFrom)
        ReportDD2013WeeklySetupDialog.setTabOrder(self.edtAgeFrom, self.edtAgeTo)
        ReportDD2013WeeklySetupDialog.setTabOrder(self.edtAgeTo, self.cmbTerType)
        ReportDD2013WeeklySetupDialog.setTabOrder(self.cmbTerType, self.cmbPayStatus)
        ReportDD2013WeeklySetupDialog.setTabOrder(self.cmbPayStatus, self.chkCountUnfinished)
        ReportDD2013WeeklySetupDialog.setTabOrder(self.chkCountUnfinished, self.buttonBox)

    def retranslateUi(self, ReportDD2013WeeklySetupDialog):
        ReportDD2013WeeklySetupDialog.setWindowTitle(_translate("ReportDD2013WeeklySetupDialog", "параметры отчёта", None))
        self.lblSex.setText(_translate("ReportDD2013WeeklySetupDialog", "По&л", None))
        self.lblAgeTo.setText(_translate("ReportDD2013WeeklySetupDialog", "по", None))
        self.lblAgeYears.setText(_translate("ReportDD2013WeeklySetupDialog", "лет", None))
        self.lblTerType.setText(_translate("ReportDD2013WeeklySetupDialog", "Территориально", None))
        self.lblEventType.setText(_translate("ReportDD2013WeeklySetupDialog", "Тип обращения", None))
        self.lblPayStatus.setText(_translate("ReportDD2013WeeklySetupDialog", "Состояние оплаты", None))
        self.cmbSex.setItemText(1, _translate("ReportDD2013WeeklySetupDialog", "М", None))
        self.cmbSex.setItemText(2, _translate("ReportDD2013WeeklySetupDialog", "Ж", None))
        self.lblAge.setText(_translate("ReportDD2013WeeklySetupDialog", "Во&зраст с", None))
        self.lblBegDate.setText(_translate("ReportDD2013WeeklySetupDialog", "Дата &начала периода", None))
        self.cmbSource.setItemText(0, _translate("ReportDD2013WeeklySetupDialog", "База данных", None))
        self.cmbSource.setItemText(1, _translate("ReportDD2013WeeklySetupDialog", "Предоставленные значения", None))
        self.chkCountUnfinished.setText(_translate("ReportDD2013WeeklySetupDialog", "Учитывать неоконченные обращения", None))
        self.lblEndDate.setText(_translate("ReportDD2013WeeklySetupDialog", "Дата &окончания периода", None))
        self.grbPopulation.setTitle(_translate("ReportDD2013WeeklySetupDialog", "Численность населения", None))
        self.lblWomen.setText(_translate("ReportDD2013WeeklySetupDialog", "Всего женщин", None))
        self.lblWomenPlan.setText(_translate("ReportDD2013WeeklySetupDialog", "План", None))
        self.lblYoung.setText(_translate("ReportDD2013WeeklySetupDialog", "21-36 лет", None))
        self.lblMenPlan.setText(_translate("ReportDD2013WeeklySetupDialog", "План", None))
        self.lblMiddle.setText(_translate("ReportDD2013WeeklySetupDialog", "39-60 лет", None))
        self.lblOld.setText(_translate("ReportDD2013WeeklySetupDialog", "старше 60 лет", None))
        self.lblMen.setText(_translate("ReportDD2013WeeklySetupDialog", "Всего мужчин", None))
        self.cmbTerType.setItemText(0, _translate("ReportDD2013WeeklySetupDialog", "Не задано", None))
        self.cmbTerType.setItemText(1, _translate("ReportDD2013WeeklySetupDialog", "Проживает в субъекте, обслуживаемом ЛПУ", None))
        self.cmbTerType.setItemText(2, _translate("ReportDD2013WeeklySetupDialog", "Прикреплен к ЛПУ", None))
        self.lblSocStatusClass.setText(_translate("ReportDD2013WeeklySetupDialog", "Класс соц. статуса", None))
        self.lblSocStatusType.setText(_translate("ReportDD2013WeeklySetupDialog", "Тип соц. статуса", None))
        self.lblSource.setText(_translate("ReportDD2013WeeklySetupDialog", "Источник данных о населении", None))
        self.lblDDPlan.setText(_translate("ReportDD2013WeeklySetupDialog", "План диспансеризации", None))

from Registry.SocStatusComboBox import CSocStatusComboBox
from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
