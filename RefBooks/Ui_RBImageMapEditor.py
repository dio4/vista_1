# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBImageMapEditor.ui'
#
# Created: Fri Jun 15 12:16:35 2012
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
        ItemEditorDialog.resize(497, 599)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 2)
        self.lblName = QtGui.QLabel(ItemEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 2)
        self.lblImage = QtGui.QLabel(ItemEditorDialog)
        self.lblImage.setObjectName(_fromUtf8("lblImage"))
        self.gridLayout.addWidget(self.lblImage, 2, 0, 1, 1)
        self.edtImage = QtGui.QLineEdit(ItemEditorDialog)
        self.edtImage.setReadOnly(True)
        self.edtImage.setObjectName(_fromUtf8("edtImage"))
        self.gridLayout.addWidget(self.edtImage, 2, 1, 1, 1)
        self.btnOpen = QtGui.QPushButton(ItemEditorDialog)
        self.btnOpen.setObjectName(_fromUtf8("btnOpen"))
        self.gridLayout.addWidget(self.btnOpen, 2, 2, 1, 1)
        self.lblMarkSize = QtGui.QLabel(ItemEditorDialog)
        self.lblMarkSize.setObjectName(_fromUtf8("lblMarkSize"))
        self.gridLayout.addWidget(self.lblMarkSize, 3, 0, 1, 1)
        self.edtMarkSize = QtGui.QSpinBox(ItemEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMarkSize.sizePolicy().hasHeightForWidth())
        self.edtMarkSize.setSizePolicy(sizePolicy)
        self.edtMarkSize.setMinimum(1)
        self.edtMarkSize.setMaximum(10)
        self.edtMarkSize.setObjectName(_fromUtf8("edtMarkSize"))
        self.gridLayout.addWidget(self.edtMarkSize, 3, 1, 1, 1)
        self.scrollAreaPixmap = QtGui.QScrollArea(ItemEditorDialog)
        self.scrollAreaPixmap.setWidgetResizable(True)
        self.scrollAreaPixmap.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignJustify)
        self.scrollAreaPixmap.setObjectName(_fromUtf8("scrollAreaPixmap"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 485, 458))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblPixmap = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblPixmap.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblPixmap.setFrameShadow(QtGui.QFrame.Plain)
        self.lblPixmap.setText(_fromUtf8(""))
        self.lblPixmap.setScaledContents(False)
        self.lblPixmap.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblPixmap.setObjectName(_fromUtf8("lblPixmap"))
        self.gridLayout_2.addWidget(self.lblPixmap, 0, 0, 1, 1)
        self.scrollAreaPixmap.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollAreaPixmap, 4, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 3)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtName)
        ItemEditorDialog.setTabOrder(self.edtName, self.edtImage)
        ItemEditorDialog.setTabOrder(self.edtImage, self.btnOpen)
        ItemEditorDialog.setTabOrder(self.btnOpen, self.edtMarkSize)
        ItemEditorDialog.setTabOrder(self.edtMarkSize, self.scrollAreaPixmap)
        ItemEditorDialog.setTabOrder(self.scrollAreaPixmap, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(QtGui.QApplication.translate("ItemEditorDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ItemEditorDialog", "Наименование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblImage.setText(QtGui.QApplication.translate("ItemEditorDialog", "Изображение", None, QtGui.QApplication.UnicodeUTF8))
        self.edtImage.setWhatsThis(QtGui.QApplication.translate("ItemEditorDialog", "Путь к картинке", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOpen.setText(QtGui.QApplication.translate("ItemEditorDialog", "Открыть", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMarkSize.setText(QtGui.QApplication.translate("ItemEditorDialog", "Размер маркера", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemEditorDialog = QtGui.QDialog()
    ui = Ui_ItemEditorDialog()
    ui.setupUi(ItemEditorDialog)
    ItemEditorDialog.show()
    sys.exit(app.exec_())

