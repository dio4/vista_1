# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Events\EventJobTicketsEditorDialog.ui'
#
# Created: Fri Jun 15 12:17:45 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_EventJobTicketsEditor(object):
    def setupUi(self, EventJobTicketsEditor):
        EventJobTicketsEditor.setObjectName(_fromUtf8("EventJobTicketsEditor"))
        EventJobTicketsEditor.resize(400, 292)
        self.verticalLayout = QtGui.QVBoxLayout(EventJobTicketsEditor)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(EventJobTicketsEditor)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabSetJobTicket = QtGui.QWidget()
        self.tabSetJobTicket.setObjectName(_fromUtf8("tabSetJobTicket"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tabSetJobTicket)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tblSetEventJobTickets = CEventJobTicketsView(self.tabSetJobTicket)
        self.tblSetEventJobTickets.setObjectName(_fromUtf8("tblSetEventJobTickets"))
        self.verticalLayout_2.addWidget(self.tblSetEventJobTickets)
        self.tabWidget.addTab(self.tabSetJobTicket, _fromUtf8(""))
        self.tabChangeJobTicket = QtGui.QWidget()
        self.tabChangeJobTicket.setObjectName(_fromUtf8("tabChangeJobTicket"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tabChangeJobTicket)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.tblChangeEventJobTickets = CEventJobTicketsView(self.tabChangeJobTicket)
        self.tblChangeEventJobTickets.setObjectName(_fromUtf8("tblChangeEventJobTickets"))
        self.verticalLayout_3.addWidget(self.tblChangeEventJobTickets)
        self.tabWidget.addTab(self.tabChangeJobTicket, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = CApplyResetDialogButtonBox(EventJobTicketsEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(EventJobTicketsEditor)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EventJobTicketsEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EventJobTicketsEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(EventJobTicketsEditor)

    def retranslateUi(self, EventJobTicketsEditor):
        EventJobTicketsEditor.setWindowTitle(QtGui.QApplication.translate("EventJobTicketsEditor", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSetJobTicket), QtGui.QApplication.translate("EventJobTicketsEditor", "Назначить", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabChangeJobTicket), QtGui.QApplication.translate("EventJobTicketsEditor", "Изменить", None, QtGui.QApplication.UnicodeUTF8))

from library.DialogButtonBox import CApplyResetDialogButtonBox
from Events.EventJobTicketsEditorTable import CEventJobTicketsView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    EventJobTicketsEditor = QtGui.QDialog()
    ui = Ui_EventJobTicketsEditor()
    ui.setupUi(EventJobTicketsEditor)
    EventJobTicketsEditor.show()
    sys.exit(app.exec_())

