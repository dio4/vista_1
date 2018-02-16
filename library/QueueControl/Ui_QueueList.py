# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QueueList.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_QueueForm(object):
    def setupUi(self, QueueForm):
        QueueForm.setObjectName(_fromUtf8("QueueForm"))
        QueueForm.resize(450, 414)
        self.gridLayout = QtGui.QGridLayout(QueueForm)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblQueue = QtGui.QTableView(QueueForm)
        self.tblQueue.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblQueue.setObjectName(_fromUtf8("tblQueue"))
        self.gridLayout.addWidget(self.tblQueue, 0, 0, 1, 3)
        self.btnCreateQueue = QtGui.QPushButton(QueueForm)
        self.btnCreateQueue.setObjectName(_fromUtf8("btnCreateQueue"))
        self.gridLayout.addWidget(self.btnCreateQueue, 1, 0, 1, 1)
        self.btnRefresh = QtGui.QPushButton(QueueForm)
        self.btnRefresh.setObjectName(_fromUtf8("btnRefresh"))
        self.gridLayout.addWidget(self.btnRefresh, 1, 1, 1, 1)
        self.btnCloseQueue = QtGui.QPushButton(QueueForm)
        self.btnCloseQueue.setObjectName(_fromUtf8("btnCloseQueue"))
        self.gridLayout.addWidget(self.btnCloseQueue, 1, 2, 1, 1)

        self.retranslateUi(QueueForm)
        QtCore.QMetaObject.connectSlotsByName(QueueForm)

    def retranslateUi(self, QueueForm):
        QueueForm.setWindowTitle(_translate("QueueForm", "Управление очередями", None))
        self.btnCreateQueue.setText(_translate("QueueForm", "Добавить очередь", None))
        self.btnRefresh.setText(_translate("QueueForm", "Обновить", None))
        self.btnCloseQueue.setText(_translate("QueueForm", "Закрыть прием", None))

