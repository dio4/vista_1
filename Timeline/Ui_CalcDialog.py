# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Timeline\CalcDialog.ui'
#
# Created: Fri Jun 15 12:15:58 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_CalcDialog(object):
    def setupUi(self, CalcDialog):
        CalcDialog.setObjectName(_fromUtf8("CalcDialog"))
        CalcDialog.resize(347, 205)
        self.gridLayout_2 = QtGui.QGridLayout(CalcDialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(CalcDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setMargin(4)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.boxBudget = QtGui.QCheckBox(self.groupBox)
        self.boxBudget.setChecked(True)
        self.boxBudget.setObjectName(_fromUtf8("boxBudget"))
        self.verticalLayout_2.addWidget(self.boxBudget)
        self.boxOMS = QtGui.QCheckBox(self.groupBox)
        self.boxOMS.setChecked(True)
        self.boxOMS.setObjectName(_fromUtf8("boxOMS"))
        self.verticalLayout_2.addWidget(self.boxOMS)
        self.boxDMS = QtGui.QCheckBox(self.groupBox)
        self.boxDMS.setChecked(True)
        self.boxDMS.setObjectName(_fromUtf8("boxDMS"))
        self.verticalLayout_2.addWidget(self.boxDMS)
        self.boxPlat = QtGui.QCheckBox(self.groupBox)
        self.boxPlat.setChecked(True)
        self.boxPlat.setObjectName(_fromUtf8("boxPlat"))
        self.verticalLayout_2.addWidget(self.boxPlat)
        self.boxCel = QtGui.QCheckBox(self.groupBox)
        self.boxCel.setChecked(True)
        self.boxCel.setObjectName(_fromUtf8("boxCel"))
        self.verticalLayout_2.addWidget(self.boxCel)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 2, 1)
        self.groupBox_2 = QtGui.QGroupBox(CalcDialog)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.boxAmb = QtGui.QCheckBox(self.groupBox_2)
        self.boxAmb.setChecked(True)
        self.boxAmb.setObjectName(_fromUtf8("boxAmb"))
        self.verticalLayout.addWidget(self.boxAmb)
        self.boxDom = QtGui.QCheckBox(self.groupBox_2)
        self.boxDom.setChecked(True)
        self.boxDom.setObjectName(_fromUtf8("boxDom"))
        self.verticalLayout.addWidget(self.boxDom)
        self.boxKAR = QtGui.QCheckBox(self.groupBox_2)
        self.boxKAR.setObjectName(_fromUtf8("boxKAR"))
        self.verticalLayout.addWidget(self.boxKAR)
        self.gridLayout_2.addWidget(self.groupBox_2, 0, 1, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(CalcDialog)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setMargin(4)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.rbFillAll = QtGui.QRadioButton(self.groupBox_3)
        self.rbFillAll.setObjectName(_fromUtf8("rbFillAll"))
        self.verticalLayout_3.addWidget(self.rbFillAll)
        self.rbFillNew = QtGui.QRadioButton(self.groupBox_3)
        self.rbFillNew.setChecked(True)
        self.rbFillNew.setObjectName(_fromUtf8("rbFillNew"))
        self.verticalLayout_3.addWidget(self.rbFillNew)
        self.gridLayout_2.addWidget(self.groupBox_3, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(CalcDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 3, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 2, 0, 1, 1)

        self.retranslateUi(CalcDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CalcDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CalcDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CalcDialog)
        CalcDialog.setTabOrder(self.boxBudget, self.boxOMS)
        CalcDialog.setTabOrder(self.boxOMS, self.boxDMS)
        CalcDialog.setTabOrder(self.boxDMS, self.boxPlat)
        CalcDialog.setTabOrder(self.boxPlat, self.boxCel)
        CalcDialog.setTabOrder(self.boxCel, self.boxAmb)
        CalcDialog.setTabOrder(self.boxAmb, self.boxDom)
        CalcDialog.setTabOrder(self.boxDom, self.boxKAR)
        CalcDialog.setTabOrder(self.boxKAR, self.rbFillAll)
        CalcDialog.setTabOrder(self.rbFillAll, self.rbFillNew)
        CalcDialog.setTabOrder(self.rbFillNew, self.buttonBox)

    def retranslateUi(self, CalcDialog):
        CalcDialog.setWindowTitle(QtGui.QApplication.translate("CalcDialog", "Заполнение фактического количества посещений", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("CalcDialog", "Тип финансирования", None, QtGui.QApplication.UnicodeUTF8))
        self.boxBudget.setText(QtGui.QApplication.translate("CalcDialog", "Бюджет", None, QtGui.QApplication.UnicodeUTF8))
        self.boxOMS.setText(QtGui.QApplication.translate("CalcDialog", "ОМС", None, QtGui.QApplication.UnicodeUTF8))
        self.boxDMS.setText(QtGui.QApplication.translate("CalcDialog", "ДМС", None, QtGui.QApplication.UnicodeUTF8))
        self.boxPlat.setText(QtGui.QApplication.translate("CalcDialog", "Платные", None, QtGui.QApplication.UnicodeUTF8))
        self.boxCel.setText(QtGui.QApplication.translate("CalcDialog", "Целевые", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("CalcDialog", "Место", None, QtGui.QApplication.UnicodeUTF8))
        self.boxAmb.setText(QtGui.QApplication.translate("CalcDialog", "Амб.", None, QtGui.QApplication.UnicodeUTF8))
        self.boxDom.setText(QtGui.QApplication.translate("CalcDialog", "Дом.", None, QtGui.QApplication.UnicodeUTF8))
        self.boxKAR.setText(QtGui.QApplication.translate("CalcDialog", "КЭР", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("CalcDialog", "Заполнение", None, QtGui.QApplication.UnicodeUTF8))
        self.rbFillAll.setText(QtGui.QApplication.translate("CalcDialog", "заполнять всё", None, QtGui.QApplication.UnicodeUTF8))
        self.rbFillNew.setText(QtGui.QApplication.translate("CalcDialog", "только незаполненное", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    CalcDialog = QtGui.QDialog()
    ui = Ui_CalcDialog()
    ui.setupUi(CalcDialog)
    CalcDialog.show()
    sys.exit(app.exec_())

