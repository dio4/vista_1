# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/craz/s11_remote/Exchange/ImportEISOMSFull.ui'
#
# Created: Thu Nov 15 23:50:16 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportEISOMSFull(object):
    def setupUi(self, ImportEISOMSFull):
        ImportEISOMSFull.setObjectName(_fromUtf8("ImportEISOMSFull"))
        ImportEISOMSFull.resize(553, 281)
        self.gridLayout = QtGui.QGridLayout(ImportEISOMSFull)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btnImport = QtGui.QPushButton(ImportEISOMSFull)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self.gridLayout.addWidget(self.btnImport, 6, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(ImportEISOMSFull)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(ImportEISOMSFull)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.horizontalLayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportEISOMSFull)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.horizontalLayout.addWidget(self.btnSelectFile)
        self.btnView = QtGui.QPushButton(ImportEISOMSFull)
        self.btnView.setObjectName(_fromUtf8("btnView"))
        self.horizontalLayout.addWidget(self.btnView)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(283, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 6, 1, 1, 1)
        self.progressBar = QtGui.QProgressBar(ImportEISOMSFull)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 3, 0, 1, 3)
        self.btnClose = QtGui.QPushButton(ImportEISOMSFull)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 6, 2, 1, 1)
        self.log = QtGui.QTextBrowser(ImportEISOMSFull)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridLayout.addWidget(self.log, 4, 0, 1, 3)
        self.chkConnectUnverified = QtGui.QCheckBox(ImportEISOMSFull)
        self.chkConnectUnverified.setObjectName(_fromUtf8("chkConnectUnverified"))
        self.gridLayout.addWidget(self.chkConnectUnverified, 1, 0, 1, 3)
        self.chkUpdateClientInfo = QtGui.QCheckBox(ImportEISOMSFull)
        self.chkUpdateClientInfo.setObjectName(_fromUtf8("chkUpdateClientInfo"))
        self.gridLayout.addWidget(self.chkUpdateClientInfo, 2, 0, 1, 3)

        self.retranslateUi(ImportEISOMSFull)
        QtCore.QMetaObject.connectSlotsByName(ImportEISOMSFull)

    def retranslateUi(self, ImportEISOMSFull):
        ImportEISOMSFull.setWindowTitle(QtGui.QApplication.translate("ImportEISOMSFull", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("ImportEISOMSFull", "Начать импорт", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportEISOMSFull", "Импортировать из:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("ImportEISOMSFull", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnView.setText(QtGui.QApplication.translate("ImportEISOMSFull", "Просмотреть", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("ImportEISOMSFull", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.chkConnectUnverified.setToolTip(QtGui.QApplication.translate("ImportEISOMSFull", "Если найдено совпадение по ФИО, полу и дате рождения и нет других данных для сравнения, не создавать нового пациента", None, QtGui.QApplication.UnicodeUTF8))
        self.chkConnectUnverified.setText(QtGui.QApplication.translate("ImportEISOMSFull", "При нехватке данных использовать существующую запись о пациенте", None, QtGui.QApplication.UnicodeUTF8))
        self.chkUpdateClientInfo.setToolTip(QtGui.QApplication.translate("ImportEISOMSFull", "Дополнить отсутствующие в БД записи о документе или полисе", None, QtGui.QApplication.UnicodeUTF8))
        self.chkUpdateClientInfo.setText(QtGui.QApplication.translate("ImportEISOMSFull", "При возможности дополнять информацию о пациенте", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportEISOMSFull = QtGui.QDialog()
    ui = Ui_ImportEISOMSFull()
    ui.setupUi(ImportEISOMSFull)
    ImportEISOMSFull.show()
    sys.exit(app.exec_())

