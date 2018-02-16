# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\DataCheck\SchemaSync.ui'
#
# Created: Fri Jun 15 12:15:02 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SchemaSyncDialog(object):
    def setupUi(self, SchemaSyncDialog):
        SchemaSyncDialog.setObjectName(_fromUtf8("SchemaSyncDialog"))
        SchemaSyncDialog.resize(426, 448)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/new/prefix1/icons/Icon2.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SchemaSyncDialog.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(SchemaSyncDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.grpServer = QtGui.QGroupBox(SchemaSyncDialog)
        self.grpServer.setObjectName(_fromUtf8("grpServer"))
        self.gridLayout_2 = QtGui.QGridLayout(self.grpServer)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblSeverName = QtGui.QLabel(self.grpServer)
        self.lblSeverName.setObjectName(_fromUtf8("lblSeverName"))
        self.gridLayout_2.addWidget(self.lblSeverName, 0, 0, 1, 1)
        self.edtServerName = QtGui.QLineEdit(self.grpServer)
        self.edtServerName.setObjectName(_fromUtf8("edtServerName"))
        self.gridLayout_2.addWidget(self.edtServerName, 0, 1, 1, 1)
        self.lvlServerPort = QtGui.QLabel(self.grpServer)
        self.lvlServerPort.setObjectName(_fromUtf8("lvlServerPort"))
        self.gridLayout_2.addWidget(self.lvlServerPort, 1, 0, 1, 1)
        self.edtServerPort = QtGui.QSpinBox(self.grpServer)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtServerPort.sizePolicy().hasHeightForWidth())
        self.edtServerPort.setSizePolicy(sizePolicy)
        self.edtServerPort.setMaximum(65535)
        self.edtServerPort.setObjectName(_fromUtf8("edtServerPort"))
        self.gridLayout_2.addWidget(self.edtServerPort, 1, 1, 1, 1)
        self.lblDatabaseName = QtGui.QLabel(self.grpServer)
        self.lblDatabaseName.setObjectName(_fromUtf8("lblDatabaseName"))
        self.gridLayout_2.addWidget(self.lblDatabaseName, 2, 0, 1, 1)
        self.edtDatabaseName = QtGui.QLineEdit(self.grpServer)
        self.edtDatabaseName.setObjectName(_fromUtf8("edtDatabaseName"))
        self.gridLayout_2.addWidget(self.edtDatabaseName, 2, 1, 1, 1)
        self.lblUserName = QtGui.QLabel(self.grpServer)
        self.lblUserName.setObjectName(_fromUtf8("lblUserName"))
        self.gridLayout_2.addWidget(self.lblUserName, 3, 0, 1, 1)
        self.edtUserName = QtGui.QLineEdit(self.grpServer)
        self.edtUserName.setObjectName(_fromUtf8("edtUserName"))
        self.gridLayout_2.addWidget(self.edtUserName, 3, 1, 1, 1)
        self.lblPassword = QtGui.QLabel(self.grpServer)
        self.lblPassword.setObjectName(_fromUtf8("lblPassword"))
        self.gridLayout_2.addWidget(self.lblPassword, 4, 0, 1, 1)
        self.edtPassword = QtGui.QLineEdit(self.grpServer)
        self.edtPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.edtPassword.setObjectName(_fromUtf8("edtPassword"))
        self.gridLayout_2.addWidget(self.edtPassword, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.grpServer, 0, 0, 1, 3)
        self.progressBar = CProgressBar(SchemaSyncDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setTextVisible(True)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 3)
        self.logBrowser = QtGui.QTextBrowser(SchemaSyncDialog)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 2, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(207, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.btnSync = QtGui.QPushButton(SchemaSyncDialog)
        self.btnSync.setMinimumSize(QtCore.QSize(100, 0))
        self.btnSync.setObjectName(_fromUtf8("btnSync"))
        self.gridLayout.addWidget(self.btnSync, 3, 1, 1, 1)
        self.btnClose = QtGui.QPushButton(SchemaSyncDialog)
        self.btnClose.setMinimumSize(QtCore.QSize(100, 0))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 3, 2, 1, 1)

        self.retranslateUi(SchemaSyncDialog)
        QtCore.QMetaObject.connectSlotsByName(SchemaSyncDialog)

    def retranslateUi(self, SchemaSyncDialog):
        SchemaSyncDialog.setWindowTitle(QtGui.QApplication.translate("SchemaSyncDialog", "Синхронизация структуры БД", None, QtGui.QApplication.UnicodeUTF8))
        self.grpServer.setTitle(QtGui.QApplication.translate("SchemaSyncDialog", "Настройка эталонного сервера", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSeverName.setText(QtGui.QApplication.translate("SchemaSyncDialog", "Адрес", None, QtGui.QApplication.UnicodeUTF8))
        self.lvlServerPort.setText(QtGui.QApplication.translate("SchemaSyncDialog", "Порт", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDatabaseName.setText(QtGui.QApplication.translate("SchemaSyncDialog", "База", None, QtGui.QApplication.UnicodeUTF8))
        self.lblUserName.setText(QtGui.QApplication.translate("SchemaSyncDialog", "Логин", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPassword.setText(QtGui.QApplication.translate("SchemaSyncDialog", "Пароль", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSync.setText(QtGui.QApplication.translate("SchemaSyncDialog", "Синхронизация", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("SchemaSyncDialog", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar
import s11main_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SchemaSyncDialog = QtGui.QDialog()
    ui = Ui_SchemaSyncDialog()
    ui.setupUi(SchemaSyncDialog)
    SchemaSyncDialog.show()
    sys.exit(app.exec_())

