# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBContactTypeEditor.ui'
#
# Created: Wed Aug  3 14:27:00 2016
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

class Ui_ContractTypeEditorDialog(object):
    def setupUi(self, ContractTypeEditorDialog):
        ContractTypeEditorDialog.setObjectName(_fromUtf8("ContractTypeEditorDialog"))
        ContractTypeEditorDialog.resize(318, 158)
        ContractTypeEditorDialog.setSizeGripEnabled(False)
        self.gridlayout = QtGui.QGridLayout(ContractTypeEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblCode = QtGui.QLabel(ContractTypeEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ContractTypeEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.lblName = QtGui.QLabel(ContractTypeEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ContractTypeEditorDialog)
        self.edtName.setMinimumSize(QtCore.QSize(200, 0))
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(73, 41, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ContractTypeEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        self.lblMask = QtGui.QLabel(ContractTypeEditorDialog)
        self.lblMask.setObjectName(_fromUtf8("lblMask"))
        self.gridlayout.addWidget(self.lblMask, 2, 0, 1, 1)
        self.edtMask = QtGui.QLineEdit(ContractTypeEditorDialog)
        self.edtMask.setObjectName(_fromUtf8("edtMask"))
        self.gridlayout.addWidget(self.edtMask, 2, 1, 1, 1)
        self.chkMaskEnabled = QtGui.QCheckBox(ContractTypeEditorDialog)
        self.chkMaskEnabled.setObjectName(_fromUtf8("chkMaskEnabled"))
        self.gridlayout.addWidget(self.chkMaskEnabled, 3, 1, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(ContractTypeEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ContractTypeEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ContractTypeEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ContractTypeEditorDialog)
        ContractTypeEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ContractTypeEditorDialog.setTabOrder(self.edtName, self.buttonBox)

    def retranslateUi(self, ContractTypeEditorDialog):
        ContractTypeEditorDialog.setWindowTitle(_translate("ContractTypeEditorDialog", "ChangeMe!", None))
        self.lblCode.setText(_translate("ContractTypeEditorDialog", "&Код", None))
        self.lblName.setText(_translate("ContractTypeEditorDialog", "На&именование", None))
        self.lblMask.setText(_translate("ContractTypeEditorDialog", "Маска", None))
        self.edtMask.setToolTip(_translate("ContractTypeEditorDialog", "<table>\n"
"<tr>\n"
"<td><b> Символ</b></td>\n"
"<td><b> Значение</b></td>\n"
"</tr>\n"
"<tr>\n"
"<td> A </td>\n"
"<td> ASCII обязательный символ A-Z, a-z </td>\n"
"</tr>\n"
"<tr>\n"
"<td> a </td>\n"
"<td> ASCII не обязательный символ A-Z, a-z </td>\n"
"</tr>\n"
"<tr>\n"
"<td> N </td>\n"
"<td> ASCII обязательный символ A-Z, a-z, 0-9 </td>\n"
"</tr>\n"
"<tr>\n"
"<td> n </td>\n"
"<td> ASCII не обязательный символ A-Z, a-z, 0-9 </td>\n"
"</tr>\n"
"<tr>\n"
"<td> X </td>\n"
"<td> Любой обязательный символ </td>\n"
"</tr>\n"
"<tr>\n"
"<td> x </td>\n"
"<td> Любой не обязательный символ </td>\n"
"</tr>\n"
"<tr>\n"
"<td> 9 </td>\n"
"<td> Цифра обязательная 0-9</td>\n"
"</tr>\n"
"<tr>\n"
"<td> 0 </td>\n"
"<td> Не обязательная цифра 0-9 </td>\n"
"</tr>\n"
"<tr>\n"
"<td> D </td>\n"
"<td> Цифра обязательная 1-9</td>\n"
"</tr>\n"
"<tr>\n"
"<td> d </td>\n"
"<td> Не обязательная цифра 1-9 </td>\n"
"</tr>\n"
"<tr>\n"
"<td> H </td>\n"
"<td> Шесстнадцатиричная цифра обязательная A-f, a-f, 0-9</td>\n"
"</tr>\n"
"<tr>\n"
"<td> h </td>\n"
"<td> Шесстнадцатиричная цифра не обязательная A-f, a-f, 0-9</td>\n"
"</tr>\n"
"<tr>\n"
"<td> B </td>\n"
"<td> Обязательный бинарный символ 0-1</td>\n"
"</tr>\n"
"<tr>\n"
"<td> b </td>\n"
"<td> Не обязательный бинарный символ 0-1</td>\n"
"</tr>\n"
"<tr>\n"
"<td> &#62; </td>\n"
"<td> Все последующие символы в верхнем регистре</td>\n"
"</tr>\n"
"<tr>\n"
"<td> &#60; </td>\n"
"<td> Все последующие символы в верхнем регистре</td>\n"
"</tr>\n"
"<tr>\n"
"<td> ! </td>\n"
"<td> Отключить учет регистра</td>\n"
"</tr>\n"
"<tr>\n"
"<td> \\ </td>\n"
"<td> Экранирование специальных символов</td>\n"
"</tr>\n"
"</table>\n"
"\n"
"<h3>Примеры: </h3>\n"
"<table>\n"
"<tr>\n"
"<td><b> Маска</b></td>\n"
"<td><b> Значение</b></td>\n"
"</tr>\n"
"<tr>\n"
"<td>000.000.000.000;_</td>\n"
"<td>IP-aдресс, пустые _ </td>\n"
"</tr>\n"
"<tr>\n"
"<td>HH:HH:HH:HH:HH:HH;_ </td>\n"
"<td>MAC-адресс </td>\n"
"</tr>\n"
"<tr>\n"
"<td>9999999999;_</td>\n"
"<td>Мобильный телефон 10 символов </td>\n"
"</tr>\n"
"</table>", None))
        self.chkMaskEnabled.setText(_translate("ContractTypeEditorDialog", "Включить маску", None))

