# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\RBSceneEditor.ui'
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
        ItemEditorDialog.resize(549, 200)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 2)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 2, 1, 3)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 2)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 2, 1, 3)
        self.edtModifyTailService_N = QtGui.QLineEdit(ItemEditorDialog)
        self.edtModifyTailService_N.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtModifyTailService_N.sizePolicy().hasHeightForWidth())
        self.edtModifyTailService_N.setSizePolicy(sizePolicy)
        self.edtModifyTailService_N.setObjectName(_fromUtf8("edtModifyTailService_N"))
        self.gridLayout.addWidget(self.edtModifyTailService_N, 5, 2, 2, 1)
        self.label_2 = QtGui.QLabel(ItemEditorDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 5, 3, 2, 1)
        self.chkModifyHeadService = QtGui.QCheckBox(ItemEditorDialog)
        self.chkModifyHeadService.setObjectName(_fromUtf8("chkModifyHeadService"))
        self.gridLayout.addWidget(self.chkModifyHeadService, 4, 0, 1, 2)
        self.edtModifyHeadService = QtGui.QLineEdit(ItemEditorDialog)
        self.edtModifyHeadService.setEnabled(False)
        self.edtModifyHeadService.setObjectName(_fromUtf8("edtModifyHeadService"))
        self.gridLayout.addWidget(self.edtModifyHeadService, 4, 4, 1, 1)
        self.chkNoModifyService = QtGui.QCheckBox(ItemEditorDialog)
        self.chkNoModifyService.setChecked(True)
        self.chkNoModifyService.setObjectName(_fromUtf8("chkNoModifyService"))
        self.gridLayout.addWidget(self.chkNoModifyService, 2, 0, 1, 5)
        self.edtModifyHeadService_N = QtGui.QLineEdit(ItemEditorDialog)
        self.edtModifyHeadService_N.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtModifyHeadService_N.sizePolicy().hasHeightForWidth())
        self.edtModifyHeadService_N.setSizePolicy(sizePolicy)
        self.edtModifyHeadService_N.setObjectName(_fromUtf8("edtModifyHeadService_N"))
        self.gridLayout.addWidget(self.edtModifyHeadService_N, 4, 2, 1, 1)
        self.chkModifyTailService = QtGui.QCheckBox(ItemEditorDialog)
        self.chkModifyTailService.setObjectName(_fromUtf8("chkModifyTailService"))
        self.gridLayout.addWidget(self.chkModifyTailService, 5, 0, 2, 2)
        self.edtModifyTailService = QtGui.QLineEdit(ItemEditorDialog)
        self.edtModifyTailService.setEnabled(False)
        self.edtModifyTailService.setObjectName(_fromUtf8("edtModifyTailService"))
        self.gridLayout.addWidget(self.edtModifyTailService, 5, 4, 2, 1)
        self.edtReplaceService = QtGui.QLineEdit(ItemEditorDialog)
        self.edtReplaceService.setEnabled(False)
        self.edtReplaceService.setObjectName(_fromUtf8("edtReplaceService"))
        self.gridLayout.addWidget(self.edtReplaceService, 3, 2, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 9, 4, 1, 1)
        self.chkReplaceService = QtGui.QCheckBox(ItemEditorDialog)
        self.chkReplaceService.setObjectName(_fromUtf8("chkReplaceService"))
        self.gridLayout.addWidget(self.chkReplaceService, 3, 0, 1, 2)
        self.label = QtGui.QLabel(ItemEditorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 4, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 2, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.lblCode.setText(_translate("ItemEditorDialog", "&Код", None))
        self.lblName.setText(_translate("ItemEditorDialog", "&Наименование", None))
        self.edtModifyTailService_N.setInputMask(_translate("ItemEditorDialog", "90; ", None))
        self.label_2.setText(_translate("ItemEditorDialog", "символов на", None))
        self.chkModifyHeadService.setText(_translate("ItemEditorDialog", "Заменяет начальные", None))
        self.chkNoModifyService.setText(_translate("ItemEditorDialog", "Не меняет услугу", None))
        self.edtModifyHeadService_N.setInputMask(_translate("ItemEditorDialog", "90; ", None))
        self.chkModifyTailService.setText(_translate("ItemEditorDialog", "Заменяет заключительные", None))
        self.chkReplaceService.setText(_translate("ItemEditorDialog", "Заменяет услугу на", None))
        self.label.setText(_translate("ItemEditorDialog", "символов на", None))

