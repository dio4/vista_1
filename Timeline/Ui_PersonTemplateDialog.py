# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PersonTemplateDialog.ui'
#
# Created: Tue Apr 23 17:44:07 2013
#      by: PyQt4 UI code generator 4.10
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

class Ui_PersonTemplateDialog(object):
    def setupUi(self, PersonTemplateDialog):
        PersonTemplateDialog.setObjectName(_fromUtf8("PersonTemplateDialog"))
        PersonTemplateDialog.resize(327, 204)
        self.gridLayout = QtGui.QGridLayout(PersonTemplateDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(PersonTemplateDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 1, 1, 1)
        self.dateRangeLayout = QtGui.QHBoxLayout()
        self.dateRangeLayout.setSpacing(4)
        self.dateRangeLayout.setObjectName(_fromUtf8("dateRangeLayout"))
        self.lblBegDate = QtGui.QLabel(PersonTemplateDialog)
        self.lblBegDate.setObjectName(_fromUtf8("lblBegDate"))
        self.dateRangeLayout.addWidget(self.lblBegDate)
        self.edtBegDate = CDateEdit(PersonTemplateDialog)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.dateRangeLayout.addWidget(self.edtBegDate)
        self.lblEndDate = QtGui.QLabel(PersonTemplateDialog)
        self.lblEndDate.setObjectName(_fromUtf8("lblEndDate"))
        self.dateRangeLayout.addWidget(self.lblEndDate)
        self.edtEndDate = CDateEdit(PersonTemplateDialog)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.dateRangeLayout.addWidget(self.edtEndDate)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.dateRangeLayout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.dateRangeLayout, 0, 0, 1, 2)
        self.chkFillRedDaysPerson = QtGui.QCheckBox(PersonTemplateDialog)
        self.chkFillRedDaysPerson.setObjectName(_fromUtf8("chkFillRedDaysPerson"))
        self.gridLayout.addWidget(self.chkFillRedDaysPerson, 3, 0, 1, 2)
        self.chkHomeSecondPeriodPerson = QtGui.QCheckBox(PersonTemplateDialog)
        self.chkHomeSecondPeriodPerson.setObjectName(_fromUtf8("chkHomeSecondPeriodPerson"))
        self.gridLayout.addWidget(self.chkHomeSecondPeriodPerson, 6, 0, 1, 2)
        self.lblInfo = QtGui.QLabel(PersonTemplateDialog)
        self.lblInfo.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lblInfo.setObjectName(_fromUtf8("lblInfo"))
        self.gridLayout.addWidget(self.lblInfo, 1, 0, 1, 2)
        self.lblNamePerson = QtGui.QLabel(PersonTemplateDialog)
        self.lblNamePerson.setText(_fromUtf8(""))
        self.lblNamePerson.setObjectName(_fromUtf8("lblNamePerson"))
        self.gridLayout.addWidget(self.lblNamePerson, 2, 0, 1, 2)
        self.chkAmbSecondPeriodPerson = QtGui.QCheckBox(PersonTemplateDialog)
        self.chkAmbSecondPeriodPerson.setObjectName(_fromUtf8("chkAmbSecondPeriodPerson"))
        self.gridLayout.addWidget(self.chkAmbSecondPeriodPerson, 4, 0, 1, 2)
        self.chkAmbInterPeriodPerson = QtGui.QCheckBox(PersonTemplateDialog)
        self.chkAmbInterPeriodPerson.setEnabled(False)
        self.chkAmbInterPeriodPerson.setObjectName(_fromUtf8("chkAmbInterPeriodPerson"))
        self.gridLayout.addWidget(self.chkAmbInterPeriodPerson, 5, 0, 1, 2)
        self.lblBegDate.setBuddy(self.edtBegDate)
        self.lblEndDate.setBuddy(self.edtEndDate)

        self.retranslateUi(PersonTemplateDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PersonTemplateDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PersonTemplateDialog.reject)
        QtCore.QObject.connect(self.chkAmbSecondPeriodPerson, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkAmbInterPeriodPerson.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(PersonTemplateDialog)
        PersonTemplateDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        PersonTemplateDialog.setTabOrder(self.edtEndDate, self.buttonBox)

    def retranslateUi(self, PersonTemplateDialog):
        PersonTemplateDialog.setWindowTitle(_translate("PersonTemplateDialog", "Персональный шаблон", None))
        self.lblBegDate.setText(_translate("PersonTemplateDialog", "В период &с", None))
        self.lblEndDate.setText(_translate("PersonTemplateDialog", "&По", None))
        self.chkFillRedDaysPerson.setText(_translate("PersonTemplateDialog", "&Заполнять выходные дни", None))
        self.chkHomeSecondPeriodPerson.setText(_translate("PersonTemplateDialog", "&Ввод второго периода вызовов", None))
        self.lblInfo.setText(_translate("PersonTemplateDialog", "Использовать персональный шаблон специалиста", None))
        self.chkAmbSecondPeriodPerson.setText(_translate("PersonTemplateDialog", "&Ввод второго периода приема", None))
        self.chkAmbInterPeriodPerson.setText(_translate("PersonTemplateDialog", "Добавить план между приемами", None))

from library.DateEdit import CDateEdit
