# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\HospitalBeds\RadialSheetDialog.ui'
#
# Created: Fri Jun 15 12:17:57 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_dialogRadialSheet(object):
    def setupUi(self, dialogRadialSheet):
        dialogRadialSheet.setObjectName(_fromUtf8("dialogRadialSheet"))
        dialogRadialSheet.resize(800, 818)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dialogRadialSheet.sizePolicy().hasHeightForWidth())
        dialogRadialSheet.setSizePolicy(sizePolicy)
        dialogRadialSheet.setAutoFillBackground(False)
        self.tblRadialSheet = QtGui.QTableView(dialogRadialSheet)
        self.tblRadialSheet.setGeometry(QtCore.QRect(9, 137, 771, 551))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblRadialSheet.sizePolicy().hasHeightForWidth())
        self.tblRadialSheet.setSizePolicy(sizePolicy)
        self.tblRadialSheet.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tblRadialSheet.setObjectName(_fromUtf8("tblRadialSheet"))
        self.buttonBox = QtGui.QDialogButtonBox(dialogRadialSheet)
        self.buttonBox.setGeometry(QtCore.QRect(403, 776, 92, 33))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lblPerson = QtGui.QLabel(dialogRadialSheet)
        self.lblPerson.setGeometry(QtCore.QRect(9, 9, 16, 16))
        self.lblPerson.setText(_fromUtf8(""))
        self.lblPerson.setObjectName(_fromUtf8("lblPerson"))
        self.tblRadiationSource = QtGui.QTableView(dialogRadialSheet)
        self.tblRadiationSource.setGeometry(QtCore.QRect(9, 29, 256, 81))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblRadiationSource.sizePolicy().hasHeightForWidth())
        self.tblRadiationSource.setSizePolicy(sizePolicy)
        self.tblRadiationSource.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tblRadiationSource.setObjectName(_fromUtf8("tblRadiationSource"))
        self.widget = QtGui.QWidget(dialogRadialSheet)
        self.widget.setGeometry(QtCore.QRect(10, 720, 771, 51))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.plainTextEdit = QtGui.QPlainTextEdit(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        self.plainTextEdit.setSizePolicy(sizePolicy)
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.verticalLayout.addWidget(self.plainTextEdit)

        self.retranslateUi(dialogRadialSheet)
        QtCore.QMetaObject.connectSlotsByName(dialogRadialSheet)

    def retranslateUi(self, dialogRadialSheet):
        dialogRadialSheet.setWindowTitle(QtGui.QApplication.translate("dialogRadialSheet", "Лучевой листок", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("dialogRadialSheet", "Заключение", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dialogRadialSheet = QtGui.QDialog()
    ui = Ui_dialogRadialSheet()
    ui.setupUi(dialogRadialSheet)
    dialogRadialSheet.show()
    sys.exit(app.exec_())

