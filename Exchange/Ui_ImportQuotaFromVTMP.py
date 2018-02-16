# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportQuotaFromVTMP.ui'
#
# Created: Fri Jun 15 12:16:47 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportQuotaFromVTMPDialog(object):
    def setupUi(self, ImportQuotaFromVTMPDialog):
        ImportQuotaFromVTMPDialog.setObjectName(_fromUtf8("ImportQuotaFromVTMPDialog"))
        ImportQuotaFromVTMPDialog.resize(400, 344)
        self.gridLayout = QtGui.QGridLayout(ImportQuotaFromVTMPDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(ImportQuotaFromVTMPDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.edtFileName = QtGui.QLineEdit(ImportQuotaFromVTMPDialog)
        self.edtFileName.setObjectName(_fromUtf8("edtFileName"))
        self.hboxlayout.addWidget(self.edtFileName)
        self.btnSelectFile = QtGui.QToolButton(ImportQuotaFromVTMPDialog)
        self.btnSelectFile.setObjectName(_fromUtf8("btnSelectFile"))
        self.hboxlayout.addWidget(self.btnSelectFile)
        self.gridLayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.progressBar = QtGui.QProgressBar(ImportQuotaFromVTMPDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(389, 33, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self._2 = QtGui.QHBoxLayout()
        self._2.setSpacing(6)
        self._2.setMargin(0)
        self._2.setObjectName(_fromUtf8("_2"))
        self.btnImport = QtGui.QPushButton(ImportQuotaFromVTMPDialog)
        self.btnImport.setObjectName(_fromUtf8("btnImport"))
        self._2.addWidget(self.btnImport)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self._2.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(ImportQuotaFromVTMPDialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self._2.addWidget(self.btnClose)
        self.gridLayout.addLayout(self._2, 5, 0, 1, 1)
        self.logList = QtGui.QListWidget(ImportQuotaFromVTMPDialog)
        self.logList.setObjectName(_fromUtf8("logList"))
        self.gridLayout.addWidget(self.logList, 2, 0, 1, 1)
        self.stat = QtGui.QLabel(ImportQuotaFromVTMPDialog)
        self.stat.setText(_fromUtf8(""))
        self.stat.setObjectName(_fromUtf8("stat"))
        self.gridLayout.addWidget(self.stat, 3, 0, 1, 1)

        self.retranslateUi(ImportQuotaFromVTMPDialog)
        QtCore.QMetaObject.connectSlotsByName(ImportQuotaFromVTMPDialog)

    def retranslateUi(self, ImportQuotaFromVTMPDialog):
        ImportQuotaFromVTMPDialog.setWindowTitle(QtGui.QApplication.translate("ImportQuotaFromVTMPDialog", "Загрузка квот из ВТМП", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ImportQuotaFromVTMPDialog", "Импортировать из", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("ImportQuotaFromVTMPDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnImport.setText(QtGui.QApplication.translate("ImportQuotaFromVTMPDialog", "начать импортирование", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("ImportQuotaFromVTMPDialog", "закрыть", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportQuotaFromVTMPDialog = QtGui.QDialog()
    ui = Ui_ImportQuotaFromVTMPDialog()
    ui.setupUi(ImportQuotaFromVTMPDialog)
    ImportQuotaFromVTMPDialog.show()
    sys.exit(app.exec_())

