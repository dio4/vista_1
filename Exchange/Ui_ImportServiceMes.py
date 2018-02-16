# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportServiceMes.ui'
#
# Created: Fri Jun 15 12:17:00 2012
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
        Dialog.resize(543, 468)
        self.gridlayout = QtGui.QGridLayout(Dialog)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.splitter = QtGui.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.hboxlayout.addWidget(self.splitter)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 2)
        self.statusLabel = QtGui.QLabel(Dialog)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridlayout.addWidget(self.statusLabel, 2, 0, 1, 2)
        self.log = QtGui.QTextBrowser(Dialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridlayout.addWidget(self.log, 3, 0, 1, 2)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.btnImport = QtGui.QPushButton(Dialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.hboxlayout1.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.btnClose = QtGui.QPushButton(Dialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout1.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout1, 6, 0, 1, 2)
        self.checkAdd = QtGui.QCheckBox(Dialog)
        self.checkAdd.setChecked(True)
        self.checkAdd.setObjectName(_fromUtf8("checkAdd"))
        self.gridlayout.addWidget(self.checkAdd, 4, 0, 1, 1)
        self.checkUpdate = QtGui.QCheckBox(Dialog)
        self.checkUpdate.setObjectName(_fromUtf8("checkUpdate"))
        self.gridlayout.addWidget(self.checkUpdate, 5, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Загрузка услуг из МЭС", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("Dialog", "начать импортирование", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Dialog", "закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.checkAdd.setText(QtGui.QApplication.translate("Dialog", "Добавлять новые услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.checkUpdate.setText(QtGui.QApplication.translate("Dialog", "Синхронизировать имена услуг", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

