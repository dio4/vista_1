# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\RBVisitTypeEditor.ui'
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
        ItemEditorDialog.resize(554, 176)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.edtModifyTailService = QtGui.QLineEdit(ItemEditorDialog)
        self.edtModifyTailService.setEnabled(False)
        self.edtModifyTailService.setObjectName(_fromUtf8("edtModifyTailService"))
        self.gridlayout.addWidget(self.edtModifyTailService, 5, 3, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 8, 0, 1, 4)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 3)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 3)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 7, 0, 1, 1)
        self.chkReplaceService = QtGui.QCheckBox(ItemEditorDialog)
        self.chkReplaceService.setObjectName(_fromUtf8("chkReplaceService"))
        self.gridlayout.addWidget(self.chkReplaceService, 3, 0, 1, 1)
        self.chkModifyHeadService = QtGui.QCheckBox(ItemEditorDialog)
        self.chkModifyHeadService.setObjectName(_fromUtf8("chkModifyHeadService"))
        self.gridlayout.addWidget(self.chkModifyHeadService, 4, 0, 1, 1)
        self.chkNoModifyService = QtGui.QCheckBox(ItemEditorDialog)
        self.chkNoModifyService.setChecked(True)
        self.chkNoModifyService.setObjectName(_fromUtf8("chkNoModifyService"))
        self.gridlayout.addWidget(self.chkNoModifyService, 2, 0, 1, 4)
        self.edtModifyHeadService_N = QtGui.QLineEdit(ItemEditorDialog)
        self.edtModifyHeadService_N.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtModifyHeadService_N.sizePolicy().hasHeightForWidth())
        self.edtModifyHeadService_N.setSizePolicy(sizePolicy)
        self.edtModifyHeadService_N.setObjectName(_fromUtf8("edtModifyHeadService_N"))
        self.gridlayout.addWidget(self.edtModifyHeadService_N, 4, 1, 1, 1)
        self.edtModifyHeadService = QtGui.QLineEdit(ItemEditorDialog)
        self.edtModifyHeadService.setEnabled(False)
        self.edtModifyHeadService.setObjectName(_fromUtf8("edtModifyHeadService"))
        self.gridlayout.addWidget(self.edtModifyHeadService, 4, 3, 1, 1)
        self.label = QtGui.QLabel(ItemEditorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 4, 2, 1, 1)
        self.chkModifyTailService = QtGui.QCheckBox(ItemEditorDialog)
        self.chkModifyTailService.setObjectName(_fromUtf8("chkModifyTailService"))
        self.gridlayout.addWidget(self.chkModifyTailService, 5, 0, 1, 1)
        self.edtModifyTailService_N = QtGui.QLineEdit(ItemEditorDialog)
        self.edtModifyTailService_N.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtModifyTailService_N.sizePolicy().hasHeightForWidth())
        self.edtModifyTailService_N.setSizePolicy(sizePolicy)
        self.edtModifyTailService_N.setObjectName(_fromUtf8("edtModifyTailService_N"))
        self.gridlayout.addWidget(self.edtModifyTailService_N, 5, 1, 1, 1)
        self.label_2 = QtGui.QLabel(ItemEditorDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridlayout.addWidget(self.label_2, 5, 2, 1, 1)
        self.edtReplaceService = QtGui.QLineEdit(ItemEditorDialog)
        self.edtReplaceService.setEnabled(False)
        self.edtReplaceService.setObjectName(_fromUtf8("edtReplaceService"))
        self.gridlayout.addWidget(self.edtReplaceService, 3, 1, 1, 3)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.lblCode.setText(_translate("ItemEditorDialog", "&Код", None))
        self.lblName.setText(_translate("ItemEditorDialog", "&Наименование", None))
        self.chkReplaceService.setText(_translate("ItemEditorDialog", "Заменяет услугу на", None))
        self.chkModifyHeadService.setText(_translate("ItemEditorDialog", "Заменяет начальные", None))
        self.chkNoModifyService.setText(_translate("ItemEditorDialog", "Не меняет услугу", None))
        self.edtModifyHeadService_N.setInputMask(_translate("ItemEditorDialog", "90; ", None))
        self.label.setText(_translate("ItemEditorDialog", "символов на", None))
        self.chkModifyTailService.setText(_translate("ItemEditorDialog", "Заменяет заключительные", None))
        self.edtModifyTailService_N.setInputMask(_translate("ItemEditorDialog", "90; ", None))
        self.label_2.setText(_translate("ItemEditorDialog", "символов на", None))

