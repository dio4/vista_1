# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ActionPropertyMergeDialog.ui'
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

class Ui_ActionPropertyMergeDialog(object):
    def setupUi(self, ActionPropertyMergeDialog):
        ActionPropertyMergeDialog.setObjectName(_fromUtf8("ActionPropertyMergeDialog"))
        ActionPropertyMergeDialog.resize(640, 480)
        self.gridLayout = QtGui.QGridLayout(ActionPropertyMergeDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblName = QtGui.QLabel(ActionPropertyMergeDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblName.sizePolicy().hasHeightForWidth())
        self.lblName.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblName.setFont(font)
        self.lblName.setText(_fromUtf8(""))
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 0, 0, 1, 1)
        self.splitter = QtGui.QSplitter(ActionPropertyMergeDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tblSrcProperties = CTableView(self.splitter)
        self.tblSrcProperties.setObjectName(_fromUtf8("tblSrcProperties"))
        self.edtDestProperty = QtGui.QTextEdit(self.splitter)
        self.edtDestProperty.setObjectName(_fromUtf8("edtDestProperty"))
        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ActionPropertyMergeDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(ActionPropertyMergeDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ActionPropertyMergeDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ActionPropertyMergeDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ActionPropertyMergeDialog)
        ActionPropertyMergeDialog.setTabOrder(self.tblSrcProperties, self.edtDestProperty)
        ActionPropertyMergeDialog.setTabOrder(self.edtDestProperty, self.buttonBox)

    def retranslateUi(self, ActionPropertyMergeDialog):
        ActionPropertyMergeDialog.setWindowTitle(_translate("ActionPropertyMergeDialog", "Dialog", None))

from library.TableView import CTableView
