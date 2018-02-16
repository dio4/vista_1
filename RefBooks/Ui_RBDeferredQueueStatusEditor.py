# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RBDeferredQueueStatusEditor.ui'
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

class Ui_ItemEditorDialog(object):
    def setupUi(self, ItemEditorDialog):
        ItemEditorDialog.setObjectName(_fromUtf8("ItemEditorDialog"))
        ItemEditorDialog.resize(295, 151)
        ItemEditorDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkIsSelectable = QtGui.QCheckBox(ItemEditorDialog)
        self.chkIsSelectable.setObjectName(_fromUtf8("chkIsSelectable"))
        self.gridLayout.addWidget(self.chkIsSelectable, 3, 0, 1, 2)
        self.lblFlatCode = QtGui.QLabel(ItemEditorDialog)
        self.lblFlatCode.setObjectName(_fromUtf8("lblFlatCode"))
        self.gridLayout.addWidget(self.lblFlatCode, 1, 0, 1, 1)
        self.edtFlatCode = CLineEdit(ItemEditorDialog)
        self.edtFlatCode.setWhatsThis(_fromUtf8(""))
        self.edtFlatCode.setObjectName(_fromUtf8("edtFlatCode"))
        self.gridLayout.addWidget(self.edtFlatCode, 1, 1, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 2)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 2, 0, 1, 1)
        self.lblFlatCodeAbout = QtGui.QLabel(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFlatCodeAbout.sizePolicy().hasHeightForWidth())
        self.lblFlatCodeAbout.setSizePolicy(sizePolicy)
        self.lblFlatCodeAbout.setMinimumSize(QtCore.QSize(16, 0))
        self.lblFlatCodeAbout.setFrameShape(QtGui.QFrame.Panel)
        self.lblFlatCodeAbout.setFrameShadow(QtGui.QFrame.Plain)
        self.lblFlatCodeAbout.setScaledContents(False)
        self.lblFlatCodeAbout.setAlignment(QtCore.Qt.AlignCenter)
        self.lblFlatCodeAbout.setObjectName(_fromUtf8("lblFlatCodeAbout"))
        self.gridLayout.addWidget(self.lblFlatCodeAbout, 1, 2, 1, 1)
        self.edtCode = CLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 2)
        self.edtName = CLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 2, 1, 1, 2)
        self.lblFlatCode.setBuddy(self.edtFlatCode)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtFlatCode)
        ItemEditorDialog.setTabOrder(self.edtFlatCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.chkIsSelectable)
        ItemEditorDialog.setTabOrder(self.chkIsSelectable, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "Dialog", None))
        self.chkIsSelectable.setText(_translate("ItemEditorDialog", "Разрешается выбор в ЖОС", None))
        self.lblFlatCode.setText(_translate("ItemEditorDialog", "&Flatcode", None))
        self.lblCode.setText(_translate("ItemEditorDialog", "&Код", None))
        self.lblName.setText(_translate("ItemEditorDialog", "&Наименование", None))
        self.lblFlatCodeAbout.setText(_translate("ItemEditorDialog", "?", None))

from library.LineEdit import CLineEdit
