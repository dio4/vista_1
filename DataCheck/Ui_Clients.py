# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\DataCheck\Clients.ui'
#
# Created: Fri Jun 15 12:15:01 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ClientsCheckDialog(object):
    def setupUi(self, ClientsCheckDialog):
        ClientsCheckDialog.setObjectName(_fromUtf8("ClientsCheckDialog"))
        ClientsCheckDialog.resize(589, 538)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ClientsCheckDialog.sizePolicy().hasHeightForWidth())
        ClientsCheckDialog.setSizePolicy(sizePolicy)
        ClientsCheckDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ClientsCheckDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.progressBar = CProgressBar(ClientsCheckDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 0, 0, 1, 4)
        self.log = QtGui.QListWidget(ClientsCheckDialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridLayout.addWidget(self.log, 1, 0, 1, 4)
        self.label = QtGui.QLabel(ClientsCheckDialog)
        self.label.setText(_fromUtf8(""))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(361, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.btnStart = QtGui.QPushButton(ClientsCheckDialog)
        self.btnStart.setMinimumSize(QtCore.QSize(100, 0))
        self.btnStart.setObjectName(_fromUtf8("btnStart"))
        self.gridLayout.addWidget(self.btnStart, 2, 2, 1, 1)
        self.btnClose = QtGui.QPushButton(ClientsCheckDialog)
        self.btnClose.setMinimumSize(QtCore.QSize(100, 0))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 2, 3, 1, 1)

        self.retranslateUi(ClientsCheckDialog)
        QtCore.QMetaObject.connectSlotsByName(ClientsCheckDialog)

    def retranslateUi(self, ClientsCheckDialog):
        ClientsCheckDialog.setWindowTitle(QtGui.QApplication.translate("ClientsCheckDialog", "логический контроль клиентов", None, QtGui.QApplication.UnicodeUTF8))
        self.btnStart.setText(QtGui.QApplication.translate("ClientsCheckDialog", "начать проверку", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("ClientsCheckDialog", "прервать", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ClientsCheckDialog = QtGui.QDialog()
    ui = Ui_ClientsCheckDialog()
    ui.setupUi(ClientsCheckDialog)
    ClientsCheckDialog.show()
    sys.exit(app.exec_())

