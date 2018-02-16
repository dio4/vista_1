# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\KSGReselectionDialog.ui'
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

class Ui_KSGReselectionDialogForm(object):
    def setupUi(self, KSGReselectionDialogForm):
        KSGReselectionDialogForm.setObjectName(_fromUtf8("KSGReselectionDialogForm"))
        KSGReselectionDialogForm.resize(640, 590)
        self.gridLayout = QtGui.QGridLayout(KSGReselectionDialogForm)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(KSGReselectionDialogForm)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.begDate = CDateEdit(KSGReselectionDialogForm)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.begDate.sizePolicy().hasHeightForWidth())
        self.begDate.setSizePolicy(sizePolicy)
        self.begDate.setObjectName(_fromUtf8("begDate"))
        self.gridLayout.addWidget(self.begDate, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(KSGReselectionDialogForm)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.endDate = CDateEdit(KSGReselectionDialogForm)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.endDate.sizePolicy().hasHeightForWidth())
        self.endDate.setSizePolicy(sizePolicy)
        self.endDate.setObjectName(_fromUtf8("endDate"))
        self.gridLayout.addWidget(self.endDate, 1, 1, 1, 1)
        self.progressBar = QtGui.QProgressBar(KSGReselectionDialogForm)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 2)
        self.logBrowser = QtGui.QTextBrowser(KSGReselectionDialogForm)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logBrowser.sizePolicy().hasHeightForWidth())
        self.logBrowser.setSizePolicy(sizePolicy)
        self.logBrowser.setObjectName(_fromUtf8("logBrowser"))
        self.gridLayout.addWidget(self.logBrowser, 3, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnStart = QtGui.QPushButton(KSGReselectionDialogForm)
        self.btnStart.setObjectName(_fromUtf8("btnStart"))
        self.horizontalLayout.addWidget(self.btnStart)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnClose = QtGui.QPushButton(KSGReselectionDialogForm)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.horizontalLayout.addWidget(self.btnClose)
        self.gridLayout.addLayout(self.horizontalLayout, 4, 0, 1, 2)

        self.retranslateUi(KSGReselectionDialogForm)
        QtCore.QMetaObject.connectSlotsByName(KSGReselectionDialogForm)

    def retranslateUi(self, KSGReselectionDialogForm):
        KSGReselectionDialogForm.setWindowTitle(_translate("KSGReselectionDialogForm", "Перевыставление КСГ в обращениях", None))
        self.label.setText(_translate("KSGReselectionDialogForm", "Дата начала", None))
        self.label_2.setText(_translate("KSGReselectionDialogForm", "Дата окончания", None))
        self.btnStart.setText(_translate("KSGReselectionDialogForm", "Перевыставить", None))
        self.btnClose.setText(_translate("KSGReselectionDialogForm", "Закрыть", None))

from library.DateEdit import CDateEdit
