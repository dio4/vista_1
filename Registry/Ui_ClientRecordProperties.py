# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Registry\ClientRecordProperties.ui'
#
# Created: Fri Jun 15 12:16:51 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ClientRecordProperties(object):
    def setupUi(self, ClientRecordProperties):
        ClientRecordProperties.setObjectName(_fromUtf8("ClientRecordProperties"))
        ClientRecordProperties.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(ClientRecordProperties)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtInfo = QtGui.QTextEdit(ClientRecordProperties)
        self.edtInfo.setReadOnly(True)
        self.edtInfo.setObjectName(_fromUtf8("edtInfo"))
        self.gridLayout.addWidget(self.edtInfo, 0, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(308, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.btnClose = QtGui.QPushButton(ClientRecordProperties)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 1, 1, 1, 1)

        self.retranslateUi(ClientRecordProperties)
        QtCore.QObject.connect(self.btnClose, QtCore.SIGNAL(_fromUtf8("clicked()")), ClientRecordProperties.close)
        QtCore.QMetaObject.connectSlotsByName(ClientRecordProperties)

    def retranslateUi(self, ClientRecordProperties):
        ClientRecordProperties.setWindowTitle(QtGui.QApplication.translate("ClientRecordProperties", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("ClientRecordProperties", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ClientRecordProperties = QtGui.QDialog()
    ui = Ui_ClientRecordProperties()
    ui.setupUi(ClientRecordProperties)
    ClientRecordProperties.show()
    sys.exit(app.exec_())

