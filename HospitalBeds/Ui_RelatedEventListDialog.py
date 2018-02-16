# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/natkuch/s11/HospitalBeds/RelatedEventListDialog.ui'
#
# Created: Thu Apr  5 16:05:21 2012
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_RelatedEventListDialog(object):
    def setupUi(self, RelatedEventListDialog):
        RelatedEventListDialog.setObjectName(_fromUtf8("RelatedEventListDialog"))
        RelatedEventListDialog.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(RelatedEventListDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblRelatedEventList = CTableView(RelatedEventListDialog)
        self.tblRelatedEventList.setObjectName(_fromUtf8("tblRelatedEventList"))
        self.gridLayout.addWidget(self.tblRelatedEventList, 0, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(221, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.btnPrint = QtGui.QPushButton(RelatedEventListDialog)
        self.btnPrint.setObjectName(_fromUtf8("btnPrint"))
        self.gridLayout.addWidget(self.btnPrint, 1, 1, 1, 1)
        self.btnClose = QtGui.QPushButton(RelatedEventListDialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 1, 2, 1, 1)

        self.retranslateUi(RelatedEventListDialog)
        QtCore.QMetaObject.connectSlotsByName(RelatedEventListDialog)

    def retranslateUi(self, RelatedEventListDialog):
        RelatedEventListDialog.setWindowTitle(QtGui.QApplication.translate("RelatedEventListDialog", "Связанные события", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPrint.setText(QtGui.QApplication.translate("RelatedEventListDialog", "Печать", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("RelatedEventListDialog", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    RelatedEventListDialog = QtGui.QDialog()
    ui = Ui_RelatedEventListDialog()
    ui.setupUi(RelatedEventListDialog)
    RelatedEventListDialog.show()
    sys.exit(app.exec_())

