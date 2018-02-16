# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBAccountExportFormatEditor.ui'
#
# Created: Fri Jun 15 12:15:39 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ItemEditorDialog(object):
    def setupUi(self, ItemEditorDialog):
        ItemEditorDialog.setObjectName(_fromUtf8("ItemEditorDialog"))
        ItemEditorDialog.resize(407, 414)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 9, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(131, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 0, 2, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setMaxLength(8)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setMaxLength(64)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 1, 1, 1, 2)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.lblProg = QtGui.QLabel(ItemEditorDialog)
        self.lblProg.setObjectName(_fromUtf8("lblProg"))
        self.gridlayout.addWidget(self.lblProg, 2, 0, 1, 1)
        self.edtProg = QtGui.QLineEdit(ItemEditorDialog)
        self.edtProg.setMaxLength(128)
        self.edtProg.setObjectName(_fromUtf8("edtProg"))
        self.gridlayout.addWidget(self.edtProg, 2, 1, 1, 2)
        self.edtPreferentArchiver = QtGui.QLineEdit(ItemEditorDialog)
        self.edtPreferentArchiver.setMaxLength(128)
        self.edtPreferentArchiver.setObjectName(_fromUtf8("edtPreferentArchiver"))
        self.gridlayout.addWidget(self.edtPreferentArchiver, 3, 1, 1, 2)
        self.lblPreferentArchiver = QtGui.QLabel(ItemEditorDialog)
        self.lblPreferentArchiver.setObjectName(_fromUtf8("lblPreferentArchiver"))
        self.gridlayout.addWidget(self.lblPreferentArchiver, 3, 0, 1, 1)
        self.chkEmailRequired = QtGui.QCheckBox(ItemEditorDialog)
        self.chkEmailRequired.setText(_fromUtf8(""))
        self.chkEmailRequired.setObjectName(_fromUtf8("chkEmailRequired"))
        self.gridlayout.addWidget(self.chkEmailRequired, 4, 1, 1, 2)
        self.lblEmailRequired = QtGui.QLabel(ItemEditorDialog)
        self.lblEmailRequired.setObjectName(_fromUtf8("lblEmailRequired"))
        self.gridlayout.addWidget(self.lblEmailRequired, 4, 0, 1, 1)
        self.lblEmailTo = QtGui.QLabel(ItemEditorDialog)
        self.lblEmailTo.setObjectName(_fromUtf8("lblEmailTo"))
        self.gridlayout.addWidget(self.lblEmailTo, 5, 0, 1, 1)
        self.edtEmailTo = QtGui.QLineEdit(ItemEditorDialog)
        self.edtEmailTo.setMaxLength(64)
        self.edtEmailTo.setObjectName(_fromUtf8("edtEmailTo"))
        self.gridlayout.addWidget(self.edtEmailTo, 5, 1, 1, 2)
        self.lblSubject = QtGui.QLabel(ItemEditorDialog)
        self.lblSubject.setObjectName(_fromUtf8("lblSubject"))
        self.gridlayout.addWidget(self.lblSubject, 6, 0, 1, 1)
        self.edtSubject = QtGui.QLineEdit(ItemEditorDialog)
        self.edtSubject.setMaxLength(128)
        self.edtSubject.setObjectName(_fromUtf8("edtSubject"))
        self.gridlayout.addWidget(self.edtSubject, 6, 1, 1, 2)
        self.lblMessage = QtGui.QLabel(ItemEditorDialog)
        self.lblMessage.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblMessage.setObjectName(_fromUtf8("lblMessage"))
        self.gridlayout.addWidget(self.lblMessage, 7, 0, 1, 1)
        self.edtMessage = QtGui.QTextEdit(ItemEditorDialog)
        self.edtMessage.setObjectName(_fromUtf8("edtMessage"))
        self.gridlayout.addWidget(self.edtMessage, 7, 1, 2, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 8, 0, 1, 1)
        self.lblName.setBuddy(self.edtName)
        self.lblCode.setBuddy(self.edtCode)
        self.lblProg.setBuddy(self.edtProg)
        self.lblPreferentArchiver.setBuddy(self.edtPreferentArchiver)
        self.lblEmailRequired.setBuddy(self.chkEmailRequired)
        self.lblEmailTo.setBuddy(self.edtEmailTo)
        self.lblSubject.setBuddy(self.edtSubject)
        self.lblMessage.setBuddy(self.edtMessage)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.edtProg)
        ItemEditorDialog.setTabOrder(self.edtProg, self.edtPreferentArchiver)
        ItemEditorDialog.setTabOrder(self.edtPreferentArchiver, self.chkEmailRequired)
        ItemEditorDialog.setTabOrder(self.chkEmailRequired, self.edtEmailTo)
        ItemEditorDialog.setTabOrder(self.edtEmailTo, self.edtSubject)
        ItemEditorDialog.setTabOrder(self.edtSubject, self.edtMessage)
        ItemEditorDialog.setTabOrder(self.edtMessage, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(QtGui.QApplication.translate("ItemEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblProg.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Подпрограмма", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPreferentArchiver.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Архиватор", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEmailRequired.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Отправлять по эл.почте", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEmailTo.setText(QtGui.QApplication.translate("ItemEditorDialog", "Aдрес &эл.почты", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSubject.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "используйте {Name}\n"
"для подстановки\n"
"значения параметра\n"
"Name", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSubject.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Тема сообщения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMessage.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "используйте {Name}\n"
"для подстановки\n"
"значения параметра\n"
"Name", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMessage.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Заготовка сообщения", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemEditorDialog = QtGui.QDialog()
    ui = Ui_ItemEditorDialog()
    ui.setupUi(ItemEditorDialog)
    ItemEditorDialog.show()
    sys.exit(app.exec_())

