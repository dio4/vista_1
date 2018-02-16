# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\HospitalBeds\HospitalBedsEvent.ui'
#
# Created: Fri Jun 15 12:16:17 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_dialogHospitalBedsEvent(object):
    def setupUi(self, dialogHospitalBedsEvent):
        dialogHospitalBedsEvent.setObjectName(_fromUtf8("dialogHospitalBedsEvent"))
        dialogHospitalBedsEvent.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(dialogHospitalBedsEvent)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblHospitalBedEvent = CTableView(dialogHospitalBedsEvent)
        self.tblHospitalBedEvent.setObjectName(_fromUtf8("tblHospitalBedEvent"))
        self.gridLayout.addWidget(self.tblHospitalBedEvent, 0, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(294, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.btnClose = QtGui.QPushButton(dialogHospitalBedsEvent)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 1, 1, 1, 1)

        self.retranslateUi(dialogHospitalBedsEvent)
        QtCore.QMetaObject.connectSlotsByName(dialogHospitalBedsEvent)

    def retranslateUi(self, dialogHospitalBedsEvent):
        dialogHospitalBedsEvent.setWindowTitle(QtGui.QApplication.translate("dialogHospitalBedsEvent", "События для коек", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("dialogHospitalBedsEvent", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dialogHospitalBedsEvent = QtGui.QDialog()
    ui = Ui_dialogHospitalBedsEvent()
    ui.setupUi(dialogHospitalBedsEvent)
    dialogHospitalBedsEvent.show()
    sys.exit(app.exec_())

