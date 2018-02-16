# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBAgreementTypeEditor.ui'
#
# Created: Fri Jun 15 12:16:49 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RBAgreementTypeEditor(object):
    def setupUi(self, RBAgreementTypeEditor):
        RBAgreementTypeEditor.setObjectName(_fromUtf8("RBAgreementTypeEditor"))
        RBAgreementTypeEditor.resize(396, 114)
        RBAgreementTypeEditor.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(RBAgreementTypeEditor)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCode = QtGui.QLabel(RBAgreementTypeEditor)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 2)
        self.edtCode = QtGui.QLineEdit(RBAgreementTypeEditor)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 2, 1, 1)
        self.lblName = QtGui.QLabel(RBAgreementTypeEditor)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 2)
        self.edtName = QtGui.QLineEdit(RBAgreementTypeEditor)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 2, 1, 1)
        self.lblQuotaStatusModifier = QtGui.QLabel(RBAgreementTypeEditor)
        self.lblQuotaStatusModifier.setObjectName(_fromUtf8("lblQuotaStatusModifier"))
        self.gridLayout.addWidget(self.lblQuotaStatusModifier, 2, 0, 1, 2)
        self.cmbQuotaStatusModifier = QtGui.QComboBox(RBAgreementTypeEditor)
        self.cmbQuotaStatusModifier.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbQuotaStatusModifier.sizePolicy().hasHeightForWidth())
        self.cmbQuotaStatusModifier.setSizePolicy(sizePolicy)
        self.cmbQuotaStatusModifier.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.cmbQuotaStatusModifier.setObjectName(_fromUtf8("cmbQuotaStatusModifier"))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.cmbQuotaStatusModifier.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbQuotaStatusModifier, 2, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(RBAgreementTypeEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 2)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblQuotaStatusModifier.setBuddy(self.cmbQuotaStatusModifier)

        self.retranslateUi(RBAgreementTypeEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RBAgreementTypeEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RBAgreementTypeEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(RBAgreementTypeEditor)

    def retranslateUi(self, RBAgreementTypeEditor):
        RBAgreementTypeEditor.setWindowTitle(QtGui.QApplication.translate("RBAgreementTypeEditor", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("RBAgreementTypeEditor", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("RBAgreementTypeEditor", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblQuotaStatusModifier.setText(QtGui.QApplication.translate("RBAgreementTypeEditor", "&Модификатор статуса", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(0, QtGui.QApplication.translate("RBAgreementTypeEditor", "Не меняет", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(1, QtGui.QApplication.translate("RBAgreementTypeEditor", "Отменено", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(2, QtGui.QApplication.translate("RBAgreementTypeEditor", "Ожидание", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(3, QtGui.QApplication.translate("RBAgreementTypeEditor", "Активный талон", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(4, QtGui.QApplication.translate("RBAgreementTypeEditor", "Талон для заполнения", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(5, QtGui.QApplication.translate("RBAgreementTypeEditor", "Заблокированный талон", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(6, QtGui.QApplication.translate("RBAgreementTypeEditor", "Отказано", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(7, QtGui.QApplication.translate("RBAgreementTypeEditor", "Необходимо согласовать дату обслуживания", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(8, QtGui.QApplication.translate("RBAgreementTypeEditor", "Дата обслуживания на согласовании", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(9, QtGui.QApplication.translate("RBAgreementTypeEditor", "Дата обслуживания согласована", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(10, QtGui.QApplication.translate("RBAgreementTypeEditor", "Пролечен", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(11, QtGui.QApplication.translate("RBAgreementTypeEditor", "Обслуживание отложено", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(12, QtGui.QApplication.translate("RBAgreementTypeEditor", "Отказ пациента", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbQuotaStatusModifier.setItemText(13, QtGui.QApplication.translate("RBAgreementTypeEditor", "Импортировано из ВТМП", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    RBAgreementTypeEditor = QtGui.QDialog()
    ui = Ui_RBAgreementTypeEditor()
    ui.setupUi(RBAgreementTypeEditor)
    RBAgreementTypeEditor.show()
    sys.exit(app.exec_())

