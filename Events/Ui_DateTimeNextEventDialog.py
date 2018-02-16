# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/natkuch/s11/Events/DateTimeNextEventDialog.ui'
#
# Created: Tue Mar  6 15:22:59 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DateTimeNextEventDialog(object):
    def setupUi(self, DateTimeNextEventDialog):
        DateTimeNextEventDialog.setObjectName(_fromUtf8("DateTimeNextEventDialog"))
        DateTimeNextEventDialog.resize(248, 98)
        self.gridLayout = QtGui.QGridLayout(DateTimeNextEventDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.edtExecTimeNew = QtGui.QTimeEdit(DateTimeNextEventDialog)
        self.edtExecTimeNew.setObjectName(_fromUtf8("edtExecTimeNew"))
        self.gridLayout.addWidget(self.edtExecTimeNew, 0, 2, 1, 2)
        spacerItem = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 4, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 1, 3, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(DateTimeNextEventDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 4)
        self.lblExecTimeNew = QtGui.QLabel(DateTimeNextEventDialog)
        self.lblExecTimeNew.setObjectName(_fromUtf8("lblExecTimeNew"))
        self.gridLayout.addWidget(self.lblExecTimeNew, 0, 0, 1, 1)
        self.edtExecDateNew = CDateEdit(DateTimeNextEventDialog)
        self.edtExecDateNew.setCalendarPopup(True)
        self.edtExecDateNew.setObjectName(_fromUtf8("edtExecDateNew"))
        self.gridLayout.addWidget(self.edtExecDateNew, 0, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 2, 4, 1, 2)

        self.retranslateUi(DateTimeNextEventDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DateTimeNextEventDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DateTimeNextEventDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DateTimeNextEventDialog)

    def retranslateUi(self, DateTimeNextEventDialog):
        DateTimeNextEventDialog.setWindowTitle(QtGui.QApplication.translate("DateTimeNextEventDialog", "Время выполнения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblExecTimeNew.setText(QtGui.QApplication.translate("DateTimeNextEventDialog", "Дата и время", None, QtGui.QApplication.UnicodeUTF8))

from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DateTimeNextEventDialog = QtGui.QDialog()
    ui = Ui_DateTimeNextEventDialog()
    ui.setupUi(DateTimeNextEventDialog)
    DateTimeNextEventDialog.show()
    sys.exit(app.exec_())

