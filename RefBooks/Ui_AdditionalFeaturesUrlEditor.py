# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AdditionalFeaturesUrlEditor.ui'
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
        ItemEditorDialog.resize(407, 192)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setVisible(False)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 9, 0, 1, 3)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setMaxLength(64)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 2)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.chkTabRegistry = QtGui.QCheckBox(ItemEditorDialog)
        self.chkTabRegistry.setText(_fromUtf8(""))
        self.chkTabRegistry.setObjectName(_fromUtf8("chkTabRegistry"))
        self.gridlayout.addWidget(self.chkTabRegistry, 4, 1, 1, 2)
        self.lblTabRegistry = QtGui.QLabel(ItemEditorDialog)
        self.lblTabRegistry.setObjectName(_fromUtf8("lblTabRegistry"))
        self.gridlayout.addWidget(self.lblTabRegistry, 4, 0, 1, 1)
        self.lblTabEvents = QtGui.QLabel(ItemEditorDialog)
        self.lblTabEvents.setObjectName(_fromUtf8("lblTabEvents"))
        self.gridlayout.addWidget(self.lblTabEvents, 5, 0, 1, 1)
        self.lblAmbCard = QtGui.QLabel(ItemEditorDialog)
        self.lblAmbCard.setObjectName(_fromUtf8("lblAmbCard"))
        self.gridlayout.addWidget(self.lblAmbCard, 6, 0, 1, 1)
        self.lblTabActions = QtGui.QLabel(ItemEditorDialog)
        self.lblTabActions.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblTabActions.setObjectName(_fromUtf8("lblTabActions"))
        self.gridlayout.addWidget(self.lblTabActions, 7, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 8, 0, 1, 1)
        self.chkTabActions = QtGui.QCheckBox(ItemEditorDialog)
        self.chkTabActions.setText(_fromUtf8(""))
        self.chkTabActions.setObjectName(_fromUtf8("chkTabActions"))
        self.gridlayout.addWidget(self.chkTabActions, 7, 1, 1, 1)
        self.chkTabEvents = QtGui.QCheckBox(ItemEditorDialog)
        self.chkTabEvents.setText(_fromUtf8(""))
        self.chkTabEvents.setObjectName(_fromUtf8("chkTabEvents"))
        self.gridlayout.addWidget(self.chkTabEvents, 5, 1, 1, 1)
        self.chkTabAmbCard = QtGui.QCheckBox(ItemEditorDialog)
        self.chkTabAmbCard.setText(_fromUtf8(""))
        self.chkTabAmbCard.setObjectName(_fromUtf8("chkTabAmbCard"))
        self.gridlayout.addWidget(self.chkTabAmbCard, 6, 1, 1, 1)
        self.lblTemplate = QtGui.QLabel(ItemEditorDialog)
        self.lblTemplate.setObjectName(_fromUtf8("lblTemplate"))
        self.gridlayout.addWidget(self.lblTemplate, 2, 0, 1, 1)
        self.edtTemplate = QtGui.QLineEdit(ItemEditorDialog)
        self.edtTemplate.setObjectName(_fromUtf8("edtTemplate"))
        self.gridlayout.addWidget(self.edtTemplate, 2, 1, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setVisible(False)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.label = QtGui.QLabel(ItemEditorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout.addWidget(self.label, 3, 0, 1, 1)
        self.lblName.setBuddy(self.edtName)
        self.lblTabRegistry.setBuddy(self.chkTabRegistry)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtName, self.chkTabRegistry)
        ItemEditorDialog.setTabOrder(self.chkTabRegistry, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(_translate("ItemEditorDialog", "ChangeMe!", None))
        self.edtCode.setText(_translate("ItemEditorDialog", "ok", None))
        self.lblName.setText(_translate("ItemEditorDialog", "&Наименование", None))
        self.lblTabRegistry.setText(_translate("ItemEditorDialog", "Регистратура: Картотека", None))
        self.lblTabEvents.setText(_translate("ItemEditorDialog", "Регистартура: Обращения", None))
        self.lblAmbCard.setToolTip(_translate("ItemEditorDialog", "используйте {Name}\n"
"для подстановки\n"
"значения параметра\n"
"Name", None))
        self.lblAmbCard.setText(_translate("ItemEditorDialog", "Регистратура: Медкарта", None))
        self.lblTabActions.setToolTip(_translate("ItemEditorDialog", "используйте {Name}\n"
"для подстановки\n"
"значения параметра\n"
"Name", None))
        self.lblTabActions.setText(_translate("ItemEditorDialog", "Регистратура: Обслуживание", None))
        self.lblTemplate.setText(_translate("ItemEditorDialog", "Шаблон URL", None))
        self.lblCode.setText(_translate("ItemEditorDialog", "Код", None))
        self.label.setText(_translate("ItemEditorDialog", "Вкладки, в которых подхватывается данное действие:", None))

