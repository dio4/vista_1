# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\SynchronizeActionTypes.ui'
#
# Created: Fri Jun 15 12:16:50 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SyncDialog(object):
    def setupUi(self, SyncDialog):
        SyncDialog.setObjectName(_fromUtf8("SyncDialog"))
        SyncDialog.resize(478, 572)
        SyncDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtGui.QVBoxLayout(SyncDialog)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(SyncDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.serviceList = QtGui.QListWidget(SyncDialog)
        self.serviceList.setObjectName(_fromUtf8("serviceList"))
        self.verticalLayout.addWidget(self.serviceList)
        self.log = QtGui.QTextBrowser(SyncDialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.verticalLayout.addWidget(self.log)
        self.checkUpdateNames = QtGui.QCheckBox(SyncDialog)
        self.checkUpdateNames.setObjectName(_fromUtf8("checkUpdateNames"))
        self.verticalLayout.addWidget(self.checkUpdateNames)
        self.checkCompareDeleted = QtGui.QCheckBox(SyncDialog)
        self.checkCompareDeleted.setObjectName(_fromUtf8("checkCompareDeleted"))
        self.verticalLayout.addWidget(self.checkCompareDeleted)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnImport = QtGui.QPushButton(SyncDialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.horizontalLayout.addWidget(self.btnImport)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnClose = QtGui.QPushButton(SyncDialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.horizontalLayout.addWidget(self.btnClose)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SyncDialog)
        QtCore.QMetaObject.connectSlotsByName(SyncDialog)

    def retranslateUi(self, SyncDialog):
        SyncDialog.setWindowTitle(QtGui.QApplication.translate("SyncDialog", "Синхронизация типов действий с услугами", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SyncDialog", "Синхронизировать типы действий со следующими услугами:", None, QtGui.QApplication.UnicodeUTF8))
        self.checkUpdateNames.setText(QtGui.QApplication.translate("SyncDialog", "Обновлять названия типов действий по названию услуги", None, QtGui.QApplication.UnicodeUTF8))
        self.checkCompareDeleted.setText(QtGui.QApplication.translate("SyncDialog", "Восстанавливать типы действий, помеченные на удаление", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("SyncDialog", "Синхронизировать", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("SyncDialog", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SyncDialog = QtGui.QDialog()
    ui = Ui_SyncDialog()
    ui.setupUi(SyncDialog)
    SyncDialog.show()
    sys.exit(app.exec_())

