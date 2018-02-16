# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Stock\ShortedNomenclatureExpense.ui'
#
# Created: Fri Jun 15 12:17:25 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_NonenclatureExpenseDialog(object):
    def setupUi(self, NonenclatureExpenseDialog):
        NonenclatureExpenseDialog.setObjectName(_fromUtf8("NonenclatureExpenseDialog"))
        NonenclatureExpenseDialog.resize(542, 452)
        self.gridLayout = QtGui.QGridLayout(NonenclatureExpenseDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblNote = QtGui.QLabel(NonenclatureExpenseDialog)
        self.lblNote.setObjectName(_fromUtf8("lblNote"))
        self.gridLayout.addWidget(self.lblNote, 0, 0, 1, 1)
        self.edtNote = QtGui.QLineEdit(NonenclatureExpenseDialog)
        self.edtNote.setObjectName(_fromUtf8("edtNote"))
        self.gridLayout.addWidget(self.edtNote, 0, 1, 1, 2)
        self.tblItems = CInDocTableView(NonenclatureExpenseDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblItems.sizePolicy().hasHeightForWidth())
        self.tblItems.setSizePolicy(sizePolicy)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.gridLayout.addWidget(self.tblItems, 1, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(NonenclatureExpenseDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 3)
        self.lblNote.setBuddy(self.edtNote)

        self.retranslateUi(NonenclatureExpenseDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NonenclatureExpenseDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NonenclatureExpenseDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NonenclatureExpenseDialog)
        NonenclatureExpenseDialog.setTabOrder(self.edtNote, self.tblItems)
        NonenclatureExpenseDialog.setTabOrder(self.tblItems, self.buttonBox)

    def retranslateUi(self, NonenclatureExpenseDialog):
        NonenclatureExpenseDialog.setWindowTitle(QtGui.QApplication.translate("NonenclatureExpenseDialog", "Списание ЛСиИМН", None, QtGui.QApplication.UnicodeUTF8))
        self.lblNote.setText(QtGui.QApplication.translate("NonenclatureExpenseDialog", "Примечания", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    NonenclatureExpenseDialog = QtGui.QDialog()
    ui = Ui_NonenclatureExpenseDialog()
    ui.setupUi(NonenclatureExpenseDialog)
    NonenclatureExpenseDialog.show()
    sys.exit(app.exec_())

