# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportDD.ui'
#
# Created: Fri Jun 15 12:15:17 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(400, 439)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(Dialog)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.hboxlayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(Dialog)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.hboxlayout.addWidget(self.btnSelectFile)
        self.btnView = QtGui.QPushButton(Dialog)
        self.btnView.setObjectName(_fromUtf8("btnView"))
        self.hboxlayout.addWidget(self.btnView)
        self.gridLayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.hboxlayout1.addWidget(self.label_2)
        self.comboBox = QtGui.QComboBox(Dialog)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.hboxlayout1.addWidget(self.comboBox)
        self.gridLayout.addLayout(self.hboxlayout1, 1, 0, 1, 1)
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName(_fromUtf8("hboxlayout2"))
        self.checkINN = QtGui.QCheckBox(Dialog)
        self.checkINN.setObjectName(_fromUtf8("checkINN"))
        self.hboxlayout2.addWidget(self.checkINN)
        self.edtINN = QtGui.QLineEdit(Dialog)
        self.edtINN.setObjectName(_fromUtf8("edtINN"))
        self.hboxlayout2.addWidget(self.edtINN)
        self.gridLayout.addLayout(self.hboxlayout2, 2, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.cmbPolis = QtGui.QComboBox(Dialog)
        self.cmbPolis.setObjectName(_fromUtf8("cmbPolis"))
        self.horizontalLayout.addWidget(self.cmbPolis)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 6, 0, 1, 1)
        self.stat = QtGui.QLabel(Dialog)
        self.stat.setText(_fromUtf8(""))
        self.stat.setObjectName(_fromUtf8("stat"))
        self.gridLayout.addWidget(self.stat, 7, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 1)
        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setObjectName(_fromUtf8("hboxlayout3"))
        self.btnImport = QtGui.QPushButton(Dialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout3.addWidget(self.btnImport)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout3.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.hboxlayout3, 9, 0, 1, 1)
        self.chkAddNewPatients = QtGui.QCheckBox(Dialog)
        self.chkAddNewPatients.setEnabled(True)
        self.chkAddNewPatients.setChecked(True)
        self.chkAddNewPatients.setObjectName(_fromUtf8("chkAddNewPatients"))
        self.gridLayout.addWidget(self.chkAddNewPatients, 4, 0, 1, 1)
        self.chkUpdatePatients = QtGui.QCheckBox(Dialog)
        self.chkUpdatePatients.setChecked(True)
        self.chkUpdatePatients.setObjectName(_fromUtf8("chkUpdatePatients"))
        self.gridLayout.addWidget(self.chkUpdatePatients, 5, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Загрузка населения (ДД) из ТФОМС", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "импортировать из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnView.setText(QtGui.QApplication.translate("Dialog", "Просмотреть", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "тип прикрепления", None, QtGui.QApplication.UnicodeUTF8))
        self.checkINN.setText(QtGui.QApplication.translate("Dialog", "ИНН работы", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "тип полиса", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("Dialog", "начать импортирование", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Dialog", "закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAddNewPatients.setText(QtGui.QApplication.translate("Dialog", "Добавлять данные о новых пациентах", None, QtGui.QApplication.UnicodeUTF8))
        self.chkUpdatePatients.setText(QtGui.QApplication.translate("Dialog", "Обновлять данные на имеющихся пациентов", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

