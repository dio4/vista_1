# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\DataCheck\Events.ui'
#
# Created: Fri Jun 15 12:15:02 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_EventsCheckDialog(object):
    def setupUi(self, EventsCheckDialog):
        EventsCheckDialog.setObjectName(_fromUtf8("EventsCheckDialog"))
        EventsCheckDialog.resize(519, 597)
        self.gridLayout = QtGui.QGridLayout(EventsCheckDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.widget = QtGui.QWidget(EventsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.dateEdit_1 = QtGui.QDateEdit(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateEdit_1.sizePolicy().hasHeightForWidth())
        self.dateEdit_1.setSizePolicy(sizePolicy)
        self.dateEdit_1.setDateTime(QtCore.QDateTime(QtCore.QDate(2009, 1, 1), QtCore.QTime(0, 0, 0)))
        self.dateEdit_1.setCalendarPopup(True)
        self.dateEdit_1.setDate(QtCore.QDate(2009, 1, 1))
        self.dateEdit_1.setObjectName(_fromUtf8("dateEdit_1"))
        self.horizontalLayout.addWidget(self.dateEdit_1)
        self.label_2 = QtGui.QLabel(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.dateEdit_2 = QtGui.QDateEdit(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateEdit_2.sizePolicy().hasHeightForWidth())
        self.dateEdit_2.setSizePolicy(sizePolicy)
        self.dateEdit_2.setDateTime(QtCore.QDateTime(QtCore.QDate(2009, 12, 31), QtCore.QTime(0, 0, 0)))
        self.dateEdit_2.setCalendarPopup(True)
        self.dateEdit_2.setDate(QtCore.QDate(2009, 12, 31))
        self.dateEdit_2.setObjectName(_fromUtf8("dateEdit_2"))
        self.horizontalLayout.addWidget(self.dateEdit_2)
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(301, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 3)
        self.checkPayed = QtGui.QCheckBox(EventsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkPayed.sizePolicy().hasHeightForWidth())
        self.checkPayed.setSizePolicy(sizePolicy)
        self.checkPayed.setChecked(True)
        self.checkPayed.setObjectName(_fromUtf8("checkPayed"))
        self.gridLayout.addWidget(self.checkPayed, 1, 0, 1, 4)
        self.checkExt = QtGui.QCheckBox(EventsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkExt.sizePolicy().hasHeightForWidth())
        self.checkExt.setSizePolicy(sizePolicy)
        self.checkExt.setObjectName(_fromUtf8("checkExt"))
        self.gridLayout.addWidget(self.checkExt, 2, 0, 1, 4)
        self.checkSetPerson = QtGui.QCheckBox(EventsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkSetPerson.sizePolicy().hasHeightForWidth())
        self.checkSetPerson.setSizePolicy(sizePolicy)
        self.checkSetPerson.setObjectName(_fromUtf8("checkSetPerson"))
        self.gridLayout.addWidget(self.checkSetPerson, 3, 0, 1, 4)
        self.checkPolis = QtGui.QCheckBox(EventsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkPolis.sizePolicy().hasHeightForWidth())
        self.checkPolis.setSizePolicy(sizePolicy)
        self.checkPolis.setObjectName(_fromUtf8("checkPolis"))
        self.gridLayout.addWidget(self.checkPolis, 4, 0, 1, 4)
        self.tblEventType = CRBListBox(EventsCheckDialog)
        self.tblEventType.setObjectName(_fromUtf8("tblEventType"))
        self.gridLayout.addWidget(self.tblEventType, 5, 0, 1, 4)
        self.progressBar = CProgressBar(EventsCheckDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 6, 0, 1, 4)
        self.log = QtGui.QListWidget(EventsCheckDialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridLayout.addWidget(self.log, 7, 0, 1, 4)
        self.labelInfo = QtGui.QLabel(EventsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelInfo.sizePolicy().hasHeightForWidth())
        self.labelInfo.setSizePolicy(sizePolicy)
        self.labelInfo.setText(_fromUtf8(""))
        self.labelInfo.setObjectName(_fromUtf8("labelInfo"))
        self.gridLayout.addWidget(self.labelInfo, 8, 0, 1, 2)
        self.btnStart = QtGui.QPushButton(EventsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnStart.sizePolicy().hasHeightForWidth())
        self.btnStart.setSizePolicy(sizePolicy)
        self.btnStart.setMinimumSize(QtCore.QSize(100, 0))
        self.btnStart.setObjectName(_fromUtf8("btnStart"))
        self.gridLayout.addWidget(self.btnStart, 8, 2, 1, 1)
        self.btnClose = QtGui.QPushButton(EventsCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnClose.sizePolicy().hasHeightForWidth())
        self.btnClose.setSizePolicy(sizePolicy)
        self.btnClose.setMinimumSize(QtCore.QSize(100, 0))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 8, 3, 1, 1)

        self.retranslateUi(EventsCheckDialog)
        QtCore.QMetaObject.connectSlotsByName(EventsCheckDialog)
        EventsCheckDialog.setTabOrder(self.dateEdit_1, self.dateEdit_2)
        EventsCheckDialog.setTabOrder(self.dateEdit_2, self.checkPayed)
        EventsCheckDialog.setTabOrder(self.checkPayed, self.checkExt)
        EventsCheckDialog.setTabOrder(self.checkExt, self.checkSetPerson)
        EventsCheckDialog.setTabOrder(self.checkSetPerson, self.checkPolis)
        EventsCheckDialog.setTabOrder(self.checkPolis, self.tblEventType)
        EventsCheckDialog.setTabOrder(self.tblEventType, self.log)
        EventsCheckDialog.setTabOrder(self.log, self.btnStart)
        EventsCheckDialog.setTabOrder(self.btnStart, self.btnClose)

    def retranslateUi(self, EventsCheckDialog):
        EventsCheckDialog.setWindowTitle(QtGui.QApplication.translate("EventsCheckDialog", "логический контроль карточек", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("EventsCheckDialog", "с", None, QtGui.QApplication.UnicodeUTF8))
        self.dateEdit_1.setDisplayFormat(QtGui.QApplication.translate("EventsCheckDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("EventsCheckDialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.dateEdit_2.setDisplayFormat(QtGui.QApplication.translate("EventsCheckDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.checkPayed.setText(QtGui.QApplication.translate("EventsCheckDialog", "только оплаченные", None, QtGui.QApplication.UnicodeUTF8))
        self.checkExt.setText(QtGui.QApplication.translate("EventsCheckDialog", "проверять наличие внешнего идентификатора", None, QtGui.QApplication.UnicodeUTF8))
        self.checkSetPerson.setText(QtGui.QApplication.translate("EventsCheckDialog", "проверять наличие ответственного врача", None, QtGui.QApplication.UnicodeUTF8))
        self.checkPolis.setText(QtGui.QApplication.translate("EventsCheckDialog", "проверять срок годности полиса", None, QtGui.QApplication.UnicodeUTF8))
        self.btnStart.setText(QtGui.QApplication.translate("EventsCheckDialog", "начать проверку", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("EventsCheckDialog", "прервать", None, QtGui.QApplication.UnicodeUTF8))

from library.RBListBox import CRBListBox
from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    EventsCheckDialog = QtGui.QDialog()
    ui = Ui_EventsCheckDialog()
    ui.setupUi(EventsCheckDialog)
    EventsCheckDialog.show()
    sys.exit(app.exec_())
