# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './Exchange/DbfToMySqlDumpDialog.ui'
#
# Created: Tue Jul 17 18:25:48 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DbfToMySqlDumpDialog(object):
    def setupUi(self, DbfToMySqlDumpDialog):
        DbfToMySqlDumpDialog.setObjectName(_fromUtf8("DbfToMySqlDumpDialog"))
        DbfToMySqlDumpDialog.resize(574, 488)
        self.gridLayout_3 = QtGui.QGridLayout(DbfToMySqlDumpDialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gbOutStmtText = QtGui.QGroupBox(DbfToMySqlDumpDialog)
        self.gbOutStmtText.setObjectName(_fromUtf8("gbOutStmtText"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gbOutStmtText)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.outStmtText = QtGui.QPlainTextEdit(self.gbOutStmtText)
        self.outStmtText.setObjectName(_fromUtf8("outStmtText"))
        self.gridLayout_2.addWidget(self.outStmtText, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.gbOutStmtText, 7, 0, 1, 4)
        self.btnGenerate = QtGui.QPushButton(DbfToMySqlDumpDialog)
        self.btnGenerate.setObjectName(_fromUtf8("btnGenerate"))
        self.gridLayout_3.addWidget(self.btnGenerate, 0, 2, 1, 1)
        self.btnClose = QtGui.QPushButton(DbfToMySqlDumpDialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout_3.addWidget(self.btnClose, 0, 3, 1, 1)
        self.gbSourceFilesList = QtGui.QGroupBox(DbfToMySqlDumpDialog)
        self.gbSourceFilesList.setObjectName(_fromUtf8("gbSourceFilesList"))
        self.gridLayout = QtGui.QGridLayout(self.gbSourceFilesList)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lstSourceFiles = QtGui.QListWidget(self.gbSourceFilesList)
        self.lstSourceFiles.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.lstSourceFiles.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lstSourceFiles.setObjectName(_fromUtf8("lstSourceFiles"))
        self.gridLayout.addWidget(self.lstSourceFiles, 0, 0, 1, 2)
        self.btnAddFiles = QtGui.QPushButton(self.gbSourceFilesList)
        self.btnAddFiles.setObjectName(_fromUtf8("btnAddFiles"))
        self.gridLayout.addWidget(self.btnAddFiles, 1, 0, 1, 1)
        self.btnDelFiles = QtGui.QPushButton(self.gbSourceFilesList)
        self.btnDelFiles.setObjectName(_fromUtf8("btnDelFiles"))
        self.gridLayout.addWidget(self.btnDelFiles, 1, 1, 1, 1)
        self.gridLayout_3.addWidget(self.gbSourceFilesList, 0, 0, 7, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 0, 1, 1, 1)
        self.chkSaveToFile = QtGui.QCheckBox(DbfToMySqlDumpDialog)
        self.chkSaveToFile.setChecked(True)
        self.chkSaveToFile.setObjectName(_fromUtf8("chkSaveToFile"))
        self.gridLayout_3.addWidget(self.chkSaveToFile, 1, 2, 1, 2)
        self.lblMySqlCodec = QtGui.QLabel(DbfToMySqlDumpDialog)
        self.lblMySqlCodec.setObjectName(_fromUtf8("lblMySqlCodec"))
        self.gridLayout_3.addWidget(self.lblMySqlCodec, 3, 1, 1, 2)
        self.cmbMySqlCodec = QtGui.QComboBox(DbfToMySqlDumpDialog)
        self.cmbMySqlCodec.setObjectName(_fromUtf8("cmbMySqlCodec"))
        self.cmbMySqlCodec.addItem(_fromUtf8(""))
        self.cmbMySqlCodec.addItem(_fromUtf8(""))
        self.cmbMySqlCodec.addItem(_fromUtf8(""))
        self.gridLayout_3.addWidget(self.cmbMySqlCodec, 4, 1, 1, 3)
        self.lblDbfCodec = QtGui.QLabel(DbfToMySqlDumpDialog)
        self.lblDbfCodec.setObjectName(_fromUtf8("lblDbfCodec"))
        self.gridLayout_3.addWidget(self.lblDbfCodec, 5, 1, 1, 2)
        self.cmbDbfCodec = QtGui.QComboBox(DbfToMySqlDumpDialog)
        self.cmbDbfCodec.setObjectName(_fromUtf8("cmbDbfCodec"))
        self.cmbDbfCodec.addItem(_fromUtf8(""))
        self.cmbDbfCodec.addItem(_fromUtf8(""))
        self.cmbDbfCodec.addItem(_fromUtf8(""))
        self.gridLayout_3.addWidget(self.cmbDbfCodec, 6, 1, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem1, 2, 2, 1, 1)

        self.retranslateUi(DbfToMySqlDumpDialog)
        self.cmbDbfCodec.setCurrentIndex(2)
        QtCore.QObject.connect(self.btnClose, QtCore.SIGNAL(_fromUtf8("clicked()")), DbfToMySqlDumpDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(DbfToMySqlDumpDialog)

    def retranslateUi(self, DbfToMySqlDumpDialog):
        DbfToMySqlDumpDialog.setWindowTitle(QtGui.QApplication.translate("DbfToMySqlDumpDialog", "Формирование файла дампов MySql из DBF", None, QtGui.QApplication.UnicodeUTF8))
        self.gbOutStmtText.setTitle(QtGui.QApplication.translate("DbfToMySqlDumpDialog", "Текст полученного mysql dump файла", None, QtGui.QApplication.UnicodeUTF8))
        self.btnGenerate.setText(QtGui.QApplication.translate("DbfToMySqlDumpDialog", "Сгенерировать", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("DbfToMySqlDumpDialog", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.gbSourceFilesList.setTitle(QtGui.QApplication.translate("DbfToMySqlDumpDialog", "Исходные файлы", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAddFiles.setText(QtGui.QApplication.translate("DbfToMySqlDumpDialog", "Добавить файл(ы) ...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDelFiles.setText(QtGui.QApplication.translate("DbfToMySqlDumpDialog", "Удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.chkSaveToFile.setText(QtGui.QApplication.translate("DbfToMySqlDumpDialog", "Сохранить результат в файл", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMySqlCodec.setText(QtGui.QApplication.translate("DbfToMySqlDumpDialog", "MySql Charset:", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbMySqlCodec.setItemText(0, QtGui.QApplication.translate("DbfToMySqlDumpDialog", "utf8", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbMySqlCodec.setItemText(1, QtGui.QApplication.translate("DbfToMySqlDumpDialog", "cp1251", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbMySqlCodec.setItemText(2, QtGui.QApplication.translate("DbfToMySqlDumpDialog", "cp866", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDbfCodec.setText(QtGui.QApplication.translate("DbfToMySqlDumpDialog", "Кодировка DBF:", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbDbfCodec.setItemText(0, QtGui.QApplication.translate("DbfToMySqlDumpDialog", "utf8", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbDbfCodec.setItemText(1, QtGui.QApplication.translate("DbfToMySqlDumpDialog", "cp1251", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbDbfCodec.setItemText(2, QtGui.QApplication.translate("DbfToMySqlDumpDialog", "cp866", None, QtGui.QApplication.UnicodeUTF8))

