# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Registry/ComplaintsEditDialog.ui'
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

class Ui_ComplaintsEditDialog(object):
    def setupUi(self, ComplaintsEditDialog):
        ComplaintsEditDialog.setObjectName(_fromUtf8("ComplaintsEditDialog"))
        ComplaintsEditDialog.resize(379, 220)
        ComplaintsEditDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ComplaintsEditDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(ComplaintsEditDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.treeTypicalComplaints = QtGui.QTreeView(self.splitter)
        self.treeTypicalComplaints.setObjectName(_fromUtf8("treeTypicalComplaints"))
        self.edtComplaints = QtGui.QTextEdit(self.splitter)
        self.edtComplaints.setObjectName(_fromUtf8("edtComplaints"))
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 2)
        self.chkCito = QtGui.QCheckBox(ComplaintsEditDialog)
        self.chkCito.setObjectName(_fromUtf8("chkCito"))
        self.gridLayout.addWidget(self.chkCito, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ComplaintsEditDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setMinimumSize(QtCore.QSize(0, 0))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)

        self.retranslateUi(ComplaintsEditDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ComplaintsEditDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ComplaintsEditDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ComplaintsEditDialog)
        ComplaintsEditDialog.setTabOrder(self.edtComplaints, self.buttonBox)

    def retranslateUi(self, ComplaintsEditDialog):
        ComplaintsEditDialog.setWindowTitle(_translate("ComplaintsEditDialog", "Жалобы", None))
        self.chkCito.setText(_translate("ComplaintsEditDialog", "Срочная", None))

