# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\MKBSubclassEditor.ui'
#
# Created: Fri Jun 15 12:15:37 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MKBSubclassEditorDialog(object):
    def setupUi(self, MKBSubclassEditorDialog):
        MKBSubclassEditorDialog.setObjectName(_fromUtf8("MKBSubclassEditorDialog"))
        MKBSubclassEditorDialog.resize(704, 627)
        MKBSubclassEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(MKBSubclassEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.label = QtGui.QLabel(MKBSubclassEditorDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.vboxlayout.addWidget(self.label)
        self.tblSubclass = CTableView(MKBSubclassEditorDialog)
        self.tblSubclass.setObjectName(_fromUtf8("tblSubclass"))
        self.vboxlayout.addWidget(self.tblSubclass)
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(4)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.btnAdd = QtGui.QPushButton(MKBSubclassEditorDialog)
        self.btnAdd.setObjectName(_fromUtf8("btnAdd"))
        self.hboxlayout.addWidget(self.btnAdd)
        self.btnEdit = QtGui.QPushButton(MKBSubclassEditorDialog)
        self.btnEdit.setObjectName(_fromUtf8("btnEdit"))
        self.hboxlayout.addWidget(self.btnEdit)
        self.btnDel = QtGui.QPushButton(MKBSubclassEditorDialog)
        self.btnDel.setEnabled(False)
        self.btnDel.setObjectName(_fromUtf8("btnDel"))
        self.hboxlayout.addWidget(self.btnDel)
        self.vboxlayout.addLayout(self.hboxlayout)
        self.gridlayout.addLayout(self.vboxlayout, 0, 0, 1, 1)
        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setSpacing(4)
        self.vboxlayout1.setObjectName(_fromUtf8("vboxlayout1"))
        self.label_2 = QtGui.QLabel(MKBSubclassEditorDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.vboxlayout1.addWidget(self.label_2)
        self.tblSubclass_Item = CTableView(MKBSubclassEditorDialog)
        self.tblSubclass_Item.setObjectName(_fromUtf8("tblSubclass_Item"))
        self.vboxlayout1.addWidget(self.tblSubclass_Item)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setSpacing(4)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.btnAdd_Item = QtGui.QPushButton(MKBSubclassEditorDialog)
        self.btnAdd_Item.setObjectName(_fromUtf8("btnAdd_Item"))
        self.hboxlayout1.addWidget(self.btnAdd_Item)
        self.btnEdit_Item = QtGui.QPushButton(MKBSubclassEditorDialog)
        self.btnEdit_Item.setObjectName(_fromUtf8("btnEdit_Item"))
        self.hboxlayout1.addWidget(self.btnEdit_Item)
        self.btnDel_Item = QtGui.QPushButton(MKBSubclassEditorDialog)
        self.btnDel_Item.setEnabled(False)
        self.btnDel_Item.setObjectName(_fromUtf8("btnDel_Item"))
        self.hboxlayout1.addWidget(self.btnDel_Item)
        self.vboxlayout1.addLayout(self.hboxlayout1)
        self.gridlayout.addLayout(self.vboxlayout1, 0, 1, 1, 1)
        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setSpacing(4)
        self.hboxlayout2.setObjectName(_fromUtf8("hboxlayout2"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem2)
        self.btnClose = QtGui.QPushButton(MKBSubclassEditorDialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout2.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout2, 1, 0, 1, 2)

        self.retranslateUi(MKBSubclassEditorDialog)
        QtCore.QMetaObject.connectSlotsByName(MKBSubclassEditorDialog)

    def retranslateUi(self, MKBSubclassEditorDialog):
        MKBSubclassEditorDialog.setWindowTitle(QtGui.QApplication.translate("MKBSubclassEditorDialog", "Субклассификация по пятому знаку", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MKBSubclassEditorDialog", "Субклассификация по пятому знаку", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("MKBSubclassEditorDialog", "добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEdit.setText(QtGui.QApplication.translate("MKBSubclassEditorDialog", "изменить", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDel.setText(QtGui.QApplication.translate("MKBSubclassEditorDialog", "удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MKBSubclassEditorDialog", "элемент субклассификации по 5 знаку", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd_Item.setText(QtGui.QApplication.translate("MKBSubclassEditorDialog", "добавить", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEdit_Item.setText(QtGui.QApplication.translate("MKBSubclassEditorDialog", "изменить", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDel_Item.setText(QtGui.QApplication.translate("MKBSubclassEditorDialog", "удалить", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("MKBSubclassEditorDialog", "закрыть", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MKBSubclassEditorDialog = QtGui.QDialog()
    ui = Ui_MKBSubclassEditorDialog()
    ui.setupUi(MKBSubclassEditorDialog)
    MKBSubclassEditorDialog.show()
    sys.exit(app.exec_())

