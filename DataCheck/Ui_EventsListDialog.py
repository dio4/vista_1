# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\DataCheck\EventsListDialog.ui'
#
# Created: Fri Jun 15 12:16:36 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_eventsListDialog(object):
    def setupUi(self, eventsListDialog):
        eventsListDialog.setObjectName(_fromUtf8("eventsListDialog"))
        eventsListDialog.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(eventsListDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblClientInfo = QtGui.QLabel(eventsListDialog)
        self.lblClientInfo.setText(_fromUtf8(""))
        self.lblClientInfo.setObjectName(_fromUtf8("lblClientInfo"))
        self.gridLayout.addWidget(self.lblClientInfo, 0, 0, 1, 3)
        self.lblSelectInfo = QtGui.QLabel(eventsListDialog)
        self.lblSelectInfo.setText(_fromUtf8(""))
        self.lblSelectInfo.setObjectName(_fromUtf8("lblSelectInfo"))
        self.gridLayout.addWidget(self.lblSelectInfo, 1, 0, 1, 3)
        self.tblListWidget = CTableView(eventsListDialog)
        self.tblListWidget.setObjectName(_fromUtf8("tblListWidget"))
        self.gridLayout.addWidget(self.tblListWidget, 2, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(294, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.btnClose = QtGui.QPushButton(eventsListDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnClose.sizePolicy().hasHeightForWidth())
        self.btnClose.setSizePolicy(sizePolicy)
        self.btnClose.setMinimumSize(QtCore.QSize(100, 0))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 3, 1, 1, 1)
        self.btnCloseCorrect = QtGui.QPushButton(eventsListDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnCloseCorrect.sizePolicy().hasHeightForWidth())
        self.btnCloseCorrect.setSizePolicy(sizePolicy)
        self.btnCloseCorrect.setMinimumSize(QtCore.QSize(100, 0))
        self.btnCloseCorrect.setObjectName(_fromUtf8("btnCloseCorrect"))
        self.gridLayout.addWidget(self.btnCloseCorrect, 3, 2, 1, 1)

        self.retranslateUi(eventsListDialog)
        QtCore.QMetaObject.connectSlotsByName(eventsListDialog)

    def retranslateUi(self, eventsListDialog):
        eventsListDialog.setWindowTitle(QtGui.QApplication.translate("eventsListDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("eventsListDialog", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCloseCorrect.setText(QtGui.QApplication.translate("eventsListDialog", "Прервать", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    eventsListDialog = QtGui.QDialog()
    ui = Ui_eventsListDialog()
    ui.setupUi(eventsListDialog)
    eventsListDialog.show()
    sys.exit(app.exec_())

