# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Quoting\EventsListDialog.ui'
#
# Created: Fri Jun 15 12:16:57 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_EventsListDialog(object):
    def setupUi(self, EventsListDialog):
        EventsListDialog.setObjectName(_fromUtf8("EventsListDialog"))
        EventsListDialog.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(EventsListDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tblEvents = CEventsTableView(EventsListDialog)
        self.tblEvents.setObjectName(_fromUtf8("tblEvents"))
        self.verticalLayout.addWidget(self.tblEvents)

        self.retranslateUi(EventsListDialog)
        QtCore.QMetaObject.connectSlotsByName(EventsListDialog)

    def retranslateUi(self, EventsListDialog):
        EventsListDialog.setWindowTitle(QtGui.QApplication.translate("EventsListDialog", "События", None, QtGui.QApplication.UnicodeUTF8))

from Registry.RegistryTable import CEventsTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    EventsListDialog = QtGui.QDialog()
    ui = Ui_EventsListDialog()
    ui.setupUi(EventsListDialog)
    EventsListDialog.show()
    sys.exit(app.exec_())

