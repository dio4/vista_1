# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportPayRefuseR23.ui'
#
# Created: Fri Jun 15 12:16:45 2012
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
        Dialog.resize(581, 496)
        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.progressBar = CProgressBar(Dialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 3, 0, 1, 1)
        self.stat = QtGui.QLabel(Dialog)
        self.stat.setText(_fromUtf8(""))
        self.stat.setObjectName(_fromUtf8("stat"))
        self.gridlayout.addWidget(self.stat, 4, 0, 1, 1)
        self.log = QtGui.QTextBrowser(Dialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridlayout.addWidget(self.log, 5, 0, 1, 1)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.btnImport = QtGui.QPushButton(Dialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.labelNum = QtGui.QLabel(Dialog)
        self.labelNum.setObjectName(_fromUtf8("labelNum"))
        self.hboxlayout.addWidget(self.labelNum)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout, 6, 0, 1, 1)
        self.tabImportType = QtGui.QTabWidget(Dialog)
        self.tabImportType.setObjectName(_fromUtf8("tabImportType"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.hboxlayout1.addWidget(self.label_2)
        self.edtConfirmation = QtGui.QLineEdit(self.tab)
        self.edtConfirmation.setObjectName(_fromUtf8("edtConfirmation"))
        self.hboxlayout1.addWidget(self.edtConfirmation)
        self.verticalLayout.addLayout(self.hboxlayout1)
        self.chkOnlyCurrentAccount = QtGui.QCheckBox(self.tab)
        self.chkOnlyCurrentAccount.setChecked(True)
        self.chkOnlyCurrentAccount.setObjectName(_fromUtf8("chkOnlyCurrentAccount"))
        self.verticalLayout.addWidget(self.chkOnlyCurrentAccount)
        self.chkImportPayed = QtGui.QCheckBox(self.tab)
        self.chkImportPayed.setEnabled(False)
        self.chkImportPayed.setChecked(True)
        self.chkImportPayed.setObjectName(_fromUtf8("chkImportPayed"))
        self.verticalLayout.addWidget(self.chkImportPayed)
        self.chkImportRefused = QtGui.QCheckBox(self.tab)
        self.chkImportRefused.setEnabled(False)
        self.chkImportRefused.setChecked(True)
        self.chkImportRefused.setObjectName(_fromUtf8("chkImportRefused"))
        self.verticalLayout.addWidget(self.chkImportRefused)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.tabImportType.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.chkDeleteAccount = QtGui.QCheckBox(self.tab_2)
        self.chkDeleteAccount.setObjectName(_fromUtf8("chkDeleteAccount"))
        self.verticalLayout_2.addWidget(self.chkDeleteAccount)
        self.chkRefreshPolicyInfo = QtGui.QCheckBox(self.tab_2)
        self.chkRefreshPolicyInfo.setObjectName(_fromUtf8("chkRefreshPolicyInfo"))
        self.verticalLayout_2.addWidget(self.chkRefreshPolicyInfo)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.tabImportType.addTab(self.tab_2, _fromUtf8(""))
        self.gridlayout.addWidget(self.tabImportType, 2, 0, 1, 1)
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setObjectName(_fromUtf8("hboxlayout2"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout2.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(Dialog)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.hboxlayout2.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(Dialog)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.hboxlayout2.addWidget(self.btnSelectFile)
        self.btnView = QtGui.QPushButton(Dialog)
        self.btnView.setObjectName(_fromUtf8("btnView"))
        self.hboxlayout2.addWidget(self.btnView)
        self.gridlayout.addLayout(self.hboxlayout2, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridlayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.tabImportType.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Загрузка отказов оплаты для Краснодарского края", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("Dialog", "начать импортирование", None, QtGui.QApplication.UnicodeUTF8))
        self.labelNum.setText(QtGui.QApplication.translate("Dialog", "всего записей в источнике:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Dialog", "закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "подтверждение", None, QtGui.QApplication.UnicodeUTF8))
        self.edtConfirmation.setText(QtGui.QApplication.translate("Dialog", "б/н", None, QtGui.QApplication.UnicodeUTF8))
        self.chkOnlyCurrentAccount.setText(QtGui.QApplication.translate("Dialog", "только текущий счёт", None, QtGui.QApplication.UnicodeUTF8))
        self.chkImportPayed.setText(QtGui.QApplication.translate("Dialog", "загружать оплаченные", None, QtGui.QApplication.UnicodeUTF8))
        self.chkImportRefused.setText(QtGui.QApplication.translate("Dialog", "загружать отказы", None, QtGui.QApplication.UnicodeUTF8))
        self.tabImportType.setTabText(self.tabImportType.indexOf(self.tab), QtGui.QApplication.translate("Dialog", "Импорт отказов", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDeleteAccount.setText(QtGui.QApplication.translate("Dialog", "удалять счет при изменении территории страхования одного из пациентов", None, QtGui.QApplication.UnicodeUTF8))
        self.chkRefreshPolicyInfo.setText(QtGui.QApplication.translate("Dialog", "обновить данные о полисах пациентов", None, QtGui.QApplication.UnicodeUTF8))
        self.tabImportType.setTabText(self.tabImportType.indexOf(self.tab_2), QtGui.QApplication.translate("Dialog", "Предварительная проверка счета", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "импортировать из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnView.setText(QtGui.QApplication.translate("Dialog", "Просмотреть", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Выберите операцию:", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

